from fastapi import FastAPI, File, UploadFile, HTTPException, Security, Depends
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.security.api_key import APIKeyHeader
import uuid
import os


API_KEY = "Set your own darn api key :)"
API_KEY_NAME = "x-api-key"

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
    print(file_id)
    if f"{file_id}.png" in os.listdir(IMAGEDIR):
        return FileResponse(path=os.path.join(IMAGEDIR, f"{file_id}.png"))
    else:
        raise HTTPException(
            status_code=404,
            detail="File Not Found"
        )

@app.post("/uploadfile/", dependencies=[Depends(get_api_key)])
async def create_upload_file(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.png"
    contents = await file.read()
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)
    return {"filename": file.filename}


@app.get("/")
async def main():
    content = """
    <body>
    <form action="/uploadfile/" enctype="multipart/form-data" method="post">
    <input name='Text" type='text'>
    <input name="file" type="file">
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)