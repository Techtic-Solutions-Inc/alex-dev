import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { MongooseModule } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import logger from '../common/services/logger.service';

@Module({
  imports: [
    ConfigModule,
    MongooseModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        uri: configService.getOrThrow<string>('DATABASE_URL'),
        serverSelectionTimeoutMS: 5_000,
        lazyConnection: true,
        onConnectionCreate: (connection: Connection) => {
          connection.on('error', (error: Error) => {
            logger.warn('MongoDB connection error', { message: error.message });
          });
          void connection.asPromise().catch((error: Error) => {
            logger.warn('MongoDB is not connected yet', { message: error.message });
          });
        },
      }),
    }),
  ],
})
export class DatabaseModule {}
