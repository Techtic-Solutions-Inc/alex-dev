import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';

export type ProfileDownloadDocument = HydratedDocument<ProfileDownload>;

@Schema({ collection: 'profile_downloads', timestamps: true, versionKey: false })
export class ProfileDownload {
  @Prop({ type: Types.ObjectId, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, trim: true, maxlength: 200 })
  title!: string;

  @Prop({ required: true, trim: true, maxlength: 50 })
  file_type!: string;

  @Prop({ required: true, trim: true, maxlength: 50 })
  file_size!: string;

  @Prop({ required: true })
  last_downloaded_at!: Date;

  @Prop({ type: String, trim: true, maxlength: 500, default: null })
  link!: string | null;

  @Prop({ type: String, trim: true, maxlength: 500, default: null })
  description!: string | null;

  @Prop({ required: true, default: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const ProfileDownloadSchema = SchemaFactory.createForClass(ProfileDownload);
ProfileDownloadSchema.index(
  { user_id: 1, is_active: 1, last_downloaded_at: -1 },
  { name: 'idx_profile_downloads_user_active_last_downloaded' },
);
