from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .study_sets import router as study_sets_router

# Create main v1 router
router = APIRouter()

# Include all routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(study_sets_router, prefix="/study-sets", tags=["study-sets"]) 