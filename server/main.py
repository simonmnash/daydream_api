from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security.api_key import APIKeyHeader
from vdiffusionwrapper import VDiffusion
import uuid
import os
from pydantic import BaseModel

API_KEY = "BABABBABABBALLLALLLEER"
API_KEY_NAME = "x-api-key"

V_DIFFUSION_MODEL = VDiffusion(num_outputs=1, clip_guidance_scale=0)
api_key_header_auth = APIKeyHeader(name=API_KEY_NAME)

async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code= 401,
            detail="Invalid API Key",
        )
    else:
        return api_key_header

app = FastAPI(dependencies=[Depends(get_api_key)])
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
    V_DIFFUSION_MODEL.clip_embed = V_DIFFUSION_MODEL.prepare_embeddings(prompts=[prompt], images=[])
    if V_DIFFUSION_MODEL.clip_embed !=None:
        return {"msg": f"Generated embeddings for {prompt}"}
    else:
        return {"msg": f"Failed to generate embeddings for {prompt}"}

class GenerationData(BaseModel):
    iterations: int
    start_from_best: bool

@app.post("/generate_images")
async def generate_images(data: GenerationData):
    files = V_DIFFUSION_MODEL.run_all(data.iterations, 0, 1, IMAGEDIR)
    return JSONResponse(content = files)


@app.post("/uploadfile", dependencies=[Depends(get_api_key)])
async def create_upload_file(file: UploadFile = File(...)):
    file.filename = f"best_so_far.png"
    contents = await file.read()
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename}