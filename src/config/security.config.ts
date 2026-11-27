export interface SecuritySettings {
  trustProxy: boolean;
  forceHttps: boolean;
  hstsEnabled: boolean;
  hstsMaxAgeSeconds: number;
}

const truthy = (value: string | undefined): boolean => {
  if (!value) {
    return false;
  }
  const normalized = value.trim().toLowerCase();
  return normalized === '1' || normalized === 'true' || normalized === 'yes' || normalized === 'on';
};

const positiveInteger = (value: string | undefined, fallback: number): number => {
  if (!value || !/^\d+$/.test(value.trim())) {
    return fallback;
  }
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : fallback;
};

export const resolveSecuritySettings = (environment: Record<string, string | undefined>): SecuritySettings => {
  const nodeEnv = environment.NODE_ENV?.trim() ?? 'development';
  const trustProxyDefault = nodeEnv === 'production' || nodeEnv === 'staging';

  return {
    trustProxy: truthy(environment.TRUST_PROXY) || (environment.TRUST_PROXY === undefined && trustProxyDefault),
    forceHttps: truthy(environment.FORCE_HTTPS) || nodeEnv === 'production',
    hstsEnabled: truthy(environment.SECURITY_HSTS_ENABLED),
    hstsMaxAgeSeconds: positiveInteger(environment.SECURITY_HSTS_MAX_AGE_SECONDS, 31_536_000),
  };
};