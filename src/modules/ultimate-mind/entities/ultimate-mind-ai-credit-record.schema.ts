import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';
import { User } from '../../auth/entities/user.schema';

export type UltimateMindAiCreditRecordDocument = HydratedDocument<UltimateMindAiCreditRecord>;

@Schema({ collection: 'ultimate_mind_ai_credit_records', timestamps: true, versionKey: false })
export class UltimateMindAiCreditRecord {
  @Prop({ type: Types.ObjectId, ref: User.name, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, min: 0 })
  usage!: number;

  @Prop({ required: true, min: 1 })
  limit!: number;

  @Prop({ required: true, trim: true, maxlength: 160 })
  full_name!: string;

  @Prop({ required: true, trim: true, maxlength: 40 })
  phone!: string;

  @Prop({ required: true, default: true, index: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const UltimateMindAiCreditRecordSchema = SchemaFactory.createForClass(UltimateMindAiCreditRecord);

UltimateMindAiCreditRecordSchema.index(
  { user_id: 1, is_active: 1 },
  {
    unique: true,
    partialFilterExpression: { is_active: true },
    name: 'uniq_active_ultimate_mind_ai_credit_per_user',
  },
);
