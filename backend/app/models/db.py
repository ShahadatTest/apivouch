from sqlalchemy import String, Text, create_engine, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.pool import StaticPool

from app.core.config import DATABASE_URL

_engine_options = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
if DATABASE_URL in {"sqlite://", "sqlite:///:memory:"}:
    _engine_options["poolclass"] = StaticPool
engine = create_engine(DATABASE_URL, **_engine_options)


class Base(DeclarativeBase):
    pass


class ProjectRow(Base):
    __tablename__ = "projects"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    openapi_url: Mapped[str] = mapped_column(Text, default="")
    spec_json: Mapped[str] = mapped_column(Text, default="{}")
    analysis_json: Mapped[str] = mapped_column(Text, default="{}")
    tests_json: Mapped[str] = mapped_column(Text, default="[]")
    issues_json: Mapped[str] = mapped_column(Text, default="[]")
    score_json: Mapped[str] = mapped_column(Text, default="{}")
    repairs_json: Mapped[str] = mapped_column(Text, default="[]")
    tools_json: Mapped[str] = mapped_column(Text, default="[]")
    retest_json: Mapped[str] = mapped_column(Text, default="{}")
    proof_json: Mapped[str] = mapped_column(Text, default="{}")


def init_db() -> None:
    Base.metadata.create_all(engine)
    columns = {column["name"] for column in inspect(engine).get_columns("projects")}
    if "proof_json" not in columns:
        with engine.begin() as connection:
            connection.exec_driver_sql("ALTER TABLE projects ADD COLUMN proof_json TEXT DEFAULT '{}'")
