from .router import router
from .experiences.router import router as experiences_router
from .educations.router import router as educations_router
from .ai_readiness.router import router as ai_readiness_router

router.include_router(experiences_router)
router.include_router(educations_router)
router.include_router(ai_readiness_router)
