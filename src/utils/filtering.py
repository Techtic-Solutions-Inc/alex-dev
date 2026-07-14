from typing import Any, Dict


def filter_query(query: Any, filters: Dict[str, Any]) -> Any:
    """
    Applies filtering to the given query based on the provided filters.

    Args:
        query: The query to filter.
        filters (dict): A dictionary of filters to apply.

    Returns:
        Any: The filtered query.
    """
    for key, value in filters.items():
        if hasattr(query.model, key):
            query = query.filter(getattr(query.model, key) == value)
        else:
            raise ValueError(f'Invalid filter key: {key}')
    return query