import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { ApmModule } from './common/apm/apm.module';
import { LoggerMiddleware } from './common/middleware/logger.middleware';
import { RateLimiterMiddleware } from './common/middleware/rate-limiter.middleware';
import { applyEnvDefaults } from './config/env.defaults';
import { requireMongoDatabaseName } from './config/database-url.util';
import { DatabaseModule } from './database/database.module';
import { AuthModule } from './modules/auth/auth.module';
import { CalendarModule } from './modules/calendar/calendar.module';
import { ContentLibraryModule } from './modules/content-library/content-library.module';
import { DashboardModule } from './modules/dashboard/dashboard.module';
import { HealthModule } from './modules/health/health.module';
import { ProfileModule } from './modules/profile/profile.module';
import { RealEstateProfessionalModule } from './modules/real-estate-professional/real-estate-professional.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      cache: true,
      ignoreEnvFile: process.env.NODE_ENV === 'test',
      validate: (environment: Record<string, string | undefined>) => {
        const env = applyEnvDefaults(environment);
        const required = ['DATABASE_URL', 'JWT_SECRET'];
        for (const name of required) {
          if (!env[name]) {
            throw new Error(`Missing required environment variable: ${name}`);
          }
        }
        requireMongoDatabaseName(env.DATABASE_URL as string);
        return env;
      },
    }),
    ApmModule,
    DatabaseModule,
    AuthModule,
    CalendarModule,
    ContentLibraryModule,
    DashboardModule,
    HealthModule,
    ProfileModule,
    RealEstateProfessionalModule,
  ],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer.apply(LoggerMiddleware, RateLimiterMiddleware).forRoutes('*');
  }
}
