const DATABASE_NAME_PATTERN = /^mongodb(?:\+srv)?:\/\/[^/]+\/([^/?]+)/i;

export function requireMongoDatabaseName(databaseUrl: string): string {
  const trimmed = databaseUrl.trim();
  const match = trimmed.match(DATABASE_NAME_PATTERN);
  const dbName = match?.[1]?.trim();

  if (!dbName) {
    throw new Error('DATABASE_URL must include a database name (for example mongodb://localhost:27017/alex-dev).');
  }

  return dbName;
}

export function resolveMongoConnectionOptions(databaseUrl: string): { uri: string; dbName: string } {
  const uri = databaseUrl.trim();
  return {
    uri,
    dbName: requireMongoDatabaseName(uri),
  };
}
