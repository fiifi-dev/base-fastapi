import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session


from core import management, database
from core.config import settings
from helpers import general_schemas
from endpoints import auth_endpoints, user_endpoints, store_endpoints

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    responses={
        422: {
            "model": general_schemas.ErrorSchema,
            "description": "Validation Error: get only has the path errors",
        }
    },
)

if settings.ALLOWED_HOSTS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

MEDIA_DIR = f"{settings.MEDIA_DIR}"
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.exception_handler(RequestValidationError)
def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    body_errors = {}
    path_errors = []

    for error in exc.errors():
        type, field = error["loc"]  # type is body or path
        if type == "body":
            body_errors[field] = error["msg"]
        elif type in ["path", "query"]:
            path_errors.append(f"{type} {field} : {error['msg']}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": {"body": body_errors, "path": path_errors},
        },
    )


@app.on_event("startup")
async def create_database():
    management.create_database()


@app.on_event("startup")
async def create_first_user():
    db: Session = database.SessionLocal()
    try:
        management.create_first_user(db)
    finally:
        db.close()


@app.on_event("startup")
async def create_minio_bucket():
    management.create_minio_bucket()


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(
    auth_endpoints.router,
    prefix="/auth",
    tags=["auth"],
)


app.include_router(
    user_endpoints.router,
    prefix="/users",
    tags=["users"],
)

app.include_router(
    store_endpoints.router,
    prefix="/store",
    tags=["store"],
)
