from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security.api_key import APIKeyHeader
from vdiffusionwrapper import VDiffusion
import config
import uuid
import os
from functools import lru_cache
from pydantic import BaseModel
api_key_header_auth = APIKeyHeader(name='x-api-key')

@lru_cache()
def get_settings():
    return config.Settings()

async def get_api_key(api_key_header: str = Security(api_key_header_auth), settings: config.Settings = Depends(get_settings)):
    if api_key_header != settings.api_key:
        raise HTTPException(
            status_code= 401,
            detail="Invalid API Key",
        )
    else:
        return api_key_header

app = FastAPI(dependencies=[Depends(get_api_key)])
settings = get_settings()
app.diffusion_model = VDiffusion(num_outputs=settings.num_outputs, clip_guidance_scale=settings.clip_guidance_scale)

IMAGEDIR = 'files/'


@app.get("/listfiles/")
async def list_files():
    files = os.listdir(IMAGEDIR)
    return JSONResponse(content=files)


@app.get("/files/{file_id}")
async def get_item(file_id: str):
    if f"{file_id}.png" in os.listdir(IMAGEDIR):
        return FileResponse(path=os.path.join(IMAGEDIR, f"{file_id}.png"))
    else:
        raise HTTPException(
            status_code=404,
            detail="File Not Found"
        )


class PromptData(BaseModel):
    prompt: str

@app.post("/generate_embeddings")
def generate_model_from_prompt(data: PromptData):
    prompt = data.prompt
    app.diffusion_model.clip_embed = app.diffusion_model.prepare_embeddings(prompts=[prompt], images=[])
    if app.diffusion_model.clip_embed !=None:
        return {"msg": f"Generated embeddings for {prompt}"}
    else:
        return {"msg": f"Failed to generate embeddings for {prompt}"}

class GenerationData(BaseModel):
    iterations: int
    start_from_best: bool

@app.post("/generate_images")
async def generate_images(data: GenerationData):
    if os.path.isfile(os.path.join(IMAGEDIR, "best_so_far.png")):
        files = app.diffusion_model.run_all(data.iterations, 0.9, 1, IMAGEDIR, init_image_path=os.path.join(IMAGEDIR, "best_so_far.png"))
    else:
        files = app.diffusion_model.run_all(data.iterations, 0, 1, IMAGEDIR)
    return JSONResponse(content = files)


@app.post("/uploadfile", dependencies=[Depends(get_api_key)])
async def create_upload_file(file: UploadFile = File(...)):
    file.filename = f"best_so_far.png"
    contents = await file.read()
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename}