import {
  isNonEmptyString,
  isStrongPassword,
  isValidBoolean,
  isValidEmail,
  isValidNumber,
  isValidObjectId,
  isValidPhone,
  isValidUrl,
} from './validation.util';

describe('validation.util', () => {
  describe('isNonEmptyString', () => {
    it('accepts trimmed non-empty strings within bounds', () => {
      expect(isNonEmptyString('John', { minLength: 1, maxLength: 10 })).toBe(true);
      expect(isNonEmptyString('  Jane  ', { trim: true })).toBe(true);
    });

    it('rejects empty, non-string, or out-of-range values', () => {
      expect(isNonEmptyString('   ')).toBe(false);
      expect(isNonEmptyString(null)).toBe(false);
      expect(isNonEmptyString('ab', { minLength: 3 })).toBe(false);
      expect(isNonEmptyString('abcdefghijk', { maxLength: 5 })).toBe(false);
    });
  });

  describe('isValidNumber', () => {
    it('accepts finite numbers within optional bounds', () => {
      expect(isValidNumber(10, { min: 1, max: 100 })).toBe(true);
      expect(isValidNumber(42, { integer: true })).toBe(true);
    });

    it('rejects NaN, non-numbers, and out-of-range values', () => {
      expect(isValidNumber(Number.NaN)).toBe(false);
      expect(isValidNumber('10' as unknown as number)).toBe(false);
      expect(isValidNumber(1.5, { integer: true })).toBe(false);
      expect(isValidNumber(0, { min: 1 })).toBe(false);
    });
  });

  describe('isValidEmail', () => {
    it('accepts well-formed emails', () => {
      expect(isValidEmail('john.doe@example.com')).toBe(true);
      expect(isValidEmail('  JOHN@EXAMPLE.COM  ')).toBe(true);
    });

    it('rejects invalid email shapes', () => {
      expect(isValidEmail('not-an-email')).toBe(false);
      expect(isValidEmail('')).toBe(false);
      expect(isValidEmail(123)).toBe(false);
    });
  });

  describe('isValidPhone', () => {
    it('accepts API-compliant phone numbers', () => {
      expect(isValidPhone('+1-555-0100')).toBe(true);
    });

    it('rejects malformed phone numbers', () => {
      expect(isValidPhone('abc')).toBe(false);
      expect(isValidPhone('123')).toBe(false);
    });
  });

  describe('isStrongPassword', () => {
    it('accepts passwords meeting complexity rules', () => {
      expect(isStrongPassword('StrongPassword123!')).toBe(true);
    });

    it('rejects weak passwords', () => {
      expect(isStrongPassword('weak')).toBe(false);
      expect(isStrongPassword('MissingSpecial1')).toBe(false);
    });
  });

  describe('isValidUrl', () => {
    it('accepts http and https URLs', () => {
      expect(isValidUrl('https://example.com/path')).toBe(true);
    });

    it('rejects invalid URLs', () => {
      expect(isValidUrl('not a url')).toBe(false);
      expect(isValidUrl('ftp://example.com')).toBe(false);
    });
  });

  describe('isValidObjectId', () => {
    it('accepts 24-character hex strings', () => {
      expect(isValidObjectId('66df0b7814b3e891e4ebcd21')).toBe(true);
    });

    it('rejects invalid object ids', () => {
      expect(isValidObjectId('not-an-id')).toBe(false);
      expect(isValidObjectId('66df0b7814b3e891e4ebcd2')).toBe(false);
    });
  });

  describe('isValidBoolean', () => {
    it('returns true only for boolean primitives', () => {
      expect(isValidBoolean(true)).toBe(true);
      expect(isValidBoolean(false)).toBe(true);
      expect(isValidBoolean('true')).toBe(false);
      expect(isValidBoolean(1)).toBe(false);
    });
  });
});