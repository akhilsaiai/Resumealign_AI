import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

# Add parent directory to sys.path to allow imports from utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import settings
from backend.routes import parser, analyzer, optimizer, exporter, pipeline

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url=None,       # Disable default docs to serve custom styled ones
    redoc_url="/redoc"   # Keep redoc default
)

# Configure CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(parser.router)
app.include_router(analyzer.router)
app.include_router(optimizer.router)
app.include_router(exporter.router)
app.include_router(pipeline.router)

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "online",
        "app": settings.API_TITLE,
        "version": settings.API_VERSION,
        "documentation": "/docs"
    }

@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "parser": "functional",
            "analyzer": "functional",
            "optimizer": "functional",
            "exporter": "functional",
            "pipeline": "functional"
        }
    }

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Renders a custom styled Swagger UI with gold and deep navy theme matching the ResumeAlign AI brand.
    """
    swagger_response = get_swagger_ui_html(
        openapi_url=app.openapi_url or "/openapi.json",
        title=f"{settings.API_TITLE} - Swagger UI",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )
    
    html_content = swagger_response.body.decode("utf-8")
    
    custom_css = """
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Outfit:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Outfit', sans-serif !important;
        }
        .swagger-ui .topbar {
            background-color: #0d1b4b !important;
            border-bottom: 3px solid #c9a96e !important;
            padding: 10px 0 !important;
        }
        .swagger-ui .topbar .link img {
            display: none !important;
        }
        .swagger-ui .topbar .link span {
            color: #ffffff !important;
            font-family: 'Playfair Display', serif !important;
            font-weight: 700 !important;
            font-size: 1.4rem !important;
            letter-spacing: -0.01em !important;
        }
        .swagger-ui .topbar .link span::after {
            content: " AI";
            color: #c9a96e !important;
        }
        .swagger-ui .info .title {
            color: #0d1b4b !important;
            font-family: 'Playfair Display', serif !important;
            border-left: 5px solid #c9a96e !important;
            padding-left: 15px !important;
        }
        .swagger-ui .btn.authorize {
            background-color: #c9a96e !important;
            color: white !important;
            border-color: #c9a96e !important;
            border-radius: 6px !important;
        }
        .swagger-ui .btn.authorize svg {
            fill: white !important;
        }
        .swagger-ui .opblock.opblock-post {
            border-color: rgba(201,169,110,0.3) !important;
            background: rgba(201,169,110,0.03) !important;
        }
        .swagger-ui .opblock.opblock-post .opblock-summary-method {
            background: #c9a96e !important;
        }
        .swagger-ui .opblock.opblock-post .opblock-summary {
            border-color: rgba(201,169,110,0.3) !important;
        }
    </style>
    </head>
    """
    html_content = html_content.replace("</head>", custom_css)
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
