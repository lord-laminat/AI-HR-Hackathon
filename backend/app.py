from fastapi import FastAPI
from dotenv import load_dotenv

from routing.cv_analysis import router as cv_routing

load_dotenv()

app = FastAPI(openapi_url="/core/openapi.json", docs_url="/core/docs")
app.include_router(cv_routing)
