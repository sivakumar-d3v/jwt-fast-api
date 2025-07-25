from app.controllers.user import router as user_router
from app.controllers.login import router as auth_router

def include_routers(app):
    app.include_router(
        auth_router, prefix = "/auth", tags = ['login']
    )

    app.include_router(
        user_router, prefix ="/api/users", tags = ['User']
    )