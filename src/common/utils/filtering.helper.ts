export type FilterOperator = 'eq' | 'ne' | 'in' | 'nin' | 'gt' | 'gte' | 'lt' | 'lte' | 'regex' | 'exists';

/**
 * One filter condition applied to a single field.
 */
export interface FilterCriterion {
  field: string;
  operator: FilterOperator;
  value: unknown;
}

export type MongoFilter = Record<string, unknown>;

export interface BuildMongoFilterOptions {
  /** Only these field names may appear in the output (prevents arbitrary query injection). */
  allowedFields?: readonly string[];
}

/**
 * Escapes user input for safe use inside a `RegExp`.
 */
export function escapeRegexForFilter(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

/**
 * Builds a case-insensitive `$or` regex filter across multiple string fields (list `search` query param).
 *
 * @example
 * ```ts
 * const filter = mergeMongoFilters(
 *   { is_active: true },
 *   buildTextSearchFilter(query.search, ['title', 'description']),
 * );
 * ```
 */
export function buildTextSearchFilter(search: string | undefined, fields: readonly string[]): MongoFilter {
  const term = search?.trim();
  if (!term || fields.length === 0) {
    return {};
  }

  const pattern = new RegExp(escapeRegexForFilter(term), 'i');
  return {
    $or: fields.map((field) => ({ [field]: pattern })),
  };
}

/**
 * Converts structured {@link FilterCriterion} entries into a MongoDB filter document.
 * Unknown fields are skipped when `allowedFields` is provided.
 */
export function buildMongoFilter(
  criteria: readonly FilterCriterion[],
  options: BuildMongoFilterOptions = {},
): MongoFilter {
  const allowed = options.allowedFields ? new Set(options.allowedFields) : null;
  const filter: MongoFilter = {};

  for (const criterion of criteria) {
    if (allowed && !allowed.has(criterion.field)) {
      continue;
    }

    switch (criterion.operator) {
      case 'eq':
        filter[criterion.field] = criterion.value;
        break;
      case 'ne':
        filter[criterion.field] = { $ne: criterion.value };
        break;
      case 'in':
        filter[criterion.field] = { $in: criterion.value };
        break;
      case 'nin':
        filter[criterion.field] = { $nin: criterion.value };
        break;
      case 'gt':
        filter[criterion.field] = { $gt: criterion.value };
        break;
      case 'gte':
        filter[criterion.field] = { $gte: criterion.value };
        break;
      case 'lt':
        filter[criterion.field] = { $lt: criterion.value };
        break;
      case 'lte':
        filter[criterion.field] = { $lte: criterion.value };
        break;
      case 'regex':
        filter[criterion.field] = criterion.value;
        break;
      case 'exists':
        filter[criterion.field] = { $exists: criterion.value };
        break;
      default:
        break;
    }
  }

  return filter;
}

/**
 * Merges MongoDB filter fragments. Later fragments override scalar keys on the root object.
 */
export function mergeMongoFilters(...parts: readonly MongoFilter[]): MongoFilter {
  return parts.reduce<MongoFilter>((merged, part) => {
    for (const [key, value] of Object.entries(part)) {
      if (key === '$or' && Array.isArray(merged.$or) && Array.isArray(value)) {
        merged.$or = [...merged.$or, ...value];
        continue;
      }
      merged[key] = value;
    }
    return merged;
  }, {});
}

export interface InMemoryPredicate<T> {
  (item: T): boolean;
}

/**
 * Creates a predicate from {@link FilterCriterion} list for array filtering in memory.
 */
export function buildInMemoryPredicates<T extends Record<string, unknown>>(
  criteria: readonly FilterCriterion[],
  options: BuildMongoFilterOptions = {},
): InMemoryPredicate<T>[] {
  const allowed = options.allowedFields ? new Set(options.allowedFields) : null;

  return criteria
    .filter((criterion) => !allowed || allowed.has(criterion.field))
    .map((criterion) => (item: T) => evaluateCriterion(item[criterion.field], criterion));
}

/**
 * Filters an array using {@link FilterCriterion} with consistent semantics to {@link buildMongoFilter}.
 */
export function filterInMemory<T extends Record<string, unknown>>(
  items: T[],
  criteria: readonly FilterCriterion[],
  options: BuildMongoFilterOptions = {},
): T[] {
  const predicates = buildInMemoryPredicates(criteria, options);
  if (predicates.length === 0) {
    return [...items];
  }

  return items.filter((item) => predicates.every((predicate) => predicate(item)));
}

function evaluateCriterion(fieldValue: unknown, criterion: FilterCriterion): boolean {
  switch (criterion.operator) {
    case 'eq':
      return fieldValue === criterion.value;
    case 'ne':
      return fieldValue !== criterion.value;
    case 'in':
      return Array.isArray(criterion.value) && criterion.value.includes(fieldValue);
    case 'nin':
      return Array.isArray(criterion.value) && !criterion.value.includes(fieldValue);
    case 'gt':
      return compareValues(fieldValue, criterion.value) > 0;
    case 'gte':
      return compareValues(fieldValue, criterion.value) >= 0;
    case 'lt':
      return compareValues(fieldValue, criterion.value) < 0;
    case 'lte':
      return compareValues(fieldValue, criterion.value) <= 0;
    case 'regex':
      return criterion.value instanceof RegExp && typeof fieldValue === 'string'
        ? criterion.value.test(fieldValue)
        : false;
    case 'exists':
      return criterion.value
        ? fieldValue !== undefined && fieldValue !== null
        : fieldValue === undefined || fieldValue === null;
    default:
      return true;
  }
}

function compareValues(left: unknown, right: unknown): number {
  if (typeof left === 'number' && typeof right === 'number') {
    return left - right;
  }
  if (typeof left === 'string' && typeof right === 'string') {
    return left.localeCompare(right);
  }
  if (left instanceof Date && right instanceof Date) {
    return left.getTime() - right.getTime();
  }
  return String(left).localeCompare(String(right));
}

export type SortDirection = 'asc' | 'desc';

/**
 * Resolves a user-facing sort key to a MongoDB sort document using an allow-list.
 *
 * @example
 * ```ts
 * const sort = resolveMongoSort(query.sort, {
 *   newest: { createdAt: -1, _id: -1 },
 *   oldest: { createdAt: 1, _id: 1 },
 * }, { createdAt: -1, _id: -1 });
 * ```
 */
export function resolveMongoSort(
  sortKey: string | undefined,
  allowList: Record<string, Record<string, 1 | -1>>,
  fallback: Record<string, 1 | -1>,
): Record<string, 1 | -1> {
  if (!sortKey) {
    return fallback;
  }
  return allowList[sortKey] ?? fallback;
}
