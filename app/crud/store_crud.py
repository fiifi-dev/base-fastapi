from app.helpers.crud import BaseCrud
import sqlalchemy as sa
from app.core import models
from app.schemas import store_schemas


class StoreCrud(
    BaseCrud[
        models.Store,
        store_schemas.CreateStoreSchema,
        store_schemas.CreateStoreSchema,
    ]
):
    def get_sql_stmt(self, *, skip: int, limit: int):
        return (
            super()
            .get_sql_stmt(skip=skip, limit=limit)
            .order_by(models.Store.created_at.desc())
        )


crud = StoreCrud(models.Store)
