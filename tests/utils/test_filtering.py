import pytest
from src.utils.filtering import filter_data


def test_filter_data_happy_path():
    data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
    filters = {'age': 30}
    result = filter_data(data, filters)
    assert len(result) == 1
    assert result[0]['name'] == 'Alice'


def test_filter_data_edge_case_empty_data():
    data = []
    filters = {'age': 30}
    result = filter_data(data, filters)
    assert result == []


def test_filter_data_edge_case_no_matches():
    data = [{'name': 'Alice', 'age': 30}, {'name': 'Bob', 'age': 25}]
    filters = {'age': 40}
    result = filter_data(data, filters)
    assert result == []


def test_filter_data_error_case_invalid_filter_key():
    data = [{'name': 'Alice', 'age': 30}]
    filters = {'invalid_key': 'value'}
    with pytest.raises(KeyError):
        filter_data(data, filters)


def test_filter_data_error_case_invalid_filter_value():
    data = [{'name': 'Alice', 'age': 30}]
    filters = {'age': 'invalid_value'}
    with pytest.raises(TypeError):
        filter_data(data, filters)
