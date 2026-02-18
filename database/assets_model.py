from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime
from bson import ObjectId
from typing import Dict, Any

# Analytics Models
class Category(BaseModel):
    name: str = Field(..., description="Category name")
    is_enabled: bool = Field(default=False, description="Category is enabled")
    is_premium: bool = Field(default=False, description="Category is premium")
    sequence: int = Field(default=0, description="Category sequence")
    image_url: str = Field(default=None, description="Category image URL")
    thumbnail_url: str = Field(default=None, description="Category thumbnail URL")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class Asset(BaseModel):
    category_id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Asset name")
    description: Optional[str] = Field(None, description="Asset description")
    image_url: Optional[str] = Field(default=None, description="Asset image URL")
    thumbnail_url: Optional[str] = Field(default=None, description="Asset thumbnail URL")
    is_enabled: bool = Field(default=False, description="Asset is enabled")
    is_premium: bool = Field(default=False, description="Asset is premium")
    sequence: int = Field(default=0, description="Asset sequence")
    views: int = Field(default=0, description="Asset views")
    downloads: int = Field(default=0, description="Asset downloads")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    moreFields: Dict[str, Any] = Field(
        default_factory=lambda: {
            "actionFile": None,
            "behaviorFile": None,
            "assets": []
        }
    )
