from datetime import datetime
from enum import Enum
import secrets
from typing import Any
from helpers.crud import BaseCrud
from sqlalchemy.orm import Session
import sqlalchemy as sa
from core import models, exceptions
from schemas import user_schemas
from core.security import get_password_hash, verify_password


class OrderUserBy(str, Enum):
    date_joined = "date_joined"
    by_email = "email"


class UserCrud(
    BaseCrud[
        models.User,
        user_schemas.RegisterUserSchema,
        user_schemas.UpdateUserSchema,
    ]
):
    def get_sql_stmt(
        self,
        *,
        skip: int,
        limit: int,
        search: str | None = None,
        is_verified: bool | None = None,
        is_active: bool | None = None,
        order_by: OrderUserBy = OrderUserBy.date_joined,
        desc: bool | None = False,
    ):
        stmt = super().get_sql_stmt(skip=skip, limit=limit)

        if search is not None:
            stmt = stmt.where(
                sa.or_(
                    models.User.email.ilike(search),
                    models.User.first_name.ilike(search),
                    models.User.last_name.ilike(search),
                )
            )

        if is_verified is not None:
            stmt = stmt.where(models.User.is_verified == is_verified)

        if is_active is not None:
            stmt = stmt.where(models.User.is_active == is_active)

        if order_by == OrderUserBy.by_email:
            order_col = models.User.email
            if desc:
                order_col = models.User.email.desc()
            stmt = stmt.order_by(order_col)
        else:
            order_col = models.User.date_joined
            if desc:
                order_col = models.User.date_joined.desc()
            stmt = stmt.order_by(order_col)

        return stmt

    def read_list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        is_verified: bool | None = None,
        is_active: bool | None = None,
        order_by: OrderUserBy = OrderUserBy.date_joined,
        desc: bool | None = False,
    ):
        stmt = self.get_sql_stmt(
            skip=skip,
            limit=limit,
            search=search,
            is_verified=is_verified,
            is_active=is_active,
            order_by=order_by,
            desc=desc,
        )
        return super().get_list(db, query=stmt, skip=skip, limit=limit)

    def get_by_email(self, db: Session, *, email: Any) -> models.User | None:
        stmt = sa.select(models.User).where(models.User.email == email)
        user = db.execute(stmt).scalar_one_or_none()
        return user

    def is_active(self, instance: models.User):
        return instance.is_active

    def is_superuser(self, instance: models.User):
        return instance.is_superuser

    def user_exists(self, db: Session, *, email: Any) -> models.User:
        user = self.get_by_email(db, email=email)

        if user is None:
            raise exceptions.BadRequest(detail="User already exists")

        return user

    def create_admin_complete(
        self,
        db: Session,
        *,
        instance: models.User,
        item_schema: user_schemas.RegisterUserSchema,
    ) -> models.User | None:
        data = item_schema.dict(exclude={"password_confirm"})
        password = data.pop("password")
        email = data.get("email")

        stmt = (
            sa.update(models.User)
            .where(models.User.id == instance.id)
            .values(
                **data,
                is_active=True,
                is_verified=True,
                hashed_password=get_password_hash(password),
            )
        )
        db.execute(stmt)

        user = self.get_by_email(db, email=email)
        db.commit()
        db.refresh(instance)
        return user

    def create_admin(
        self, db: Session, *, item_schema: user_schemas.CreateAdminSchema
    ) -> models.User | None:
        data = item_schema.dict()
        email = data.get("email")

        stmt = sa.insert(models.User).values(
            **data,
            hashed_password=get_password_hash(secrets.token_urlsafe(10)),
        )
        db.execute(stmt)

        user = self.get_by_email(db, email=email)
        db.commit()
        return user

    def reset_password_complete(
        self,
        db: Session,
        *,
        instance: models.User,
        item_schema: user_schemas.ResetUserPasswordSchema,
    ):
        data = item_schema.dict()
        password = data.get("password")

        stmt = (
            sa.update(models.User)
            .where(models.User.email == instance.id)
            .values(
                hashed_password=get_password_hash(password),
            )
        )
        db.execute(stmt)
        db.commit()
        db.refresh(instance)
        return instance

    def update_password(
        self,
        db: Session,
        *,
        instance: models.User,
        item_schema: user_schemas.ChangeUserPasswordSchema,
    ):
        data = item_schema.dict()
        old_password = data.get("old_password")
        password = data.get("password")

        if verify_password(old_password, instance.hashed_password):
            raise exceptions.PermissionDenied()

        stmt = (
            sa.update(models.User)
            .where(models.User.id == instance.id)
            .values(
                hashed_password=get_password_hash(password),
            )
        )
        db.execute(stmt)
        db.commit()
        db.refresh(instance)
        return instance

    def update_toggle_active(self, db: Session, *, id: str):

        user = self.get_object(db, id=id)

        stmt = (
            sa.update(models.User)
            .where(models.User.id == id)
            .values(
                is_active=not user.is_active,
            )
        )
        db.execute(stmt)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(
        self, db: Session, *, email: str, password: str
    ) -> models.User | None:
        user = self.get_by_email(db, email=email)

        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_superuser(self, db: Session, *, email: str, password: str):
        user = self.get_by_email(db, email=email)

        if user is not None:
            return

        stmt = sa.insert(models.User).values(
            email=email,
            is_superuser=True,
            is_active=True,
            is_verified=True,
            hashed_password=get_password_hash(password),
        )

        db.execute(stmt)
        db.commit()
        return self.get_by_email(db, email=email)

    def update_last_login(self, db: Session, *, instance: models.User):
        stmt = (
            sa.update(models.User)
            .where(models.User.id == instance.id)
            .values(last_login=datetime.utcnow())
        )
        db.execute(stmt)
        db.commit()
        db.refresh(instance)

        return instance


crud = UserCrud(models.User)
