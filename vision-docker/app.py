from io import BytesIO, StringIO
from typing import Annotated
from pydantic import BaseModel

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import skimage

import vision
app = FastAPI()

origins = [
  "*"
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*']
)

class XRay(BaseModel):
  file: UploadFile

@app.get('/test')
async def root():
  return {"message": "Hello world!"}

@app.post('/diagnose')
async def diagnose_xray(file: UploadFile):

  file_content = await file.read()
  file_name = str(file.filename)
  file_bytes = BytesIO(file_content)

  img = skimage.io.imread(file_bytes)
  return {
    'conditions': vision.diagnose(img),
    }

@app.post('/heart')
async def heart(file: UploadFile):

  file_content = await file.read()
  file_name = str(file.filename)
  file_bytes = BytesIO(file_content)

  img = skimage.io.imread(file_bytes)
  return FileResponse(vision.segment(img))