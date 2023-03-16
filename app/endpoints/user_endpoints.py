from enum import Enum
import secrets
import sqlalchemy as sa

from fastapi import APIRouter, BackgroundTasks, Body, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session


from app.core import dependencies, exceptions, models, security, permissions
from app.core.config import settings
from app.crud import user_crud
from app.schemas import user_schemas
from app.helpers import general_schemas, emails, utils

router = APIRouter()


@router.get(
    "/",
    response_model=general_schemas.ListBaseSchema[user_schemas.ReadUserSchema],
    dependencies=[Depends(dependencies.get_current_active_superuser)],
)
def list_users(
    db: Session = Depends(dependencies.get_db),
    paginate_params: dict = Depends(dependencies.paginate_params),
    search: str | None = None,
    is_verified: bool | None = None,
    is_active: bool | None = None,
    order_by: user_crud.OrderUserBy = user_crud.OrderUserBy.date_joined,
    desc: bool = False,
):

    return user_crud.crud.read_list(
        db,
        skip=paginate_params["skip"],
        limit=paginate_params["limit"],
        search=search,
        is_verified=is_verified,
        is_active=is_active,
        order_by=order_by,
        desc=desc,
    )


@router.get("/me", response_model=user_schemas.ReadUserSchema)
def current_user(current_user=Depends(dependencies.get_current_active_user)):
    return current_user


@router.get("/test_email")
def test_email(background_tasks: BackgroundTasks):
    background_tasks.add_task(
        emails.send_test_email,
        email_to="fiifi.dev@gmail.com",
    )
    return {"detail": "ok"}


@router.put(
    "/update_password",
    response_model=user_schemas.ReadUserSchema,
)
def update_password(
    item: user_schemas.ChangeUserPasswordSchema,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
):
    is_valid = security.verify_password(item.old_password, current_user.hashed_password)

    if not is_valid:
        raise exceptions.PermissionDenied()

    return user_crud.crud.update_password(
        db,
        instance=current_user,
        item_schema=item,
    )


@router.get(
    "/{user_id}",
    response_model=user_schemas.ReadUserSchema,
    dependencies=[Depends(dependencies.get_current_active_superuser)],
)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(dependencies.get_db),
):
    return user_crud.crud.read_one(db, id=user_id)


@router.post(
    "/create-admin",
    response_model=user_schemas.ReadUserSchema,
    dependencies=[Depends(dependencies.get_current_active_superuser)],
)
def create_admin(
    background_tasks: BackgroundTasks,
    item: user_schemas.CreateAdminSchema,
    db: Session = Depends(dependencies.get_db),
):
    user = user_crud.crud.create_admin(db, item_schema=item)

    if user is not None:
        token = utils.generate_token(
            user.email,
            key=security.generate_user_secret_key(user),
            expire_time_in_hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
        )

        background_tasks.add_task(
            emails.send_new_account_email,
            user=user,
            token=token,
        )

    return user


@router.post(
    "/create-admin-complete",
    response_model=general_schemas.MessageSchema,
)
def create_admin_complete(
    uid: str,
    token: str,
    item: user_schemas.RegisterUserSchema,
    db: Session = Depends(dependencies.get_db),
):
    user = user_crud.crud.read_one(db, id=uid)

    if not user:
        raise exceptions.BadRequest(f"Account does not exist")

    email = utils.verify_token(token, security.generate_user_secret_key(user))

    if not email:
        raise exceptions.BadRequest(detail="Invalid token")

    user_crud.crud.create_admin_complete(
        db,
        instance=user,
        item_schema=item,
    )

    return {"detail": f"{user.email} registered successfully"}


@router.put(
    "/{user_id}",
    response_model=user_schemas.ReadUserSchema,
    dependencies=[Depends(dependencies.get_current_active_superuser)],
)
def update_user(
    user_id: str,
    item: user_schemas.UpdateUserSchema,
    db: Session = Depends(dependencies.get_db),
):
    instance = user_crud.crud.read_one(db, id=user_id)

    if instance is None:
        raise exceptions.NotFound()

    return user_crud.crud.update(db, id=user_id, update_schema=item)[0]


@router.get(
    "/{user_id}/toggle_status",
    response_model=user_schemas.ReadUserSchema,
    dependencies=[Depends(dependencies.get_current_active_superuser)],
)
def toggle_status(
    user_id: str,
    db: Session = Depends(dependencies.get_db),
):
    user = user_crud.crud.update_toggle_active(db, id=user_id)
    return user
