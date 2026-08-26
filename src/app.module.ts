import { MiddlewareConsumer, Module, NestModule } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { applyEnvDefaults } from './config/env.defaults';
import { databaseProviders } from './config/database.config';
import { LoggingMiddleware } from './middleware/logging.middleware';
import { RateLimiterMiddleware } from './middleware/rate-limiter.middleware';
import { AuthModule } from './modules/auth/auth.module';
import { CalendarModule } from './modules/calendar/calendar.module';
import { ContentLibraryModule } from './modules/content-library/content-library.module';
import { DashboardModule } from './modules/dashboard/dashboard.module';
import { HealthModule } from './modules/health/health.module';
import { ProfileModule } from './modules/profile/profile.module';
import { VisitorModule } from './modules/visitor/visitor.module';

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
    ...databaseProviders,
    AuthModule,
    CalendarModule,
    ContentLibraryModule,
    DashboardModule,
    HealthModule,
    ProfileModule,
    VisitorModule,
  ],
})
export class AppModule implements NestModule {
  configure(consumer: MiddlewareConsumer): void {
    consumer.apply(LoggingMiddleware, RateLimiterMiddleware).forRoutes('*');
  }
}
