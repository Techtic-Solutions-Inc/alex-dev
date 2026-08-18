import { ConfigService } from '@nestjs/config';
import { MongooseModule } from '@nestjs/mongoose';

export const databaseProviders = [
  MongooseModule.forRootAsync({
    useFactory: (configService: ConfigService) => ({
      uri: configService.getOrThrow<string>('DATABASE_URL'),
      serverSelectionTimeoutMS: 5_000,
    }),
    inject: [ConfigService],
  }),
];
