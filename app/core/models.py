import sqlalchemy as sa
import sqlalchemy.orm as orm


class Base(orm.DeclarativeBase):
    id: orm.Mapped[int] = orm.mapped_column(primary_key=True)

    @orm.declared_attr  # type: ignore
    def __tablename__(cls):
        return cls.__name__.lower()


class User(Base):
    email: orm.Mapped[str] = orm.mapped_column(
        sa.String(150),
        unique=True,
    )

    hashed_password: orm.Mapped[str] = orm.mapped_column(sa.String(200))

    role: orm.Mapped[str] = orm.mapped_column(
        sa.String(20),
        default="user",
    )

    first_name: orm.Mapped[str] = orm.mapped_column(
        sa.String(100),
        nullable=True,
    )

    last_name: orm.Mapped[str] = orm.mapped_column(
        sa.String(100),
        nullable=True,
    )

    is_admin: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        default=False,
    )

    is_active: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        default=False,
    )

    is_superuser: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        default=False,
    )

    is_verified: orm.Mapped[bool] = orm.mapped_column(
        sa.Boolean,
        default=False,
    )

    last_login: orm.Mapped[bool] = orm.mapped_column(
        sa.DATETIME,
        nullable=True,
    )

    date_joined: orm.Mapped[bool] = orm.mapped_column(
        sa.DATETIME,
        default=sa.func.now(),
    )


class Store(Base):
    link: orm.Mapped[str] = orm.mapped_column(
        sa.String(150),
        nullable=False,
    )
    thumb: orm.Mapped[str] = orm.mapped_column(
        sa.String(150),
        nullable=True,
    )
    created_at: orm.Mapped[bool] = orm.mapped_column(
        sa.DATETIME,
        default=sa.func.now(),
    )
