from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends, Form, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security.api_key import APIKeyHeader
from vdiffusionwrapper import VDiffusion
import config
import random
import os
from io import BytesIO
from functools import lru_cache
from pydantic import BaseModel
from PIL import Image

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

async def authenticate_websocket_initial_connection(websocket: WebSocket):
    settings = get_settings()
    if websocket.headers['x-api-key'] == settings.api_key:
        return True
    else:
        return False

app = FastAPI(dependencies=[Depends(get_api_key)])
settings = get_settings()
app.diffusion_model = VDiffusion(num_outputs=settings.num_outputs, clip_guidance_scale=settings.clip_guidance_scale)
app.current_iteration_count = 1
IMAGEDIR = 'files/'


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
def generate_images(data: GenerationData):
    if os.path.isfile(os.path.join(IMAGEDIR, "best_so_far.png")):
        files = app.diffusion_model.build_on(random.randint(0,50), data.iterations, 1, IMAGEDIR, init_image_path=os.path.join(IMAGEDIR, "best_so_far.png"))
    else:
        files = app.diffusion_model.run_all(data.iterations, 0, 1, IMAGEDIR)
    return {"msg": f"Generated new images"}


@app.post("/uploadfile", dependencies=[Depends(get_api_key)])
async def create_upload_file(file: UploadFile = File(...)):
    file.filename = f"best_so_far.png"
    contents = await file.read()
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename}

@app.get("/health", dependencies=[Depends(get_api_key)])
async def health():
    return True

import base64
@app.websocket("/generation_stream")
async def websocket_endpoint(websocket: WebSocket):
    good_key = await authenticate_websocket_initial_connection(websocket)
    if good_key:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            data = base64.b64decode(data)
            input_buffer = BytesIO(data)
            if app.diffusion_model.clip_embed == None:
                app.diffusion_model.clip_embed = app.diffusion_model.prepare_embeddings(prompts=["Crystal Starship"], images=[])
            else:
                pass
            files = app.diffusion_model.generation_stream(app.current_iteration_count, app.current_iteration_count * 2, 1, IMAGEDIR, init_image_path=input_buffer)
            app.current_iteration_count += 1
            text_to_send = base64.b64encode(files[0].getvalue())
            await websocket.send_text(text_to_send)