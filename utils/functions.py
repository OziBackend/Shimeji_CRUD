import os
from environment import config
from fastapi import HTTPException

def create_target_Assets_folders(name):
    os.makedirs(os.path.join(config.SHIMEJI_ASSETS_ORIGINAL_DIR, name.replace(" ","_").lower()), exist_ok=True)
    os.makedirs(os.path.join(config.SHIMEJI_ASSETS_THUMBNAIL_DIR, name.replace(" ","_").lower()), exist_ok=True)



async def save_images_by_folder(
    folder_path,
    images
):
    try:
        for image in images:
            image_name = image.filename
            image_path = os.path.join(folder_path, image_name)
            with open(image_path, "wb") as f:
                f.write(await image.read())
        return {
            "message": f"{len(images)} images saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save images: {e}"
        )