import sqlalchemy as sa
import copy
from sqlalchemy.orm import Session
from typing import Any, Generic, Type, TypeVar
from fastapi.encoders import jsonable_encoder
from fastapi import status, exceptions
from pydantic import BaseModel
from app.core.models import Base


ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class BaseCrud(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    def __get_object_stmt(self, id: int | str):
        return sa.select(self.model).where(self.model.id == id)

    def _get_object(self, db: Session, *, id: int | str) -> ModelT:
        stmt = self.__get_object_stmt(id)
        obj = db.scalar(stmt)

        if obj is None:
            raise exceptions.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find this record",
            )

        return obj

    def _get_sql_stmt(self, *, skip: int, limit: int):
        return sa.select(self.model).offset(skip).limit(limit)

    def _get_list(
        self,
        db: Session,
        *,
        query: sa.Select[tuple[ModelT]],
        skip: int = 0,
        limit: int = 20
    ):
        stmtCount = sa.select(sa.func.count()).select_from(self.model)

        count = db.scalars(stmtCount).first()

        if count == None:
            count = 0

        next = skip + 1 if (skip + 1) * limit < count else None
        prev = skip - 1 if skip > 0 else None

        items = db.scalars(query).all()

        return {
            "data": items,
            "count": count,
            "next": next,
            "prev": prev,
        }

    def read_one(self, db: Session, *, id: int | str):
        return self._get_object(db, id=id)

    def read_list(self, db: Session, *, skip: int = 0, limit: int = 20):
        stmt = self._get_sql_stmt(skip=skip, limit=limit)
        return self._get_list(db, query=stmt, skip=skip, limit=limit)

    def create(
        self, db: Session, create_schema: CreateSchemaT | dict[str, Any]
    ) -> ModelT | None:
        data = (
            create_schema
            if isinstance(create_schema, "dict")
            else create_schema.dict(exclude_unset=True)
        )
        stmt = sa.insert(self.model).values(**data)
        item = db.execute(stmt)
        db.commit()

        (pk,) = item.inserted_primary_key  # type: ignore
        return db.scalar(sa.select(self.model).where(self.model.id == pk))

    def update(
        self,
        db: Session,
        *,
        id: int | str,
        update_schema: UpdateSchemaT | dict[str, Any]
    ) -> tuple[ModelT, ModelT]:
        instance = self._get_object(db, id=id)
        old_instance = copy.deepcopy(instance)
        data = (
            update_schema
            if isinstance(update_schema, "dict")
            else update_schema.dict(exclude_unset=True)
        )
        stmt = sa.update(self.model).where(self.model.id == instance.id).values(**data)
        db.execute(stmt)
        db.commit()
        db.refresh(instance)
        return instance, old_instance

    def destroy(self, db: Session, *, id: int | str) -> ModelT:
        instance = self._get_object(db, id=id)

        stmt = sa.delete(self.model).where(self.model.id == instance.id)
        db.execute(stmt)
        db.commit()

        return instance
