import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { AuthModule } from '../auth/auth.module';
import { User, UserSchema } from '../auth/entities/user.schema';
import {
  UltimateMindAiCreditRecord,
  UltimateMindAiCreditRecordSchema,
} from './entities/ultimate-mind-ai-credit-record.schema';
import { UltimateMindController } from './ultimate-mind.controller';
import { UltimateMindService } from './ultimate-mind.service';

@Module({
  imports: [
    AuthModule,
    MongooseModule.forFeature([
      { name: User.name, schema: UserSchema },
      { name: UltimateMindAiCreditRecord.name, schema: UltimateMindAiCreditRecordSchema },
    ]),
  ],
  controllers: [UltimateMindController],
  providers: [UltimateMindService, JwtAuthGuard],
  exports: [UltimateMindService],
})
export class UltimateMindModule {}
