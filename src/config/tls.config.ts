import { readFileSync } from 'fs';
import { resolve } from 'path';
import type { HttpsOptions } from '@nestjs/common/interfaces/external/https-options.interface';

export interface TlsSettings {
  enabled: boolean;
  certPath: string | null;
  keyPath: string | null;
  caPath: string | null;
}

const truthy = (value: string | undefined): boolean => {
  if (!value) {
    return false;
  }
  const normalized = value.trim().toLowerCase();
  return normalized === '1' || normalized === 'true' || normalized === 'yes' || normalized === 'on';
};

const resolveExistingPath = (rawPath: string | undefined): string | null => {
  if (typeof rawPath !== 'string' || rawPath.trim().length === 0) {
    return null;
  }
  const absolutePath = resolve(rawPath.trim());
  try {
    readFileSync(absolutePath);
    return absolutePath;
  } catch {
    throw new Error(`TLS file not found or unreadable: ${absolutePath}`);
  }
};

export const resolveTlsSettings = (environment: Record<string, string | undefined>): TlsSettings => {
  const certPath = environment.SSL_CERT_PATH?.trim() || null;
  const keyPath = environment.SSL_KEY_PATH?.trim() || null;
  const caPath = environment.SSL_CA_PATH?.trim() || null;
  const explicit = truthy(environment.TLS_ENABLED);
  const inferred = Boolean(certPath && keyPath);

  return {
    enabled: explicit || inferred,
    certPath,
    keyPath,
    caPath,
  };
};

export const buildHttpsOptions = (environment: Record<string, string | undefined>): HttpsOptions | undefined => {
  const settings = resolveTlsSettings(environment);
  if (!settings.enabled) {
    return undefined;
  }

  if (!settings.certPath || !settings.keyPath) {
    throw new Error('TLS is enabled but SSL_CERT_PATH and SSL_KEY_PATH must both be set.');
  }

  const certFile = resolveExistingPath(settings.certPath);
  const keyFile = resolveExistingPath(settings.keyPath);
  const options: HttpsOptions = {
    cert: readFileSync(certFile as string),
    key: readFileSync(keyFile as string),
  };

  if (settings.caPath) {
    const caFile = resolveExistingPath(settings.caPath);
    options.ca = readFileSync(caFile as string);
  }

  return options;
};