from models.user import User


class TestUserModel:
    def test_tablename(self) -> None:
        assert User.__tablename__ == "users"

    def test_default_is_confirmed_false(self) -> None:
        user = User(email="test@example.com", hashed_password="hashed")
        assert user.is_confirmed is False

    def test_required_fields(self) -> None:
        columns = {c.name for c in User.__table__.columns}
        assert "id" in columns
        assert "email" in columns
        assert "hashed_password" in columns
        assert "is_confirmed" in columns
        assert "created_at" in columns
        assert "updated_at" in columns

    def test_profile_fields_exist(self) -> None:
        columns = {c.name for c in User.__table__.columns}
        assert "first_name" in columns
        assert "last_name" in columns
        assert "mobile_number" in columns
        assert "bio" in columns
        assert "address" in columns
        assert "profile_picture" in columns

    def test_email_column_is_unique(self) -> None:
        email_col = User.__table__.columns["email"]
        assert email_col.unique is True

    def test_email_column_is_indexed(self) -> None:
        email_col = User.__table__.columns["email"]
        assert email_col.index is True

    def test_email_not_nullable(self) -> None:
        email_col = User.__table__.columns["email"]
        assert email_col.nullable is False

    def test_hashed_password_not_nullable(self) -> None:
        col = User.__table__.columns["hashed_password"]
        assert col.nullable is False

    def test_id_is_primary_key(self) -> None:
        id_col = User.__table__.columns["id"]
        assert id_col.primary_key is True
