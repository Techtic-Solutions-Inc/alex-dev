import { resolveSecuritySettings } from './security.config';
import { resolveTlsSettings } from './tls.config';

describe('resolveSecuritySettings', () => {
  it('enables trust proxy and HTTPS redirect defaults in production', () => {
    const settings = resolveSecuritySettings({ NODE_ENV: 'production' });
    expect(settings.trustProxy).toBe(true);
    expect(settings.forceHttps).toBe(true);
    expect(settings.hstsEnabled).toBe(false);
  });

  it('honours explicit TRUST_PROXY and SECURITY_HSTS_ENABLED flags', () => {
    const settings = resolveSecuritySettings({
      NODE_ENV: 'development',
      TRUST_PROXY: 'true',
      FORCE_HTTPS: 'false',
      SECURITY_HSTS_ENABLED: 'true',
      SECURITY_HSTS_MAX_AGE_SECONDS: '120',
    });

    expect(settings.trustProxy).toBe(true);
    expect(settings.forceHttps).toBe(false);
    expect(settings.hstsEnabled).toBe(true);
    expect(settings.hstsMaxAgeSeconds).toBe(120);
  });
});

describe('resolveTlsSettings', () => {
  it('enables TLS when certificate paths are configured', () => {
    const settings = resolveTlsSettings({
      SSL_CERT_PATH: '/etc/ssl/certs/api.crt',
      SSL_KEY_PATH: '/etc/ssl/private/api.key',
    });

    expect(settings.enabled).toBe(true);
    expect(settings.certPath).toBe('/etc/ssl/certs/api.crt');
    expect(settings.keyPath).toBe('/etc/ssl/private/api.key');
  });
});
