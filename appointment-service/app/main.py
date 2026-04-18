from app.database.session import Base, engine
from app.main_base import app
from app.routes.appointment_routes import router
Base.metadata.create_all(bind=engine)
app.include_router(router)
