export function applyEnvDefaults(environment: Record<string, string | undefined>): Record<string, string | undefined> {
  const env = { ...environment };

  env.DATABASE_URL ??= env.MONGODB_URI ?? env.MONGO_URI;

  if (env.NODE_ENV !== 'production') {
    env.JWT_SECRET ??= 'dev-jwt-secret-at-least-32-characters-long';
    env.JWT_EXPIRY ??= '3600';
    env.JWT_REFRESH_EXPIRY ??= '86400';
    env.EMAIL_VERIFICATION_URL ??= 'http://localhost:3000/api/auth/verify-email';
    env.EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS ??= '24';
    env.RATE_LIMIT_POINTS ??= '1000';
    env.RATE_LIMIT_DURATION ??= '1';

    const rateLimitPoints = Number(env.RATE_LIMIT_POINTS);
    if (!Number.isInteger(rateLimitPoints) || rateLimitPoints < 100) {
      env.RATE_LIMIT_POINTS = '100000';
    }
  }

  env.GOOGLE_ANALYTICS_MEASUREMENT_ID ??= env.GA_MEASUREMENT_ID;
  env.GOOGLE_ANALYTICS_API_SECRET ??= env.GA_API_SECRET;

  return env;
}
