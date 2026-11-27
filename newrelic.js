'use strict';

/**
 * New Relic Node agent configuration. Loaded when APM_ENABLED=true and
 * APM_PROVIDER=newrelic.
 */
exports.config = {
  app_name: [process.env.NEW_RELIC_APP_NAME || 'backend-api'],
  license_key: process.env.NEW_RELIC_LICENSE_KEY,
  logging: {
    level: process.env.NEW_RELIC_LOG_LEVEL || 'info',
  },
  distributed_tracing: {
    enabled: true,
  },
  application_logging: {
    forwarding: {
      enabled: true,
    },
    metrics: {
      enabled: true,
    },
  },
  attributes: {
    exclude: ['request.headers.authorization', 'request.headers.cookie', 'request.headers.set-cookie'],
  },
  allow_all_headers: false,
};