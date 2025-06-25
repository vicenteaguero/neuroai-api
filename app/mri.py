from fastapi import UploadFile

import hashlib, os
from app.utils import extract_modalities, array_to_base64, save_numpy_image

def save_user_file(username,surname,file:UploadFile):
    if not file.filename.endswith(".nii.gz"):
        raise ValueError("Only .nii.gz files are supported")
    user_hash = hashlib.sha256(username.encode()).hexdigest()[:8]
    folder_path = f"uploads/{user_hash}_{surname}"
    os.makedirs(folder_path,exist_ok=True)
    file_path = os.path.join(folder_path,file.filename)
    with open(file_path,"wb") as f:
        f.write(file.file.read())
    return file_path, folder_path
def process_and_save_modalities(file_path:str,folder_path:str):
    data = extract_modalities(file_path)
    base64_images = {}
    for modality,arr in data.items():
        if modality == "shape":
            continue
    
        save_numpy_image(arr,os.path.join(folder_path,f"{modality}.png"))
        base64_images[modality] = array_to_base64(arr)
    base64_images["shape"] = data["shape"]
    return base64_images