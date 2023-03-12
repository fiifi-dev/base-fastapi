import pathlib
from fastapi import UploadFile, BackgroundTasks
from helpers import storage


def upload_file(
    file_content: UploadFile,
    loc: str = "media",
    background_tasks: BackgroundTasks | None = None,
    is_thumb=False,
):
    minio = storage.MinioStorage()
    object_path = minio.save(f"{loc}/{file_content.filename}", file_content)

    has_thumb = background_tasks is not None and is_thumb

    if background_tasks is not None and is_thumb:
        background_tasks.add_task(
            minio.generate_thumbnail,
            object_path=f"{loc}/{file_content.filename}",
            content=file_content,
        )

    object_thumb_path = None

    if has_thumb:
        file_path: pathlib.Path = pathlib.Path(object_path)
        stem = file_path.stem if not is_thumb else f"thumb_{file_path.stem}"
        ext = file_path.suffix
        dir = file_path.parent

        object_thumb_path = f"{dir}/{stem}{ext}"

    return {"link": object_path, "thumb": object_thumb_path}
