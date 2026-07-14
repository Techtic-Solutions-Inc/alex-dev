from typing import Any, List


def paginate(query: Any, page: int, page_size: int) -> List[Any]:
    """
    Paginates the given query.

    Args:
        query: The query to paginate.
        page (int): The page number to retrieve.
        page_size (int): The number of items per page.

    Returns:
        List[Any]: A list of items for the requested page.
    """
    if page < 1:
        raise ValueError('Page number must be greater than 0')
    if page_size < 1:
        raise ValueError('Page size must be greater than 0')

    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size).all()


def sort(query: Any, sort_by: str, order: str) -> Any:
    """
    Sorts the given query based on the specified field and order.

    Args:
        query: The query to sort.
        sort_by (str): The field to sort by.
        order (str): The order to sort in ('asc' or 'desc').

    Returns:
        Any: The sorted query.
    """
    if order not in ['asc', 'desc']:
        raise ValueError('Order must be either asc or desc')

    return query.order_by(getattr(query.model, sort_by).asc() if order == 'asc' else getattr(query.model, sort_by).desc())