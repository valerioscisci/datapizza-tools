from .router import router
from .messages.router import router as messages_router

router.include_router(messages_router)
