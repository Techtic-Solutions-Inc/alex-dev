# Rate limiting middleware

The API applies global rate limiting through `RateLimiterMiddleware`, registered in `AppModule` for all routes.

## Configuration

| Environment variable | Description | Default |
| --- | --- | --- |
| `RATE_LIMIT_POINTS` | Maximum requests allowed per client within one window | `5` (see `env.defaults` in non-production) |
| `RATE_LIMIT_DURATION` | Window length in seconds | `1` |
| `RATE_LIMIT_STRATEGY` | `fixed` or `sliding` | `fixed` |

- **Fixed window**: counters reset on a fixed schedule (`rate-limiter-flexible` in-memory store).
- **Sliding window**: only requests in the last `RATE_LIMIT_DURATION` seconds count toward the limit.

## Client identity

- Requests with a valid Bearer access JWT are limited **per user** (`sub` claim).
- Unauthenticated or invalid-token requests are limited **per IP address**.

## Response when limited

HTTP `429 Too Many Requests` with the standard API envelope:

```json
{
  "success": false,
  "message": "Too many requests. Please try again shortly.",
  "error": { "code": "RATE_LIMITED", "details": null }
}
```

When the limiter can compute a retry delay, the `Retry-After` header is set (seconds).

## Integration

No per-route setup is required. To change limits for an environment, set the variables above in the deployment config map or `.env` (see `.env.example`).