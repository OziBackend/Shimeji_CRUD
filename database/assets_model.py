from pydantic import BaseModel, Field, field_serializer
from typing import Optional
from datetime import datetime
from bson import ObjectId

# Analytics Models
class Category(BaseModel):
    name: str = Field(..., description="Category name")
    is_enabled: bool = Field(default=False, description="Category is enabled")
    is_premium: bool = Field(default=False, description="Category is premium")
    sequence: int = Field(default=0, description="Category sequence")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

class Asset(BaseModel):
    category_id: str = Field(..., description="Category ID")
    name: str = Field(..., description="Asset name")
    description: Optional[str] = Field(None, description="Asset description")
    image_url: str = Field(..., description="Asset image URL")
    thumbnail_url: str = Field(..., description="Asset thumbnail URL")
    is_enabled: bool = Field(default=False, description="Asset is enabled")
    is_premium: bool = Field(default=False, description="Asset is premium")
    sequence: int = Field(default=0, description="Asset sequence")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

