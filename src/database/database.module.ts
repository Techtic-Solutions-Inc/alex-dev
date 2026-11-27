import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { MongooseModule } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import { resolveMongoConnectionOptions } from '../config/database-url.util';
import logger from '../common/services/logger.service';

@Module({
  imports: [
    ConfigModule,
    MongooseModule.forRootAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => {
        const databaseUrl =
          process.env.NODE_ENV === 'test'
            ? (process.env.DATABASE_URL ?? configService.getOrThrow<string>('DATABASE_URL'))
            : configService.getOrThrow<string>('DATABASE_URL');
        const { uri, dbName } = resolveMongoConnectionOptions(databaseUrl);

        return {
          uri,
          dbName,
          serverSelectionTimeoutMS: 5_000,
          bufferCommands: false,
          ...(process.env.NODE_ENV === 'test' ? { directConnection: true } : {}),
          onConnectionCreate: (connection: Connection) => {
            connection.on('error', (error: Error) => {
              logger.warn('MongoDB connection error', { message: error.message });
            });
          },
        };
      },
    }),
  ],
})
export class DatabaseModule {}
