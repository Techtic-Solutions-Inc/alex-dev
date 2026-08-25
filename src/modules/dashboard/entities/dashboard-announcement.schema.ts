import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';
import { User } from '../../auth/entities/user.schema';

export type DashboardAnnouncementDocument = HydratedDocument<DashboardAnnouncement>;

@Schema({ collection: 'dashboard_announcements', timestamps: true, versionKey: false })
export class DashboardAnnouncement {
  @Prop({ type: Types.ObjectId, ref: User.name, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, trim: true, maxlength: 160 })
  announcement_title!: string;

  @Prop({ required: true, trim: true, maxlength: 5000 })
  announcement_content!: string;

  @Prop({ required: true, trim: true, maxlength: 160 })
  full_name!: string;

  @Prop({ required: true, trim: true, lowercase: true, maxlength: 254 })
  email!: string;

  @Prop({ required: true, trim: true, maxlength: 40 })
  phone!: string;

  @Prop({ type: String, trim: true, maxlength: 2048, default: null })
  link!: string | null;

  @Prop({ required: true, trim: true, default: 'active', maxlength: 40 })
  status!: string;

  createdAt!: Date;
  updatedAt!: Date;
}

export const DashboardAnnouncementSchema = SchemaFactory.createForClass(DashboardAnnouncement);

DashboardAnnouncementSchema.index(
  { user_id: 1, announcement_title: 1 },
  {
    unique: true,
    name: 'uniq_dashboard_announcement_title_per_user',
    collation: { locale: 'en', strength: 2 },
  },
);
