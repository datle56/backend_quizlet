from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .study_sets import router as study_sets_router
from .study import router as study_router
from .social import router as social_router
from .classes import router as classes_router

# Create main v1 router
router = APIRouter()

# Include all routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(study_sets_router, prefix="/study-sets", tags=["study-sets"])
router.include_router(study_router, prefix="/study", tags=["study"])
router.include_router(social_router, prefix="/social", tags=["social"])
router.include_router(classes_router, prefix="/classes", tags=["classes"]) 