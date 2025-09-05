from fastapi import FastAPI
from routing.cv_analysis import router as cv_routing

app = FastAPI(openapi_url="/core/openapi.json", docs_url="/core/docs")

app.include_router(cv_routing)
