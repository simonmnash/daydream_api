from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends, WebSocket
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security.api_key import APIKeyHeader
from vdiffusionwrapper import VDiffusion
import config
from io import BytesIO
from functools import lru_cache
from pydantic import BaseModel
import base64

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
app.start = 0
app.end = 5 
IMAGEDIR = 'files/'


class PromptData(BaseModel):
    prompt: str
    start: int
    end: int

@app.post("/generate_embeddings")
def generate_model_from_prompt(data: PromptData):
    prompt = data.prompt
    app.diffusion_model.clip_embed = app.diffusion_model.prepare_embeddings(prompts=[prompt], images=[])
    app.start = data.start
    app.end = data.end
    if app.diffusion_model.clip_embed !=None:
        print("Generated Embeddings")
        return {"msg": f"Generated embeddings for {prompt}"}
    else:
        return {"msg": f"Failed to generate embeddings for {prompt}"}

@app.post("/refreshimage", dependencies=[Depends(get_api_key)])
async def refresh_upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    input_buffer = BytesIO(contents)
    files = app.diffusion_model.generation_stream(app.start, app.end, 1, IMAGEDIR, init_image_path=input_buffer)
    app.current_iteration_count += 1
    text_to_send = base64.b64encode(files[0].getvalue())
    return PlainTextResponse(text_to_send)

app.mount("/", StaticFiles(directory="static",html = True), name="static")