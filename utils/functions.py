import os
from environment import config

def create_target_Assets_folders(name):
    os.makedirs(os.path.join(config.SHIMEJI_ASSETS_ORIGINAL_DIR, name.replace(" ","_").lower()), exist_ok=True)
    os.makedirs(os.path.join(config.SHIMEJI_ASSETS_THUMBNAIL_DIR, name.replace(" ","_").lower()), exist_ok=True)