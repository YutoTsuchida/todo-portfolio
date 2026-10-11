import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from tests.integration.conftest import require_test_database_url

pytestmark = pytest.mark.integration


def test_initial_migration_upgrade_downgrade_upgrade(alembic_config: Config) -> None:
    """REQ-D-001..008, REQ-SEC-008, REQ-T-008: migration round trip."""
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")
    engine = create_engine(require_test_database_url())
    try:
        assert not {"users", "todos", "sessions"} & set(
            inspect(engine).get_table_names()
        )
    finally:
        engine.dispose()

    command.upgrade(alembic_config, "head")
    command.upgrade(alembic_config, "head")


def test_initial_migration_schema(alembic_config: Config) -> None:
    """REQ-D-001..008, REQ-SEC-008: required DB objects are explicit."""
    command.upgrade(alembic_config, "head")
    engine = create_engine(require_test_database_url())
    try:
        db_inspector = inspect(engine)
        assert {"users", "todos", "sessions"} <= set(db_inspector.get_table_names())
        assert db_inspector.get_pk_constraint("users")["name"] == "pk_users"
        assert db_inspector.get_pk_constraint("todos")["name"] == "pk_todos"
        assert db_inspector.get_pk_constraint("sessions")["name"] == "pk_sessions"
        assert {
            constraint["name"]
            for constraint in db_inspector.get_unique_constraints("users")
        } == {"uq_users_username"}
        for table_name in ("todos", "sessions"):
            foreign_keys = db_inspector.get_foreign_keys(table_name)
            assert len(foreign_keys) == 1
            assert foreign_keys[0]["referred_table"] == "users"
            assert foreign_keys[0]["referred_columns"] == ["id"]
            assert foreign_keys[0]["options"]["ondelete"] == "RESTRICT"
        for table_name in ("users", "todos", "sessions"):
            assert all(
                not column["nullable"]
                for column in db_inspector.get_columns(table_name)
            )
        assert {
            constraint["name"]
            for constraint in db_inspector.get_check_constraints("users")
        } == {"ck_users_username_format"}
        assert {
            constraint["name"]
            for constraint in db_inspector.get_check_constraints("todos")
        } == {
            "ck_todos_description_length",
            "ck_todos_status_values",
            "ck_todos_title_length",
            "ck_todos_title_no_newlines",
            "ck_todos_title_no_surrounding_whitespace",
        }
        assert {
            constraint["name"]
            for constraint in db_inspector.get_check_constraints("sessions")
        } == {
            "ck_sessions_fixed_duration",
            "ck_sessions_token_hash_length",
        }
        assert {index["name"] for index in db_inspector.get_indexes("sessions")} == {
            "ix_sessions_expires_at",
            "ix_sessions_user_id",
        }
        with engine.connect() as connection:
            index_definition = connection.execute(
                text(
                    "SELECT indexdef FROM pg_indexes "
                    "WHERE schemaname = current_schema() "
                    "AND indexname = 'ix_todos_user_id_created_at_id'"
                )
            ).scalar_one()
        assert "(user_id, created_at DESC, id DESC)" in index_definition
    finally:
        engine.dispose()
