import pytest
from src.utils.pagination import paginate


def test_paginate_happy_path():
    data = list(range(100))  # Sample data
    page_size = 10
    page_number = 1
    result = paginate(data, page_number, page_size)
    assert len(result) == 10
    assert result == list(range(10))


def test_paginate_edge_case_empty_data():
    data = []
    page_size = 10
    page_number = 1
    result = paginate(data, page_number, page_size)
    assert result == []


def test_paginate_edge_case_large_page_number():
    data = list(range(100))
    page_size = 10
    page_number = 100
    result = paginate(data, page_number, page_size)
    assert result == []


def test_paginate_error_case_invalid_page_number():
    data = list(range(100))
    page_size = 10
    page_number = -1
    with pytest.raises(ValueError):
        paginate(data, page_number, page_size)


def test_paginate_error_case_invalid_page_size():
    data = list(range(100))
    page_size = 0
    page_number = 1
    with pytest.raises(ValueError):
        paginate(data, page_number, page_size)
