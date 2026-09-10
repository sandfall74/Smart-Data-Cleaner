from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_dataclean.api.router import api_router

app = FastAPI(
    title="DataClean AI API",
    description="API para limpieza, análisis y diagnóstico inteligente de datasets",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "DataClean AI Backend funcionando correctamente"}