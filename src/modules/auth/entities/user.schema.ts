import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument } from 'mongoose';

export type UserDocument = HydratedDocument<User>;

@Schema({ collection: 'users', timestamps: true, versionKey: false })
export class User {
  @Prop({ required: true, trim: true, maxlength: 100 })
  first_name!: string;

  @Prop({ required: true, trim: true, maxlength: 100 })
  last_name!: string;

  @Prop({ required: true, trim: true, lowercase: true, maxlength: 254, unique: true })
  email!: string;

  @Prop({ required: true, select: false })
  password_hash!: string;

  @Prop({ required: true, default: false })
  terms_accepted!: boolean;

  @Prop({ required: true, default: false })
  email_verified!: boolean;

  @Prop({ required: true, default: true })
  is_active!: boolean;

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
