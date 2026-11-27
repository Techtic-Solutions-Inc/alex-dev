import { Injectable } from '@nestjs/common';
import { InjectConnection } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';

@Injectable()
export class HealthService {
  constructor(@InjectConnection() private readonly connection: Connection) {}

  async assertDatabaseReady(): Promise<void> {
    if (this.connection.readyState === 2) {
      await new Promise<void>((resolve, reject) => {
        const timeout = setTimeout(() => {
          reject(new HttpException('Database connection is unavailable', 503, 'DATABASE_UNAVAILABLE'));
        }, 10_000);

        this.connection.once('connected', () => {
          clearTimeout(timeout);
          resolve();
        });
        this.connection.once('error', () => {
          clearTimeout(timeout);
          reject(new HttpException('Database connection is unavailable', 503, 'DATABASE_UNAVAILABLE'));
        });
      });
    } else if (this.connection.readyState !== 1) {
      try {
        await this.connection.asPromise();
      } catch {
        throw new HttpException('Database connection is unavailable', 503, 'DATABASE_UNAVAILABLE');
      }
    }

    const database = this.connection.db;
    if (!database) {
      throw new HttpException('Database connection is unavailable', 503, 'DATABASE_UNAVAILABLE');
    }

    try {
      await database.admin().command({ ping: 1 });
    } catch {
      throw new HttpException('Database connection is unavailable', 503, 'DATABASE_UNAVAILABLE');
    }
  }
}
