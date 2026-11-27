# Validation utilities

Location: `src/common/utils/validation.util.ts`

Boolean helpers for reusable checks outside (or alongside) class-validator DTOs. Each function returns `true` when valid, `false` otherwise — no exceptions are thrown from the helpers themselves.

| Function | Purpose |
| --- | --- |
| `isNonEmptyString(value, options?)` | Non-empty string with optional `minLength` / `maxLength` |
| `isValidNumber(value, options?)` | Finite number; optional integer-only and min/max |
| `isValidEmail(value)` | Email format (≤ 254 chars, lowercases for check) |
| `isValidPhone(value)` | Phone pattern aligned with sign-up DTOs |
| `isStrongPassword(value)` | Password complexity aligned with auth sign-up |
| `isValidUrl(value)` | `http` / `https` absolute URLs |
| `isValidObjectId(value)` | MongoDB ObjectId hex string |
| `isValidBoolean(value)` | Strict `boolean` type (no coercion) |

## Example

```typescript
import { isValidEmail, isNonEmptyString } from '../common/utils/validation.util';

if (!isNonEmptyString(dto.first_name, { maxLength: 100 })) {
  // map to HttpException / VALIDATION_ERROR in the service layer
}
```

Unit tests: `src/common/utils/validation.util.spec.ts`.