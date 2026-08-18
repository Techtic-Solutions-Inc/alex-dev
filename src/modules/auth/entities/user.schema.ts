import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument } from 'mongoose';

export type UserDocument = HydratedDocument<User>;
export type UserRole = 'agent' | 'admin' | 'marketing_manager' | 'real_estate_professional';

@Schema({ collection: 'users', timestamps: true, versionKey: false })
export class User {
  @Prop({ required: true, trim: true, maxlength: 100 })
  first_name!: string;

  @Prop({ required: true, trim: true, maxlength: 100 })
  last_name!: string;

  @Prop({ required: true, trim: true, lowercase: true, maxlength: 254, unique: true })
  email!: string;

  @Prop({ type: String, trim: true, maxlength: 40, default: null })
  phone!: string | null;

  @Prop({ type: String, trim: true, maxlength: 40, default: null })
  mobile_number!: string | null;

  @Prop({ type: String, trim: true, maxlength: 500, default: null })
  bio!: string | null;

  @Prop({ type: String, trim: true, maxlength: 120, default: null })
  time_zone!: string | null;

  @Prop({ type: String, trim: true, maxlength: 200, default: null })
  street!: string | null;

  @Prop({ type: String, trim: true, maxlength: 100, default: null })
  country!: string | null;

  @Prop({ type: String, trim: true, maxlength: 100, default: null })
  state!: string | null;

  @Prop({ type: String, trim: true, maxlength: 100, default: null })
  city!: string | null;

  @Prop({ type: String, trim: true, maxlength: 20, default: null })
  zip!: string | null;

  @Prop({ type: String, trim: true, maxlength: 500, default: null })
  image!: string | null;

  @Prop({ type: String, trim: true, maxlength: 500, default: null })
  link!: string | null;

  @Prop({ type: String, trim: true, maxlength: 500, default: null })
  description!: string | null;

  @Prop({ required: true, select: false })
  password_hash!: string;

  @Prop({ required: true, default: false })
  terms_accepted!: boolean;

  @Prop({ required: true, default: false })
  email_verified!: boolean;

  @Prop({ required: true, default: true })
  is_active!: boolean;

  @Prop({
    required: true,
    trim: true,
    lowercase: true,
    enum: ['agent', 'admin', 'marketing_manager', 'real_estate_professional'],
    default: 'agent',
  })
  role!: UserRole;

  @Prop({ required: true, default: true })
  ai_generation_enabled!: boolean;

  @Prop({ required: true, default: 5000, min: 0 })
  ai_credits_total!: number;

  @Prop({ required: true, default: 0, min: 0 })
  ai_credits_used!: number;

  @Prop({ select: false })
  verification_token_hash?: string;

  @Prop()
  verification_token_expires_at?: Date;

  createdAt!: Date;
  updatedAt!: Date;
}

export const UserSchema = SchemaFactory.createForClass(User);
UserSchema.index(
  { email: 1 },
  {
    unique: true,
    name: 'uniq_users_email',
    collation: { locale: 'en', strength: 2 },
  },
);
UserSchema.index({ verification_token_hash: 1 }, { sparse: true });
