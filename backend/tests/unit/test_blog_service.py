import uuid
from unittest.mock import MagicMock

import pytest
from app.exceptions.http_exceptions import ConflictException, NotFoundException
from app.models.blog import Blog
from app.schemas.blog import BlogCreateRequest, BlogUpdateRequest
from app.services.blog_service import BlogService


@pytest.fixture
def mock_db() -> MagicMock:
    return MagicMock()


@pytest.fixture
def blog_service(mock_db: MagicMock) -> BlogService:
    return BlogService(mock_db)


@pytest.fixture
def sample_blog() -> Blog:
    return Blog(
        id=uuid.uuid4(),
        title="Sample Blog",
        slug="sample-blog",
        content="Sample content for the blog post.",
        description="Sample content for the blog post.",
        phone="+1-555-0100",
        terms_accepted=True,
        first_name="Jane",
        last_name="Smith",
        email="jane@example.com",
    )


def test_create_blog_post_success(
    blog_service: BlogService,
    sample_blog: Blog,
) -> None:
    blog_service.repository.get_by_title = MagicMock(return_value=None)
    blog_service.repository.get_by_slug = MagicMock(return_value=None)
    blog_service.repository.create = MagicMock(return_value=sample_blog)
    blog_service.analytics.track_event = MagicMock()

    payload = BlogCreateRequest(
        title="Sample Blog",
        content="Sample content for the blog post.",
        terms_accepted=True,
        phone="+1-555-0100",
    )
    result = blog_service.create_blog_post(payload, user_id="user-1")

    assert result.title == sample_blog.title
    assert result.phone_number == sample_blog.phone
    assert result.link == f"/api/blog/{sample_blog.id}"
    blog_service.repository.create.assert_called_once()


def test_create_blog_post_missing_fields_validation() -> None:
    with pytest.raises(Exception):
        BlogCreateRequest(
            title="",
            content="",
            terms_accepted=True,
            phone="",
        )


def test_create_blog_post_duplicate_title(
    blog_service: BlogService,
    sample_blog: Blog,
) -> None:
    blog_service.repository.get_by_title = MagicMock(return_value=sample_blog)

    payload = BlogCreateRequest(
        title="Sample Blog",
        content="Another content.",
        terms_accepted=True,
        phone="+1-555-0100",
    )

    with pytest.raises(ConflictException) as exc_info:
        blog_service.create_blog_post(payload)

    assert exc_info.value.code == "BLOG_TITLE_ALREADY_EXISTS"


def test_update_blog_post_success(
    blog_service: BlogService,
    sample_blog: Blog,
) -> None:
    blog_service.repository.get_by_id = MagicMock(return_value=sample_blog)
    blog_service.repository.get_by_title = MagicMock(return_value=None)
    blog_service.repository.get_by_slug = MagicMock(return_value=None)
    blog_service.repository.update = MagicMock(return_value=sample_blog)
    blog_service.analytics.track_event = MagicMock()

    payload = BlogUpdateRequest(title="Updated Title")
    result = blog_service.update_blog_post(sample_blog.id, payload)

    assert result.title == sample_blog.title
    blog_service.repository.update.assert_called_once()


def test_update_blog_post_not_found(blog_service: BlogService) -> None:
    blog_service.repository.get_by_id = MagicMock(return_value=None)

    with pytest.raises(NotFoundException) as exc_info:
        blog_service.update_blog_post(
            uuid.uuid4(),
            BlogUpdateRequest(title="Updated"),
        )

    assert exc_info.value.code == "BLOG_NOT_FOUND"


def test_delete_blog_post_success(
    blog_service: BlogService,
    sample_blog: Blog,
) -> None:
    blog_service.repository.get_by_id = MagicMock(return_value=sample_blog)
    blog_service.repository.delete = MagicMock()
    blog_service.analytics.track_event = MagicMock()

    blog_service.delete_blog_post(sample_blog.id)

    blog_service.repository.delete.assert_called_once_with(sample_blog)


def test_delete_blog_post_not_found(blog_service: BlogService) -> None:
    blog_service.repository.get_by_id = MagicMock(return_value=None)

    with pytest.raises(NotFoundException) as exc_info:
        blog_service.delete_blog_post(uuid.uuid4())

    assert exc_info.value.code == "BLOG_NOT_FOUND"
