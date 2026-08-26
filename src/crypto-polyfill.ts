import { webcrypto } from 'crypto';

/**
 * Node 18 CommonJS entrypoints do not expose the Web Crypto global.
 * The MongoDB driver calls crypto.getRandomValues() when opening sessions,
 * which otherwise throws ReferenceError and becomes HTTP 500 on every DB route.
 */
if (typeof globalThis.crypto === 'undefined' || typeof globalThis.crypto.getRandomValues !== 'function') {
  Object.defineProperty(globalThis, 'crypto', {
    value: webcrypto,
    configurable: true,
  });
}
