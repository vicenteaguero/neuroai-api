import numpy as np
import nibabel as nib
from PIL import Image
import base64
import io


def extract_modalities(file_path:str,slice_id:int = 80):
    img = nib.load(file_path)
    data = img.get_fdata()
    if data.ndim != 4 or data.shape[-1] != 4:
        raise ValueError("Expected image shape: (H, W, Slices, 4 modalities)")
    return {
        "t1": data[:,:,slice_id,0],
        "t1_gd": data[:,:,slice_id,1],
        "t2": data[:,:,slice_id,2],
        "t2_flair":data[:,:,slice_id,3],
        "shape": data.shape,
    }
    
def array_to_base64(array: np.ndarray) -> str:
    array = np.nan_to_num(array) 
    if np.max(array) == np.min(array):
        norm_array = np.zeros_like(array, dtype=np.uint8)
    else:
        norm_array = (255 * (array - np.min(array)) / (np.max(array) - np.min(array))).astype(np.uint8)
    image = Image.fromarray(norm_array)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
def save_numpy_image(array: np.ndarray, path: str):
    # Normalize array to 0-255 and convert to uint8
    print(array.dtype, array.shape, np.min(array), np.max(array))
    array = np.nan_to_num(array)  # Replace NaNs with 0

    if np.max(array) == np.min(array):
        norm_array = np.zeros_like(array, dtype=np.uint8)
    else:
        norm_array = (255 * (array - np.min(array)) / (np.max(array) - np.min(array))).astype(np.uint8)

    image = Image.fromarray(norm_array)
    image.convert("L").save(path)