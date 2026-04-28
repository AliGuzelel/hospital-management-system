from app.database.session import Base, engine
from app.main_base import app
from app.models.availability import DoctorAvailability, DoctorTimeOff  # noqa: F401
from app.models.appointment import Appointment  # noqa: F401
from app.models.invoice import Invoice  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.routes.availability_routes import router as availability_router
from app.routes.appointment_routes import router as appointment_router
from app.routes.doctor_appointments_routes import router as doctor_appointments_router
from app.routes.invoice_routes import router as invoice_router
from app.routes.notification_routes import router as notification_router

Base.metadata.create_all(bind=engine)
app.include_router(appointment_router)
app.include_router(notification_router)
app.include_router(doctor_appointments_router)
app.include_router(availability_router)
app.include_router(invoice_router)
