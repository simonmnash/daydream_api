from vdiffusionpytorch.diffusion import get_model, get_models, sampling, utils
from vdiffusionpytorch.CLIP import clip
from torchvision import transforms
from functools import partial
from pathlib import Path

from PIL import Image
from torch import nn
from torch.nn import functional as F
from torchvision.transforms import functional as TF
from tqdm import trange
import torch
import os

DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
NORMALIZE = transforms.Normalize(mean=[0.48145466, 0.4578275, 0.40821073],
                                     std=[0.26862954, 0.26130258, 0.27577711])
MODULE_DIR = Path(__file__).resolve().parent


class MakeCutouts(nn.Module):
    def __init__(self, cut_size, cutn, cut_pow=1):
        super().__init__()
        self.cut_size = cut_size
        self.cutn = cutn
        self.cut_pow = cut_pow

    def forward(self, input):
        sideY, sideX = input.shape[2:4]
        max_size = min(sideX, sideY)
        min_size = min(sideX, sideY, self.cut_size)
        cutouts = []
        for _ in range(self.cutn):
            size = int(torch.rand([])**self.cut_pow * (max_size - min_size) + min_size)
            offsetx = torch.randint(0, sideX - size + 1, ())
            offsety = torch.randint(0, sideY - size + 1, ())
            cutout = input[:, :, offsety:offsety + size, offsetx:offsetx + size]
            cutout = F.adaptive_avg_pool2d(cutout, self.cut_size)
            cutouts.append(cutout)
        return torch.cat(cutouts)


def spherical_dist_loss(x, y):
    x = F.normalize(x, dim=-1)
    y = F.normalize(y, dim=-1)
    return (x - y).norm(dim=-1).div(2).arcsin().pow(2).mul(2)


def parse_prompt(prompt):
    if prompt.startswith('http://') or prompt.startswith('https://'):
        vals = prompt.rsplit(':', 2)
        vals = [vals[0] + ':' + vals[1], *vals[2:]]
    else:
        vals = prompt.rsplit(':', 1)
    vals = vals + ['', '1'][len(vals):]
    return vals[0], float(vals[1])


def resize_and_center_crop(image, size):
    fac = max(size[0] / image.size[0], size[1] / image.size[1])
    image = image.resize((int(fac * image.size[0]), int(fac * image.size[1])), Image.LANCZOS)
    return TF.center_crop(image, size[::-1])

