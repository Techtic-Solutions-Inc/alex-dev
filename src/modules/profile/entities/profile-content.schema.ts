import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';

export type ProfileContentDocument = HydratedDocument<ProfileContent>;

@Schema({ collection: 'profile_contents', timestamps: true, versionKey: false })
export class ProfileContent {
  @Prop({ type: Types.ObjectId, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, trim: true, maxlength: 160 })
  title!: string;

  @Prop({ required: true, trim: true, maxlength: 2000 })
  description!: string;

  @Prop({ required: true, trim: true, maxlength: 160 })
  full_name!: string;

  @Prop({ required: true, trim: true, maxlength: 40 })
  phone!: string;

  @Prop({ type: String, trim: true, maxlength: 500, default: null })
  link!: string | null;

  @Prop({ required: true, default: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const ProfileContentSchema = SchemaFactory.createForClass(ProfileContent);

ProfileContentSchema.index({ user_id: 1, is_active: 1, updatedAt: -1 }, { name: 'idx_profile_contents_user_active_updated' });
