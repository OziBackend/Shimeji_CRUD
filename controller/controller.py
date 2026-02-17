import os

from utils.preprocess_image import create_thumbnail

#loading database functions
from database.database_config import get_assets_db
from database.assets_model import Category, Asset

from utils.functions import create_target_Assets_folders, save_images_by_folder

from environment import config

from fastapi import HTTPException

async def add_categories(categories, images, has_images):
    try:
        db = get_assets_db()
        collection = db[config.CATEGORIES_COLLECTION_NAME]
        
        if has_images:
            # Images Recieved
            print("Images Recieved")
            await save_images_by_folder(config.SHIMEJI_CATEGORIES_ORIGINAL_DIR, images)
            for image in images:
                filename = image.filename
                category_name = filename.split(".")[0]
                filepath = os.path.join(config.SHIMEJI_CATEGORIES_ORIGINAL_DIR, filename)
                thumbnailpath = os.path.join(config.SHIMEJI_CATEGORIES_THUMBNAIL_DIR, filename)

                #create thumbnail and make url
                create_thumbnail(filepath, thumbnailpath)
                image_url = f"{config.IMAGE_URL_PREFIX}/{filepath}"
                thumbnail_url = f"{config.IMAGE_URL_PREFIX}/{thumbnailpath}"

                #create folder for assets
                create_target_Assets_folders(category_name)
                
                category_model = Category(
                    name= category_name,
                    image_url= image_url,
                    thumbnail_url= thumbnail_url
                )

                await collection.insert_one(category_model.model_dump())
            return {
                "message": f"{len(images)} Categories Created using images"
            }
        else:
            # Categories Recieved
            print("Categories Recieved")
            for category in categories:
                category_model = Category(name=category)

                #create categories name folders
                create_target_Assets_folders(category)

                await collection.insert_one(category_model.model_dump())
            return {
                "message": f"{len(categories)} Categories Created"
            }

    except Exception as e:
        print(e)
        raise HTTPException (
            status_code=500,
            detail=f"Failed to add categories: {e}"
        )
    
async def get_all_categories(
):
    try:
        db = get_assets_db()
        collection = db[config.CATEGORIES_COLLECTION_NAME]
        projection = {
            "_id":1,
            "name": 1,
            "is_premium": 1
        }
        # 1. Fetch the data
        categories = await collection.find({},projection).to_list(length=None)
        
        # 2. Convert ObjectId to string for every document
        for category in categories:
            category["_id"] = str(category["_id"])
        return {
            "categories": categories,
            "message": f"{len(categories)} categories fetched successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch categories: {e}"
        )