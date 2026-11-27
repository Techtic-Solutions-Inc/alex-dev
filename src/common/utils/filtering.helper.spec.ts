import {
  buildInMemoryPredicates,
  buildMongoFilter,
  buildTextSearchFilter,
  filterInMemory,
  mergeMongoFilters,
  resolveMongoSort,
} from './filtering.helper';

describe('filtering.helper', () => {
  it('test_filtering_success — builds MongoDB equality and range criteria', () => {
    const filter = buildMongoFilter(
      [
        { field: 'status', operator: 'eq', value: 'active' },
        { field: 'score', operator: 'gte', value: 10 },
      ],
      { allowedFields: ['status', 'score'] },
    );

    expect(filter).toEqual({
      status: 'active',
      score: { $gte: 10 },
    });
  });

  it('ignores fields outside the allow-list', () => {
    const filter = buildMongoFilter(
      [{ field: 'role', operator: 'eq', value: 'admin' }],
      { allowedFields: ['status'] },
    );
    expect(filter).toEqual({});
  });

  it('builds text search filters across fields', () => {
    const filter = buildTextSearchFilter('market', ['title', 'description']);
    expect(filter.$or).toHaveLength(2);
    expect((filter.$or as Record<string, RegExp>[])[0].title).toBeInstanceOf(RegExp);
  });

  it('merges base and search filters', () => {
    const merged = mergeMongoFilters({ is_active: true }, buildTextSearchFilter('blog', ['title']));
    expect(merged.is_active).toBe(true);
    expect(merged.$or).toBeDefined();
  });

  it('filters in-memory collections with the same operators', () => {
    const rows = [
      { status: 'active', score: 12 },
      { status: 'active', score: 4 },
      { status: 'archived', score: 20 },
    ];

    const filtered = filterInMemory(
      rows,
      [
        { field: 'status', operator: 'eq', value: 'active' },
        { field: 'score', operator: 'gte', value: 10 },
      ],
      { allowedFields: ['status', 'score'] },
    );

    expect(filtered).toEqual([{ status: 'active', score: 12 }]);
  });

  it('composes in-memory predicates', () => {
    const predicates = buildInMemoryPredicates(
      [{ field: 'status', operator: 'eq', value: 'active' }],
      { allowedFields: ['status'] },
    );
    expect(predicates[0]({ status: 'active' })).toBe(true);
    expect(predicates[0]({ status: 'draft' })).toBe(false);
  });

  it('resolves allow-listed MongoDB sort keys', () => {
    const fallback = { createdAt: -1 as const, _id: -1 as const };
    const allowList = { oldest: { createdAt: 1 as const, _id: 1 as const } };
    expect(resolveMongoSort('oldest', allowList, fallback)).toEqual({
      createdAt: 1,
      _id: 1,
    });
    expect(resolveMongoSort('unknown', allowList, fallback)).toEqual(fallback);
  });
});