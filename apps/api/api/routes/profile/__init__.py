from .router import router
from .experiences.router import router as experiences_router
from .educations.router import router as educations_router

router.include_router(experiences_router)
router.include_router(educations_router)
