from app.main_base import app
from app.routes.gateway_routes import router
app.include_router(router)
