import os
from bson import ObjectId
from datetime import datetime

from utils.preprocess_image import create_thumbnail

#loading database functions
from database.database_config import get_assets_db
from database.assets_model import Category, Asset

from utils.functions import create_target_Assets_folders, save_files_by_folder,save_single_file_by_folder

from environment import config

from fastapi import HTTPException

CREATE_THUMBNAILS = False

async def add_categories(
    categories, 
    images, 
    has_images
):
    try:
        db = get_assets_db()
        collection = db[config.CATEGORIES_COLLECTION_NAME]
        
        if has_images:
            # Images Recieved
            print("Images Recieved")
            await save_files_by_folder(config.SHIMEJI_CATEGORIES_ORIGINAL_DIR, images)
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
        # 1. Fetch the data sorted by name
        categories = await collection.find({},projection).sort("name", 1).to_list(length=None)
        
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


async def add_assets(
    categoryId, 
    categoryName, 
    characterName,
    images, 
    thumbnail,
    actionFile,
    behaviorFile
):
    try:
        print("In Assets Function")
        db = get_assets_db()
        collection = db[config.ASSETS_COLLECTION_NAME]

        image_url = None
        thumbnail_url = None
        file_url = None

        # Category Folder to store assets and files
        character_folder = f"{config.SHIMEJI_ASSETS_ORIGINAL_DIR}/{categoryName.replace(" ","_").lower()}/{characterName}"
        os.makedirs(character_folder, exist_ok=True)
        # thumbnails folder
        thumbnails_folder = f"{config.SHIMEJI_ASSETS_THUMBNAIL_DIR}/{categoryName.replace(" ","_").lower()}/{characterName}"
        os.makedirs(thumbnails_folder, exist_ok=True)

        file_url = f"{config.IMAGE_URL_PREFIX}/{character_folder}"
        thumbnail_url = f"{config.IMAGE_URL_PREFIX}/{thumbnails_folder}/{thumbnail.filename}"

        # saving files and images
        await save_files_by_folder(character_folder, images)
        await save_single_file_by_folder(character_folder, actionFile)
        await save_single_file_by_folder(character_folder, behaviorFile)
        # save thumbnail 
        await save_single_file_by_folder(thumbnails_folder, thumbnail)

        assets = []
        for image in images:
            assets.append({
                "name": image.filename.rsplit(".", 1)[0],
                "url": f"{file_url}/{image.filename}"
            })

        asset_model = Asset(
            category_id = categoryId,
            name= characterName,
            image_url= image_url,
            thumbnail_url= thumbnail_url,
            moreFields = {
                "actionFile": f"{file_url}/{actionFile.filename}",
                "behaviorFile": f"{file_url}/{behaviorFile.filename}",
                "assets" : assets
            }
        )

        await collection.insert_one(asset_model.model_dump())

        return {
            "message": "Asset Saved"
        }
    except Exception as e:
        print("ERROR: ", e)
        raise HTTPException(
            status_code=500,
            detail= f"Failed to save asset: {e}"
        )


async def get_assets(
    category_id
):
    try:
        db = get_assets_db()
        collection = db[config.ASSETS_COLLECTION_NAME]

        condition = {}
        projection = {
            "_id":1,
            "name": 1,
            "thumbnail_url": 1,
            "is_premium": 1,
            "moreFields": 1
        }
        if category_id:
            condition["category_id"] = category_id

        assets = await collection.find(condition, projection).to_list(length=None)

        for asset in assets:
            asset["_id"] = str(asset["_id"])
        
        return {
            "assets": assets,
            "message": f"{len(assets)} assets retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve assets: {e}"
        )

async def updateAsset(frame_id, requiredFunction):
    try:
        db = get_assets_db()
        collection = db[config.ASSETS_COLLECTION_NAME]

        condition = {}
        if frame_id:
            condition["_id"] = ObjectId(frame_id)

        updateSet = {}
        message = ""
        if requiredFunction == "view":
            updateSet = {"$inc" : {"views": 1}}
            message = "View Increased"
        elif requiredFunction == "enable":
            updateSet = {"$set" : {"is_enabled": True}}
            message = "Asset Enabled"
        elif requiredFunction == "disable":
            updateSet = {"$set" : {"is_enabled": False}}
            message = "Asset Disabled"
        elif requiredFunction == "premium":
            updateSet = {"$set" : {"is_premium": True}}
            message = "Asset Made Premium"
        elif requiredFunction == "notPremium":
            updateSet = {"$set" : {"is_premium": False}}
            message = "Asset Removed Premium"
        else:
            raise ValueError("No function defined / Wrong function name")

        result = await collection.update_one(condition, updateSet)

        if result.matched_count == 0:
            return {"error": "Asset not found"}
        
        return {"message": message}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update asset view: {e}"
        )

async def addValueInMoreFields(
    request,
    asset_id
):
    try:
        db = get_assets_db()
        collection = db[config.ASSETS_COLLECTION_NAME]

        # Get the key-value pairs from request body
        try:
            body = await request.json()
        except Exception as json_error:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON in request body: {json_error}"
            )
        
        if not body or not isinstance(body, dict):
            raise HTTPException(
                status_code=400,
                detail="Request body must contain key-value pairs"
            )

        # Build the update query to add/update fields in moreFields
        update_fields = {}
        for key, value in body.items():
            update_fields[f"moreFields.{key}"] = value

        # Update the asset
        result = await collection.update_one(
            {"_id": ObjectId(asset_id)},
            {
                "$set": update_fields,
                "$currentDate": {"updated_at": True}
            }
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Asset not found"
            )

        return {
            "message": f"Successfully added/updated {len(body)} field(s) in moreFields",
            "updated_fields": list(body.keys())
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update moreFields: {e}"
        )

async def update_thumbnail(asset_id, thumbnail):
    try:
        db = get_assets_db()
        collection = db[config.ASSETS_COLLECTION_NAME]

        # Validate that the file is a GIF
        if not thumbnail.filename.lower().endswith('.gif'):
            raise HTTPException(
                status_code=400,
                detail="Thumbnail must be a .gif file"
            )

        # Get the asset to find its category and name
        asset = await collection.find_one({"_id": ObjectId(asset_id)})
        
        if not asset:
            raise HTTPException(
                status_code=404,
                detail="Asset not found"
            )

        # Extract category and asset name from existing thumbnail_url or use asset name
        category_name = asset.get("name", "unknown").replace(" ", "_").lower()
        
        # Create thumbnail directory path
        thumbnails_folder = f"{config.SHIMEJI_ASSETS_THUMBNAIL_DIR}/{category_name}"
        os.makedirs(thumbnails_folder, exist_ok=True)

        # Save the new thumbnail
        await save_single_file_by_folder(thumbnails_folder, thumbnail)
        
        # Generate the new thumbnail URL
        thumbnail_url = f"{config.IMAGE_URL_PREFIX}/{thumbnails_folder}/{thumbnail.filename}"

        # Update the asset with new thumbnail URL
        result = await collection.update_one(
            {"_id": ObjectId(asset_id)},
            {
                "$set": {
                    "thumbnail_url": thumbnail_url,
                    "updated_at": datetime.utcnow()
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail="Asset not found"
            )

        return {
            "message": "Thumbnail updated successfully",
            "thumbnail_url": thumbnail_url,
            "file_type": "gif"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update thumbnail: {e}"
        )