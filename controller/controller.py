from utils.preprocess_image import create_thumbnail
from utils.postprocess_image import save_img_with_url

#loading database functions
from database.database_config import get_assets_db
from database.assets_model import Category, Asset

from utils.functions import create_target_Assets_folders

from environment import config

async def add_categories(categories, images):
    try:
        db = get_assets_db()
        collection = db[config.ASSETS_COLLECTION_NAME]
        
        if(images):
            for image in images:
                filename = image.filename
                category_name = filename.split(".")[0]
                filepath = os.path.join(config.SHIMEJI_CATEGORIES_ORIGNAL_DIR, filename)
                thumbnailpath = os.path.join(config.SHIMEJI_CATEGORIES_THUMBNAIL_DIR, filename)

                # get image url by saving image
                image_url = save_img_with_url(image.file, filepath, filepath)
                #create thumbnail and make url
                create_thumbnail(filepath, thumbnailpath)
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
            for category in categories:
                category_model = Category(name=category)

                #create categories name folders
                create_target_Assets_folders(category_model)

                await collection.insert_one(category_model.model_dump())
            return {
                "message": f"{len(categories)} Categories Created"
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add categories: {e}"
        )
    
        