from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi import HTTPException

from controller import controller

router = APIRouter(prefix="/api/shimeji", tags=["shimeji"])

@router.get("/", response_model=dict)
async def read_root():
    return {
        "message": "Shimeji API is running"
    }

@router.post("/add_categories", response_model=dict)
async def add_categories(
    request: Request,
    categories: list[str],
    images: list[UploadFile],
):
    print(categories)
    print(images)
    # 1. Normalize categories if they come in as an empty list/None
    has_categories = categories and len(categories) > 0
    
    # 2. Check if images were actually uploaded
    # We check for: list is not None, list is not empty, and filename is not empty
    has_images = images and len(images) > 0 and images[0].filename != ""

    if not has_categories and not has_images:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Enter at least one field: categories or images"}
        )

    result = await controller.add_categories(categories, images, has_images)
    return result

@router.get("/get_categories", response_model=dict)
async def get_categories():

    result = await controller.get_all_categories()
    return result

@router.post("/add_assets", response_model=dict)
async def add_assets(
    request: Request,
    categoryId: str = Form(...),
    categoryName: str = Form(...),
    characterName: str = Form(...),
    images: list[UploadFile] = File(...),
    thumbnail: UploadFile = File(...),
    actionFile: UploadFile = File(...),
    behaviorFile: UploadFile = File(...)
):
    has_images = images and len(images) > 0 and images[0].filename != ""

    if not has_images or not actionFile or not behaviorFile or not characterName or not thumbnail:
        return JSONResponse(
            status_code=400, # 400 is better for "User Error/Bad Request"
            content={"status": "error", "message": "Missing Body Params"}
        )
    result = await controller.add_assets(
        categoryId, 
        categoryName, 
        characterName,
        images, 
        thumbnail, 
        actionFile, 
        behaviorFile)

    return result

@router.get("/get_assets", response_model=dict)
async def get_assets(
    request: Request
):
    category_id = request.query_params.get("category_id")
    
    # Get assets from database
    result = await controller.get_assets(category_id)
    return result

@router.put("/updateAsset", response_model=dict)
async def updateAsset(
    request: Request
):
    frame_id = request.query_params.get("frame_id")
    requiredFunction = request.query_params.get("requiredFunction")

    if not frame_id:
        raise HTTPException(
            status_code=400,
            detail="Frame ID is missing"
        )
    if not requiredFunction:
        raise HTTPException(
            status_code=400,
            detail="requiredFunction is missing"
        )

    result = await controller.updateAsset(frame_id, requiredFunction)
    return result