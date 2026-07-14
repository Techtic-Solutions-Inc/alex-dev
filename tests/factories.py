import pytest
from sqlalchemy.orm import Session
from src.models import User


@pytest.fixture
def sample_user(db: Session):
    user = User(name='Test User', email='testuser@example.com', password='hashed_password', role='user')
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
