import re
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.blog import Blog


class BlogRepository:
    """Data access layer for blog post records."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_all(self) -> list[Blog]:
        """Return all blog posts ordered by creation date descending."""
        stmt = select(Blog).order_by(Blog.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_by_id(self, blog_id: uuid.UUID) -> Blog | None:
        """Return a blog post by primary key."""
        stmt = select(Blog).where(Blog.id == blog_id)
        return self.db.scalar(stmt)

    def get_by_title(self, title: str) -> Blog | None:
        """Return a blog post matching the given title (case-insensitive)."""
        stmt = select(Blog).where(func.lower(Blog.title) == title.lower())
        return self.db.scalar(stmt)

    def get_by_slug(self, slug: str) -> Blog | None:
        """Return a blog post matching the given slug."""
        stmt = select(Blog).where(Blog.slug == slug)
        return self.db.scalar(stmt)

    def create(self, blog: Blog) -> Blog:
        """Persist a new blog post and return the saved record."""
        self.db.add(blog)
        self.db.commit()
        self.db.refresh(blog)
        return blog

    def update(self, blog: Blog) -> Blog:
        """Persist changes to an existing blog post."""
        self.db.commit()
        self.db.refresh(blog)
        return blog

    def delete(self, blog: Blog) -> None:
        """Remove a blog post from the database."""
        self.db.delete(blog)
        self.db.commit()


def generate_slug(title: str) -> str:
    """Generate a URL-safe slug from a blog title."""
    slug = title.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug or "blog-post"
