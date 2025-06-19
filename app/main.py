from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import nibabel as nib
import io
import os
import tempfile
from PIL import Image
import base64





app = FastAPI(title="NeuroAI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

def extract_modalities(file_path:str,slice_id:int = 80):
    img = nib.load(file_path).get_fdata()
    if img.ndim != 4 or img.shape[-1] != 4:
        raise ValueError("Expected image shape: (H, W, Slices, 4 modalities)")
    t1 = img[:, :, slice_id, 0]
    t1_gd = img[:, :, slice_id, 1]
    t2 = img[:, :, slice_id, 2]
    t2_flair = img[:, :, slice_id, 3]

    return {
        "t1": t1,
        "t1_gd": t1_gd,
        "t2": t2,
        "t2_flair": t2_flair,
        "shape": img.shape
    
    }

def array_to_base64(array:np.ndarray) -> str:
    arr = (255 * (array - np.min(array)) / (np.max(array) - np.min(array))).astype(np.uint8)
    image = Image.fromarray(arr)
    buffered = io.BytesIO()
    image.save(buffered,format = "PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


    


@app.post("/upload-mri/")
async def upload_mri(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".nii.gz") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name
        
    try:
        data = extract_modalities(tmp_path)
        t1 = data["t1"]
        base64_t1_img = array_to_base64(t1)
        base64_t1_gd_img = array_to_base64(data["t1_gd"])
        base64_t2_img = array_to_base64(data["t2"])
        base64_t2_flair_img = array_to_base64(data["t2_flair"])
        return JSONResponse({
            "message": "MRI modalities extracted successfully",
            "image_t1": base64_t1_img,
            "image_gd": base64_t1_gd_img,
            "image_t2": base64_t2_img,
            "image_t2_flair": base64_t2_flair_img,
            "shape": data["shape"]
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    finally:
        os.remove(tmp_path)

