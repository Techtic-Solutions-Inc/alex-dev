/**
 * Shared validation helpers returning `true` when a value passes checks, otherwise `false`.
 * Use inside services, guards, or custom pipes; DTO class-validator decorators remain the primary HTTP validation layer.
 *
 * @example
 * ```ts
 * if (!isValidEmail(payload.email)) {
 *   throw new HttpException('Validation failed', 400, 'VALIDATION_ERROR', { email: ['Invalid email'] });
 * }
 * ```
 */

const EMAIL_PATTERN =
  /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$/;

const PHONE_PATTERN = /^\+?[0-9][0-9\s\-().]{6,24}$/;

const STRONG_PASSWORD_PATTERN = /^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

const OBJECT_ID_PATTERN = /^[a-fA-F0-9]{24}$/;

const URL_PATTERN = /^https?:\/\/[^\s/$.?#].[^\s]*$/i;

export interface NonEmptyStringOptions {
  minLength?: number;
  maxLength?: number;
  /** When true (default), trims whitespace before measuring length. */
  trim?: boolean;
}

export interface NumberValidationOptions {
  /** Require a finite integer (no decimals). */
  integer?: boolean;
  min?: number;
  max?: number;
}

/**
 * Returns `true` when `value` is a non-empty string within optional length bounds.
 */
export function isNonEmptyString(value: unknown, options: NonEmptyStringOptions = {}): boolean {
  if (typeof value !== 'string') {
    return false;
  }

  const trim = options.trim ?? true;
  const candidate = trim ? value.trim() : value;
  if (candidate.length === 0) {
    return false;
  }

  if (options.minLength !== undefined && candidate.length < options.minLength) {
    return false;
  }

  if (options.maxLength !== undefined && candidate.length > options.maxLength) {
    return false;
  }

  return true;
}

/**
 * Returns `true` when `value` is a finite number within optional bounds.
 */
export function isValidNumber(value: unknown, options: NumberValidationOptions = {}): boolean {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return false;
  }

  if (options.integer === true && !Number.isInteger(value)) {
    return false;
  }

  if (options.min !== undefined && value < options.min) {
    return false;
  }

  if (options.max !== undefined && value > options.max) {
    return false;
  }

  return true;
}

/**
 * Returns `true` for RFC 5322–style email addresses (simplified, max 254 chars).
 */
export function isValidEmail(value: unknown): boolean {
  if (typeof value !== 'string') {
    return false;
  }

  const normalized = value.trim().toLowerCase();
  return normalized.length > 0 && normalized.length <= 254 && EMAIL_PATTERN.test(normalized);
}

/**
 * Returns `true` for international phone strings matching API DTO rules.
 */
export function isValidPhone(value: unknown): boolean {
  if (typeof value !== 'string') {
    return false;
  }
  return PHONE_PATTERN.test(value.trim());
}

/**
 * Returns `true` when `value` matches the application's strong-password policy.
 */
export function isStrongPassword(value: unknown): boolean {
  if (typeof value !== 'string') {
    return false;
  }
  return STRONG_PASSWORD_PATTERN.test(value);
}

/**
 * Returns `true` for absolute `http` or `https` URLs.
 */
export function isValidUrl(value: unknown): boolean {
  if (typeof value !== 'string') {
    return false;
  }
  const candidate = value.trim();
  if (candidate.length === 0) {
    return false;
  }
  try {
    const parsed = new URL(candidate);
    return (parsed.protocol === 'http:' || parsed.protocol === 'https:') && URL_PATTERN.test(candidate);
  } catch {
    return false;
  }
}

/**
 * Returns `true` when `value` is a 24-character hexadecimal MongoDB ObjectId string.
 */
export function isValidObjectId(value: unknown): boolean {
  if (typeof value !== 'string') {
    return false;
  }
  return OBJECT_ID_PATTERN.test(value.trim());
}

/**
 * Returns `true` when `value` is a boolean (not truthy/falsy coercion).
 */
export function isValidBoolean(value: unknown): boolean {
  return typeof value === 'boolean';
}