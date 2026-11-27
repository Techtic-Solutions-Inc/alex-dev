import { HttpException } from '../exceptions/http.exception';
import {
  buildPaginatedResult,
  buildPaginationMeta,
  normalizePaginationQuery,
  paginateArray,
  PAGINATION_DEFAULT_LIMIT,
  PAGINATION_DEFAULT_PAGE,
  PAGINATION_MAX_LIMIT,
} from './pagination.helper';

describe('pagination.helper', () => {
  it('test_pagination_success — normalizes defaults and computes skip', () => {
    const normalized = normalizePaginationQuery({});
    expect(normalized).toEqual({
      page: PAGINATION_DEFAULT_PAGE,
      limit: PAGINATION_DEFAULT_LIMIT,
      skip: 0,
    });
  });

  it('builds pagination metadata for non-empty totals', () => {
    expect(buildPaginationMeta(2, 20, 45)).toEqual({
      page: 2,
      limit: 20,
      total: 45,
      total_pages: 3,
      has_next: true,
      has_previous: true,
    });
  });

  it('returns an empty page with correct total when past the last page', () => {
    const items = Array.from({ length: 5 }, (_, index) => ({ id: index + 1 }));
    const result = paginateArray(items, { page: 10, limit: 20 });

    expect(result.items).toEqual([]);
    expect(result.pagination).toEqual({
      page: 10,
      limit: 20,
      total: 5,
      total_pages: 1,
      has_next: false,
      has_previous: true,
    });
  });

  it('wraps mapped items with buildPaginatedResult', () => {
    const result = buildPaginatedResult([{ id: 'a' }], 1, 1, 20);
    expect(result.items).toHaveLength(1);
    expect(result.pagination.total).toBe(1);
    expect(result.pagination.has_next).toBe(false);
  });

  it('rejects invalid page values with 422', () => {
    expect(() => normalizePaginationQuery({ page: 0, limit: 20 })).toThrow(HttpException);
    try {
      normalizePaginationQuery({ page: 0, limit: 20 });
    } catch (error) {
      expect(error).toBeInstanceOf(HttpException);
      expect((error as HttpException).status).toBe(422);
      expect((error as HttpException).code).toBe('VALIDATION_ERROR');
    }
  });

  it(`rejects limit above ${PAGINATION_MAX_LIMIT}`, () => {
    expect(() => normalizePaginationQuery({ page: 1, limit: PAGINATION_MAX_LIMIT + 1 })).toThrow(HttpException);
  });
});
