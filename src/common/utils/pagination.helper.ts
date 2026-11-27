import { HttpStatus } from '@nestjs/common';
import { HttpException } from '../exceptions/http.exception';

/** Default list page (1-based). */
export const PAGINATION_DEFAULT_PAGE = 1;

/** Default page size when `limit` is omitted. */
export const PAGINATION_DEFAULT_LIMIT = 20;

/** Hard maximum page size for collection endpoints. */
export const PAGINATION_MAX_LIMIT = 100;

export interface PaginationQueryInput {
  page?: number;
  limit?: number;
}

export interface NormalizedPagination {
  page: number;
  limit: number;
  skip: number;
}

/**
 * Standard pagination block returned by list endpoints (nested under `pagination` or flattened).
 */
export interface PaginationMeta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

/**
 * Consistent paginated payload shape for services and in-memory collections.
 */
export interface PaginatedResult<T> {
  items: T[];
  pagination: PaginationMeta;
}

export interface NormalizePaginationOptions {
  defaultPage?: number;
  defaultLimit?: number;
  maxLimit?: number;
}

/**
 * Validates and normalizes `page` / `limit` query parameters.
 *
 * - `page` must be an integer ≥ 1 (default {@link PAGINATION_DEFAULT_PAGE}).
 * - `limit` must be an integer between 1 and {@link PAGINATION_MAX_LIMIT} (default {@link PAGINATION_DEFAULT_LIMIT}).
 * - Returns `skip` for MongoDB `skip()` / SQL `OFFSET`.
 *
 * @throws {HttpException} 422 when `page` or `limit` are out of range.
 *
 * @example
 * ```ts
 * const { page, limit, skip } = normalizePaginationQuery({ page: 2, limit: 20 });
 * const [items, total] = await Promise.all([
 *   model.find(filter).sort(sort).skip(skip).limit(limit).exec(),
 *   model.countDocuments(filter).exec(),
 * ]);
 * return buildPaginatedResult(items.map(toDto), total, page, limit);
 * ```
 */
export function normalizePaginationQuery(
  input: PaginationQueryInput,
  options: NormalizePaginationOptions = {},
): NormalizedPagination {
  const defaultPage = options.defaultPage ?? PAGINATION_DEFAULT_PAGE;
  const defaultLimit = options.defaultLimit ?? PAGINATION_DEFAULT_LIMIT;
  const maxLimit = options.maxLimit ?? PAGINATION_MAX_LIMIT;

  const page = input.page ?? defaultPage;
  const limit = input.limit ?? defaultLimit;

  const details: Record<string, string[]> = {};

  if (!Number.isInteger(page) || page < 1) {
    details.page = ['page must be an integer greater than or equal to 1'];
  }

  if (!Number.isInteger(limit) || limit < 1 || limit > maxLimit) {
    details.limit = [`limit must be an integer between 1 and ${maxLimit}`];
  }

  if (Object.keys(details).length > 0) {
    throw new HttpException('Validation failed', HttpStatus.UNPROCESSABLE_ENTITY, 'VALIDATION_ERROR', details);
  }

  return {
    page,
    limit,
    skip: (page - 1) * limit,
  };
}

/**
 * Builds pagination metadata from the current page, page size, and total row count.
 */
export function buildPaginationMeta(page: number, limit: number, total: number): PaginationMeta {
  const totalPages = total === 0 ? 0 : Math.ceil(total / limit);

  return {
    page,
    limit,
    total,
    total_pages: totalPages,
    has_next: page < totalPages,
    has_previous: page > 1 && total > 0,
  };
}

/**
 * Wraps a page of items with {@link PaginationMeta} in the standard list format.
 */
export function buildPaginatedResult<T>(items: T[], total: number, page: number, limit: number): PaginatedResult<T> {
  return {
    items,
    pagination: buildPaginationMeta(page, limit, total),
  };
}

/**
 * Paginates an in-memory array (useful for tests or bounded derived collections).
 */
export function paginateArray<T>(items: T[], input: PaginationQueryInput): PaginatedResult<T> {
  const { page, limit, skip } = normalizePaginationQuery(input);
  const slice = items.slice(skip, skip + limit);
  return buildPaginatedResult(slice, items.length, page, limit);
}
