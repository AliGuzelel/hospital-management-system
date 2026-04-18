from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from prometheus_fastapi_instrumentator import Instrumentator
from app.config.settings import settings

app = FastAPI(
    title="API Gateway",
    openapi_version="3.0.2",
    docs_url=None,
    redoc_url="/redoc",
)

@app.get("/docs", include_in_schema=False)
def swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        swagger_js_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/")
def root():
    return {"service": settings.service_name, "status": "running"}

@app.get("/health")
def health():
    return {"status": "UP", "service": settings.service_name}

Instrumentator().instrument(app).expose(app)
