import { Injectable } from '@nestjs/common';
import { InjectConnection } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';

@Injectable()
export class HealthService {
  constructor(@InjectConnection() private readonly connection: Connection) {}

  assertDatabaseReady(): void {
    if (this.connection.readyState !== 1) {
      throw new HttpException('Database connection is unavailable', 503, 'DATABASE_UNAVAILABLE');
    }
  }
}
