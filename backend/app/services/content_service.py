from sqlalchemy.orm import Session
from app.models.content import Content
from app.exceptions import NotFoundException, ForbiddenException

class ContentService:
    def __init__(self, db: Session):
        self.db = db

    def update_content(self, content_id: str, payload: dict, *, user_id: str):
        content = self.db.query(Content).filter(Content.id == content_id).first()
        if content is None:
            raise NotFoundException("Content not found")
        if str(content.user_id) != user_id:
            raise ForbiddenException(message="Access denied", code="FORBIDDEN")
        # Update content logic here
        return content