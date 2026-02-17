from fastapi import APIRouter, Request, UploadFile, File, Form

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
    images: list[UploadFile] = File(...),
):
    if categories is None and images is None:
        raise HTTPException(
            status_code=500,
            detail=f"Enter at least one field"
        )

    result = await controller.add_categories(categories, images)
    return result