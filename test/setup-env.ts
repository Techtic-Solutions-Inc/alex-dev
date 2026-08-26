import { webcrypto } from 'crypto';
import { config } from 'dotenv';
import { resolve } from 'path';

if (!globalThis.crypto) {
  Object.defineProperty(globalThis, 'crypto', { value: webcrypto });
}

config({ path: resolve(__dirname, '../.env.test'), override: true });

config({ path: resolve(__dirname, '../.env.test'), override: true });

jest.setTimeout(30_000);

process.env.JWT_SECRET ??= 'test-jwt-secret-at-least-32-characters-long';
process.env.JWT_EXPIRY ??= '3600';
process.env.JWT_REFRESH_EXPIRY ??= '86400';
process.env.EMAIL_VERIFICATION_URL ??= 'http://localhost:3000/api/auth/verify-email';
process.env.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS ??= '24';
process.env.RATE_LIMIT_POINTS = '100000';
process.env.RATE_LIMIT_DURATION ??= '1';
