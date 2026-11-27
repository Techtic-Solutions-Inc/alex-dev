import { Module } from '@nestjs/common';
import { AuthModule } from '../auth/auth.module';
import { VisitorSignupController } from './signup.controller';
import { VisitorSignupService } from './signup.service';

@Module({
  imports: [AuthModule],
  controllers: [VisitorSignupController],
  providers: [VisitorSignupService],
})
export class VisitorModule {}
