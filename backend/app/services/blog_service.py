import uuid

from sqlalchemy.orm import Session

from app.exceptions.http_exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.models.blog import Blog
from app.repositories.blog_repository import BlogRepository, generate_slug
from app.schemas.blog import BlogCreateRequest, BlogData, BlogUpdateRequest
from app.services.google_analytics_service import GoogleAnalyticsService

_DESCRIPTION_MAX_LENGTH = 200


class BlogService:
    """Business logic for blog post operations."""

    def __init__(self, db: Session) -> None:
        self.repository = BlogRepository(db)
        self.analytics = GoogleAnalyticsService()

    @staticmethod
    def _build_description(content: str, description: str | None) -> str:
        if description:
            return description.strip()
        stripped = content.strip()
        if len(stripped) <= _DESCRIPTION_MAX_LENGTH:
            return stripped
        return f"{stripped[:_DESCRIPTION_MAX_LENGTH].rstrip()}..."

    @staticmethod
    def _build_name(first_name: str | None, last_name: str | None) -> str:
        parts = [part for part in (first_name, last_name) if part]
        return " ".join(parts)

    @staticmethod
    def _build_link(blog_id: uuid.UUID) -> str:
        return f"/api/blog/{blog_id}"

    def _to_blog_data(self, blog: Blog) -> BlogData:
        return BlogData(
            id=str(blog.id),
            title=blog.title,
            content=blog.content,
            description=self._build_description(blog.content, blog.description),
            phone=blog.phone,
            phone_number=blog.phone,
            terms_accepted=blog.terms_accepted,
            first_name=blog.first_name,
            last_name=blog.last_name,
            email=blog.email,
            name=self._build_name(blog.first_name, blog.last_name),
            link=self._build_link(blog.id),
            error=None,
        )

    def _ensure_unique_slug(self, base_slug: str, exclude_id: uuid.UUID | None = None) -> str:
        slug = base_slug
        counter = 1
        while True:
            existing = self.repository.get_by_slug(slug)
            if existing is None or (exclude_id is not None and existing.id == exclude_id):
                return slug
            slug = f"{base_slug}-{counter}"
            counter += 1

    def list_blog_posts(self, *, user_id: str | None = None) -> list[BlogData]:
        """Return all blog posts."""
        blogs = self.repository.get_all()
        self.analytics.track_event("blog_list_viewed", user_id=user_id)
        return [self._to_blog_data(blog) for blog in blogs]

    def get_blog_post(
        self,
        blog_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> BlogData:
        """Return a single blog post by ID."""
        blog = self.repository.get_by_id(blog_id)
        if blog is None:
            raise NotFoundException(
                message="Blog post not found",
                code="BLOG_NOT_FOUND",
            )
        self.analytics.track_event(
            "blog_post_viewed",
            blog_id=blog.id,
            title=blog.title,
            user_id=user_id,
        )
        return self._to_blog_data(blog)

    def create_blog_post(
        self,
        payload: BlogCreateRequest,
        *,
        user_id: str | None = None,
    ) -> BlogData:
        """Create a new blog post."""
        if self.repository.get_by_title(payload.title):
            raise ConflictException(
                message="A blog post with this title already exists",
                code="BLOG_TITLE_ALREADY_EXISTS",
            )

        slug = self._ensure_unique_slug(generate_slug(payload.title))
        blog = Blog(
            title=payload.title,
            slug=slug,
            content=payload.content,
            description=self._build_description(payload.content, payload.description),
            phone=payload.phone,
            terms_accepted=payload.terms_accepted,
            first_name=payload.first_name,
            last_name=payload.last_name,
            email=str(payload.email) if payload.email else None,
        )
        saved = self.repository.create(blog)
        self.analytics.track_event(
            "blog_post_created",
            blog_id=saved.id,
            title=saved.title,
            user_id=user_id,
        )
        return self._to_blog_data(saved)

    def update_blog_post(
        self,
        blog_id: uuid.UUID,
        payload: BlogUpdateRequest,
        *,
        user_id: str | None = None,
    ) -> BlogData:
        """Update an existing blog post."""
        blog = self.repository.get_by_id(blog_id)
        if blog is None:
            raise NotFoundException(
                message="Blog post not found",
                code="BLOG_NOT_FOUND",
            )

        update_data = payload.model_dump(exclude_unset=True)
        if not update_data:
            raise BadRequestException(
                message="At least one field must be provided for update",
                code="VALIDATION_ERROR",
            )

        if "title" in update_data and update_data["title"] != blog.title:
            existing = self.repository.get_by_title(update_data["title"])
            if existing is not None and existing.id != blog.id:
                raise ConflictException(
                    message="A blog post with this title already exists",
                    code="BLOG_TITLE_ALREADY_EXISTS",
                )
            blog.title = update_data["title"]
            blog.slug = self._ensure_unique_slug(
                generate_slug(update_data["title"]),
                exclude_id=blog.id,
            )

        if "content" in update_data:
            blog.content = update_data["content"]

        if "description" in update_data:
            blog.description = update_data["description"]
        elif "content" in update_data:
            blog.description = self._build_description(
                update_data["content"],
                blog.description,
            )

        if "phone" in update_data:
            blog.phone = update_data["phone"]

        if "terms_accepted" in update_data:
            blog.terms_accepted = update_data["terms_accepted"]

        if "first_name" in update_data:
            blog.first_name = update_data["first_name"]

        if "last_name" in update_data:
            blog.last_name = update_data["last_name"]

        if "email" in update_data:
            blog.email = (
                str(update_data["email"]) if update_data["email"] else None
            )

        saved = self.repository.update(blog)
        self.analytics.track_event(
            "blog_post_updated",
            blog_id=saved.id,
            title=saved.title,
            user_id=user_id,
        )
        return self._to_blog_data(saved)

    def delete_blog_post(
        self,
        blog_id: uuid.UUID,
        *,
        user_id: str | None = None,
    ) -> None:
        """Delete a blog post by ID."""
        blog = self.repository.get_by_id(blog_id)
        if blog is None:
            raise NotFoundException(
                message="Blog post not found",
                code="BLOG_NOT_FOUND",
            )
        title = blog.title
        self.repository.delete(blog)
        self.analytics.track_event(
            "blog_post_deleted",
            blog_id=blog_id,
            title=title,
            user_id=user_id,
        )
