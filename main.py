import os
from environment import config
from analytics.excluded_paths import EXCLUDE_PATHS
from analytics.middleware import AnalyticsMiddleware
from routes import router as shimeji_router
from analytics.routes import router as analytics_router

#Server Initialization
from inits.server_init import app

#Setup Analytics Router
app.add_middleware(
    AnalyticsMiddleware,
    exclude_paths=EXCLUDE_PATHS
    )

#Add routers
app.include_router(shimeji_router)
app.include_router(analytics_router)

#============================================================================
#Create Assets Folder
os.makedirs(config.SHIMEJI_ASSETS_DIR, exist_ok=True)
#Create Assets/Original Folder
os.makedirs(config.SHIMEJI_ASSETS_ORIGINAL_DIR, exist_ok=True)
#Create Assets/Thumbnail Folder
os.makedirs(config.SHIMEJI_ASSETS_THUMBNAIL_DIR, exist_ok=True)


#Create Categories Folder
os.makedirs(config.SHIMEJI_CATEGORIES_DIR, exist_ok=True)
#Create Categories/Original Folder
os.makedirs(config.SHIMEJI_CATEGORIES_ORIGINAL_DIR, exist_ok=True)
#Create Categories/Thumbnail Folder
os.makedirs(config.SHIMEJI_CATEGORIES_THUMBNAIL_DIR, exist_ok=True)