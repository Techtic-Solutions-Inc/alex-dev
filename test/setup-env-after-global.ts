import { readFileSync } from 'fs';
import { join } from 'path';

/**
 * Jest runs globalSetup in a separate process; worker processes load the URI from disk.
 */
const mongoStatePath = join(__dirname, '.mongo-test-state.json');

try {
  const state = JSON.parse(readFileSync(mongoStatePath, 'utf8')) as { uri: string };
  process.env.DATABASE_URL = state.uri;
  process.env.MIGRATIONS_DATABASE_URL = state.uri;
} catch {
  // setup-env.ts will throw if still missing.
}
