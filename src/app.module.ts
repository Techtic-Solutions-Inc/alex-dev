import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { LoggerMiddleware } from './common/middleware/logger.middleware';
import { RateLimiterMiddleware } from './common/middleware/rate-limiter.middleware';
import { applyEnvDefaults } from './config/env.defaults';
import { DatabaseModule } from './database/database.module';
import { AuthModule } from './modules/auth/auth.module';
import { CalendarModule } from './modules/calendar/calendar.module';
import { ContentLibraryModule } from './modules/content-library/content-library.module';
import { DashboardModule } from './modules/dashboard/dashboard.module';
import { HealthModule } from './modules/health/health.module';
import { ProfileModule } from './modules/profile/profile.module';

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      cache: true,
      validate: (environment: Record<string, string | undefined>) => {
        const env = applyEnvDefaults(environment);
        const required = ['DATABASE_URL', 'JWT_SECRET'];
        for (const name of required) {
          if (!env[name]) {
            throw new Error(`Missing required environment variable: ${name}`);
          }
        }
        return env;
      },
    }),
    DatabaseModule,
    AuthModule,
    CalendarModule,
    ContentLibraryModule,
    DashboardModule,
    HealthModule,
    ProfileModule,
  ],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer.apply(LoggerMiddleware, RateLimiterMiddleware).forRoutes('*');
  }
}
