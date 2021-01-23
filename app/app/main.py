from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.core.config import settings

from fastapi_profiler.profiler_middleware import PyInstrumentProfilerMiddleware

import sqltap

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.ENV == 'development':
    app.add_middleware(PyInstrumentProfilerMiddleware)

    @app.middleware("http")
    async def add_sql_tap(request: Request, call_next):
        profiler = sqltap.start()
        response = await call_next(request)
        statistics = profiler.collect()
        print(statistics);
        #sqltap.report(statistics, "report.html")
        # sqltap.report(statistics, "report.txt", report_format="text")
        return response

app.include_router(api_router, prefix=settings.API_V1_STR)
