import pytest
from sqlalchemy.orm import Session
from src.api.v1.models.user import User

@pytest.fixture
def create_user(db: Session):
    def _create_user(name='Test User', email='testuser@example.com', password='securepassword', role='user'):
        user = User(name=name, email=email, password=password, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    return _create_user
