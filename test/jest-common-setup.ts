/**
 * Shared Jest setup (unit + e2e): hermetic env, no external Mongo/Redis, quiet logs in CI.
 */
process.env.NODE_ENV = 'test';
process.env.LOG_LEVEL = 'silent';
process.env.JWT_SECRET = process.env.JWT_SECRET ?? 'test-jwt-secret-at-least-32-characters-long-for-ci';
process.env.JWT_EXPIRY = process.env.JWT_EXPIRY ?? '3600';
process.env.JWT_REFRESH_EXPIRY = process.env.JWT_REFRESH_EXPIRY ?? '86400';
