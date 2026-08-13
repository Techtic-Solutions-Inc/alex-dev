import uuid

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


def test_initial_migration_creates_users_table(
    db_engine: Engine,
    alembic_config: Config,
) -> None:
    command.downgrade(alembic_config, "base")
    command.upgrade(alembic_config, "head")

    inspector = inspect(db_engine)
    assert "users" in inspector.get_table_names()

    columns = {column["name"] for column in inspector.get_columns("users")}
    assert columns == {
        "id",
        "username",
        "email",
        "created_at",
        "updated_at",
        "first_name",
        "last_name",
        "hashed_password",
        "is_locked",
        "role",
        "mobile_number",
        "bio",
        "address_street",
        "address_city",
        "address_state",
        "address_zip",
        "address_country",
        "time_zone",
        "ai_credit_usage",
    }

    assert "blogs" in inspector.get_table_names()
    assert "contents" in inspector.get_table_names()

    content_columns = {
        column["name"] for column in inspector.get_columns("contents")
    }
    assert {
        "id",
        "caption",
        "description",
        "phone",
        "terms_accepted",
        "privacy_policy",
        "full_name",
        "created_at",
        "updated_at",
    }.issubset(content_columns)


def test_migration_rollback_drops_users_table(
    db_engine: Engine,
    alembic_config: Config,
) -> None:
    command.upgrade(alembic_config, "head")
    command.downgrade(alembic_config, "base")

    inspector = inspect(db_engine)
    assert "users" not in inspector.get_table_names()

    command.upgrade(alembic_config, "head")


def test_users_email_unique_constraint(db_session: Session) -> None:
    user_id = uuid.uuid4()
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
            "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false, 'user')"
        ),
        {
            "id": user_id,
            "username": "alice",
            "email": "alice@example.com",
            "first_name": "Alice",
            "last_name": "Example",
            "hashed_password": "hashed",
        },
    )
    db_session.flush()

    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "INSERT INTO users "
                "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
                "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false, 'user')"
            ),
            {
                "id": uuid.uuid4(),
                "username": "bob",
                "email": "alice@example.com",
                "first_name": "Bob",
                "last_name": "Example",
                "hashed_password": "hashed",
            },
        )
        db_session.flush()


def test_users_username_unique_constraint(db_session: Session) -> None:
    db_session.execute(
        text(
            "INSERT INTO users "
            "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
            "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false, 'user')"
        ),
        {
            "id": uuid.uuid4(),
            "username": "carol",
            "email": "carol@example.com",
            "first_name": "Carol",
            "last_name": "Example",
            "hashed_password": "hashed",
        },
    )
    db_session.flush()

    with pytest.raises(IntegrityError):
        db_session.execute(
            text(
                "INSERT INTO users "
                "(id, username, email, first_name, last_name, hashed_password, is_locked, role) "
                "VALUES (:id, :username, :email, :first_name, :last_name, :hashed_password, false, 'user')"
            ),
            {
                "id": uuid.uuid4(),
                "username": "carol",
                "email": "carol2@example.com",
                "first_name": "Carol",
                "last_name": "Duplicate",
                "hashed_password": "hashed",
            },
        )
        db_session.flush()
