import os
from environment import config
from fastapi import HTTPException

def create_target_Assets_folders(name):
    os.makedirs(os.path.join(config.SHIMEJI_ASSETS_ORIGINAL_DIR, name.replace(" ","_").lower()), exist_ok=True)
    os.makedirs(os.path.join(config.SHIMEJI_ASSETS_THUMBNAIL_DIR, name.replace(" ","_").lower()), exist_ok=True)



async def save_files_by_folder(
    folder_path,
    files
):
    try:
        for file in files:
            file_name = file.filename
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, "wb") as f:
                f.write(await file.read())
        return {
            "message": f"{len(files)} files saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save files: {e}"
        )

async def save_single_file_by_folder(
    folder_path,
    file
):
    try:
        
        file_name = file.filename
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        return {
            "message": f"File saved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save file: {e}"
        )

