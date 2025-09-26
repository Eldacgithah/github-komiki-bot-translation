from fastapi import FastAPI
from app.webhook.api import router as handlers_router

import uvicorn


def диспетчер():
    app = FastAPI()
    app.include_router(router=handlers_router, prefix="/webhook")

    @app.get("/")
    async def корень():
        return {
            "message": "Привет мир",
        }

    uvicorn.run(app, host="0.0.0.0", port=4454)
