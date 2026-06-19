from fastapi import FastAPI, APIRouter, Depends
import os
from helpers.config import get_settings, Settings

# base router
base_router = APIRouter(
    prefix = "/api/v1",
    tags = ["api-v1"],
    )

# routes
## default route
## returns an app's name and version
@base_router.get("/")
async def welcome(app_settings:Settings = Depends(get_settings)):   # create app_settings object
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    return {
        "app_name": app_name,
        "app_version": app_version
    }