class VDiffusion:
    def __init__(self,
                 num_outputs=1,
                 clip_guidance_scale=500,
                 cutn = 16,
                 cutpow = 1,
                 side_x = 128,
                 side_y = 128,
                 init_image_path = None
                ):
        self.device = DEVICE
        self.cutn = cutn
        self.cutpow = cutpow
        self.normalize = NORMALIZE
        self.model, self.clip_model = self.load_model()
        self.make_cutouts = MakeCutouts(self.clip_model.visual.input_resolution, self.cutn, self.cutpow)
        self.side_x = side_x
        self.side_y = side_y
        self.num_outputs = num_outputs
        self.eta = 1
        self.clip_embed = None
        self.clip_guidance_scale = clip_guidance_scale
        self.init_image = init_image_path

    def load_model(self, MODEL = "cc12m_1"):
        model = get_model(MODEL)()
        checkpoint = MODULE_DIR / f'vdiffusionpytorch/checkpoints/{MODEL}.pth'
        model.load_state_dict(torch.load(checkpoint, map_location='cpu'))
        if self.device.type == 'cuda':
            model = model.half()
        model = model.to(self.device).eval().requires_grad_(False)
        clip_model_name = model.clip_model if hasattr(model, 'clip_model') else 'ViT-B/16'
        clip_model = clip.load(clip_model_name, jit=False, device=self.device)[0]
        clip_model.eval().requires_grad_(False)
        return model, clip_model

    def load_init_image(self, init_image_path):
        init = Image.open(utils.fetch(init_image_path)).convert('RGB')
        init = resize_and_center_crop(init, (self.side_x, self.side_y))
        init = utils.from_pil_image(init).cuda()[None].repeat([self.num_outputs, 1, 1, 1])
        return init

    def prepare_embeddings(self, prompts, images):
        target_embeds, weights = [], []
        for prompt in prompts:
            txt, weight = parse_prompt(prompt)
            target_embeds.append(self.clip_model.encode_text(clip.tokenize(txt).to(self.device)).float())
            weights.append(weight)

        for prompt in images:
            path, weight = parse_prompt(prompt)
            img = Image.open(utils.fetch(path)).convert('RGB')
            img = TF.resize(img, min(self.side_x, self.side_y, *img.size),
                            transforms.InterpolationMode.LANCZOS)
            batch = self.make_cutouts(TF.to_tensor(img)[None].to(self.device))
            embeds = F.normalize(self.clip_model.encode_image(NORMALIZE(batch)).float(), dim=-1)
            target_embeds.append(embeds)
            weights.extend([weight / self.cutn] * self.cutn)
        target_embeds = torch.cat(target_embeds)
        weights = torch.tensor(weights, device=self.device)
        weights /= weights.sum().abs()

        clip_embed = F.normalize(target_embeds.mul(weights[:, None]).sum(0, keepdim=True), dim=-1)
        clip_embed = clip_embed.repeat([self.num_outputs, 1])
        return clip_embed
    
    def cond_fn(self, x, t, pred, clip_embed):
        clip_in = self.normalize(self.make_cutouts((pred + 1) / 2))
        image_embeds = self.clip_model.encode_image(clip_in).view([self.cutn, x.shape[0], -1])
        losses = spherical_dist_loss(image_embeds, clip_embed[None])
        loss = losses.mean(0).sum() * self.clip_guidance_scale
        grad = -torch.autograd.grad(loss, x)[0]
        return grad

    def run(self, x, steps, clip_embed):
        if hasattr(self.model, 'clip_model'):
            extra_args = {'clip_embed': clip_embed}
            cond_fn_ = self.cond_fn
        else:
            extra_args = {}
            cond_fn_ = partial(self.cond_fn)
        if not self.clip_guidance_scale:
            return sampling.sample(self.model, x, steps, self.eta, extra_args)
        return sampling.cond_sample(self.model, x, steps, self.eta, extra_args, cond_fn_)

    def run_all(self, steps, starting_timestamp=0, batch_size=1, output_directory=None):
        if os.path.isdir(output_directory):
            pass
        else:
            os.mkdir(output_directory)
        x = torch.randn([self.num_outputs, 3, self.side_y, self.side_x], device=self.device)
        t = torch.linspace(1, 0, steps + 1, device=self.device)[:-1]
        steps = utils.get_spliced_ddpm_cosine_schedule(t)
        if self.init_image != None:
            steps = steps[steps > starting_timestamp]
            alpha, sigma = utils.t_to_alpha_sigma(steps[0])
            x = self.init_image * alpha + x * sigma
        for i in trange(0, self.num_outputs, batch_size):
            cur_batch_size = min(self.num_outputs - i, batch_size)
            outs = self.run(x[i:i+cur_batch_size], steps, self.clip_embed[i:i+cur_batch_size])
            for j, out in enumerate(outs):
                utils.to_pil_image(out).save(os.path.join(output_directory, f'out_{i + j:05}.png'))
        return os.listdir(output_directory)


if __name__ == '__main__':
    torch.manual_seed(101)
    generator = VDiffusion(num_outputs=4, clip_guidance_scale=20)
    generator.clip_embed = generator.prepare_embeddings(prompts=["Black and White", "Chess"], images=[])
    num_steps = 5
    generator.run_all(num_steps, batch_size=1, output_directory='/home/simon/cow2')

