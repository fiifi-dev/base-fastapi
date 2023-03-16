from fastapi import APIRouter, Depends, BackgroundTasks, UploadFile
from sqlalchemy.orm import Session
from app.core import dependencies
from app.schemas import store_schemas
from app.helpers import files, general_schemas, storage
from app.crud import store_crud

router = APIRouter()


@router.post("/upload-image/", response_model=store_schemas.CreateStoreSchema)
def upload_image(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    loc: str = "media",
    current_user=Depends(dependencies.get_current_active_user),
):
    return files.upload_file(file, loc, background_tasks, True)


@router.get(
    "/",
    response_model=general_schemas.ListBaseSchema[store_schemas.ReadStoreSchema],
)
def get_all_store(
    db: Session = Depends(dependencies.get_db),
    paginate_params: dict = Depends(dependencies.paginate_params),
    current_user=Depends(dependencies.get_current_active_user),
):

    return store_crud.crud.read_list(
        db,
        skip=paginate_params["skip"],
        limit=paginate_params["limit"],
    )


@router.post(
    "/",
    response_model=store_schemas.ReadStoreSchema,
)
def create_store(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    loc: str = "media",
    db: Session = Depends(dependencies.get_db),
    current_user=Depends(dependencies.get_current_active_user),
):
    data = files.upload_file(file, loc, background_tasks, True)
    store_schema = store_schemas.CreateStoreSchema(**data)

    return store_crud.crud.create(db, create_schema=store_schema)


@router.put(
    "/{store_id}",
    response_model=store_schemas.ReadStoreSchema,
)
def update_store(
    background_tasks: BackgroundTasks,
    store_id: int,
    file: UploadFile,
    loc: str = "media",
    db: Session = Depends(dependencies.get_db),
    current_user=Depends(dependencies.get_current_active_user),
):
    store = store_crud.crud.read_one(db, id=store_id)
    minio_storage = storage.MinioStorage()

    data = files.upload_file(file, loc, background_tasks, True)
    store_schema = store_schemas.CreateStoreSchema(**data)
    obj = store_crud.crud.update(
        db,
        update_schema=store_schema,
        id=store_id,
    )[0]

    background_tasks.add_task(
        minio_storage.delete,
        object_path=store.link,
    )

    if store.thumb:
        background_tasks.add_task(
            minio_storage.delete,
            object_path=store.thumb,
        )

    return obj


@router.get(
    "/{store_id}",
    response_model=store_schemas.ReadStoreSchema,
)
def get_one_store(
    store_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user=Depends(dependencies.get_current_active_user),
):

    res = store_crud.crud.read_one(
        db,
        id=store_id,
    )

    return res


@router.delete(
    "/{store_id}",
    response_model=store_schemas.ReadStoreSchema,
)
def destroy_store(
    background_tasks: BackgroundTasks,
    store_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user=Depends(dependencies.get_current_active_user),
):
    store = store_crud.crud.read_one(db, id=store_id)
    minio_storage = storage.MinioStorage()

    res = store_crud.crud.destroy(
        db,
        id=store_id,
    )

    background_tasks.add_task(
        minio_storage.delete,
        object_path=store.link,
    )

    if store.thumb:
        background_tasks.add_task(
            minio_storage.delete,
            object_path=store.thumb,
        )

    return res
