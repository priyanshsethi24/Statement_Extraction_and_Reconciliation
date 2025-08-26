from fastapi import APIRouter
from controllers.dolphin_controller import router as dolphin_controller_router

router = APIRouter()
router.include_router(dolphin_controller_router)
