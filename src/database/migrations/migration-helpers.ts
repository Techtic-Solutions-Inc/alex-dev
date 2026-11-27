import { mongo } from 'mongoose';

type Db = mongo.Db;

export async function collectionExists(database: Db, name: string): Promise<boolean> {
  const collections = await database.listCollections({ name }, { nameOnly: true }).toArray();
  return collections.length > 0;
}

export async function ensureCollection(database: Db, name: string): Promise<void> {
  if (!(await collectionExists(database, name))) {
    await database.createCollection(name);
  }
}

export async function dropIndexIfExists(database: Db, collectionName: string, indexName: string): Promise<void> {
  try {
    await database.collection(collectionName).dropIndex(indexName);
  } catch (error) {
    if (!(error instanceof mongo.MongoServerError) || error.code !== 27) {
      throw error;
    }
  }
}
