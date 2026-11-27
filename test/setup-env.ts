/**
 * Runs before each e2e test file (Jest setupFiles).
 * DATABASE_URL is injected by test/global-setup.ts via mongodb-memory-server.
 */
process.env.LOG_LEVEL = 'silent';
process.env.JWT_SECRET = process.env.JWT_SECRET ?? 'test-jwt-secret-at-least-32-characters-long-for-ci';
process.env.JWT_EXPIRY = process.env.JWT_EXPIRY ?? '3600';
process.env.JWT_REFRESH_EXPIRY = process.env.JWT_REFRESH_EXPIRY ?? '86400';
process.env.EMAIL_VERIFICATION_URL =
  process.env.EMAIL_VERIFICATION_URL ?? 'http://localhost:3000/api/v1/auth/verify-email';
process.env.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS = process.env.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS ?? '24';
process.env.RATE_LIMIT_POINTS = process.env.RATE_LIMIT_POINTS ?? '100000';
process.env.RATE_LIMIT_DURATION = process.env.RATE_LIMIT_DURATION ?? '1';
process.env.CORS_ORIGIN = process.env.CORS_ORIGIN ?? 'http://localhost:3000';
process.env.AUTH0_DOMAIN = process.env.AUTH0_DOMAIN ?? '';
process.env.AUTH0_CLIENT_ID = process.env.AUTH0_CLIENT_ID ?? '';
process.env.AUTH0_CLIENT_SECRET = process.env.AUTH0_CLIENT_SECRET ?? '';

if (!process.env.DATABASE_URL) {
  throw new Error(
    'DATABASE_URL is not set. Ensure jest e2e project uses test/global-setup.ts (mongodb-memory-server).',
  );
}
