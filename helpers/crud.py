import sqlalchemy as sa
from sqlalchemy.orm import Session
from typing import Any, Generic, Type, TypeVar
from fastapi.encoders import jsonable_encoder
from fastapi import status, exceptions
from pydantic import BaseModel
from core.models import Base


ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class BaseCrud(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    def get_object(self, db: Session, *, id: int | str) -> ModelT:
        stmt = sa.select(self.model).where(self.model.id == id)
        obj = db.scalar(stmt)

        if obj is None:
            raise exceptions.HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find this record",
            )

        return obj

    def get_sql_stmt(self, *, skip: int, limit: int):
        return sa.select(self.model).offset(skip).limit(limit)

    def get_list(
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
        return self.get_object(db, id=id)

    def read_list(self, db: Session, *, skip: int = 0, limit: int = 20):
        stmt = self.get_sql_stmt(skip=skip, limit=limit)
        return self.get_list(db, query=stmt, skip=skip, limit=limit)

    def create(self, db: Session, create_schema: CreateSchemaT) -> ModelT | None:
        stmt = sa.insert(self.model).values(**create_schema.dict())
        item = db.execute(stmt)
        db.commit()

        (pk,) = item.inserted_primary_key  # type: ignore
        return db.scalar(sa.select(self.model).where(self.model.id == pk))

    def update(
        self, db: Session, *, id: int | str, update_schema: UpdateSchemaT
    ) -> ModelT | None:
        instance = self.get_object(db, id=id)

        stmt = (
            sa.update(self.model)
            .where(self.model.id == instance.id)
            .values(**update_schema.dict(exclude_unset=True))
        )
        db.execute(stmt)
        db.commit()
        db.refresh(instance)
        return instance

    def destroy(self, db: Session, *, id: int | str) -> ModelT | None:
        instance = self.get_object(db, id=id)

        stmt = sa.delete(self.model).where(self.model.id == instance.id)
        db.execute(stmt)
        db.commit()

        return instance
