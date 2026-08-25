import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';
import { User } from '../../auth/entities/user.schema';

export type ContentCalendarEntryDocument = HydratedDocument<ContentCalendarEntry>;

@Schema({ collection: 'content_calendar_entries', timestamps: true, versionKey: false })
export class ContentCalendarEntry {
  @Prop({ type: Types.ObjectId, ref: User.name, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, trim: true, maxlength: 160 })
  title!: string;

  @Prop({ required: true, type: Date })
  date!: Date;

  @Prop({ required: true, trim: true, maxlength: 5000 })
  content!: string;

  @Prop({ required: true, trim: true, maxlength: 5000 })
  description!: string;

  @Prop({ required: true, trim: true, maxlength: 160 })
  full_name!: string;

  @Prop({ required: true, trim: true, maxlength: 40 })
  phone!: string;

  @Prop({ type: String, trim: true, maxlength: 2048, default: null })
  link!: string | null;

  @Prop({ required: true, default: true, index: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const ContentCalendarEntrySchema = SchemaFactory.createForClass(ContentCalendarEntry);

ContentCalendarEntrySchema.index(
  { user_id: 1, title: 1, date: 1, is_active: 1 },
  {
    unique: true,
    partialFilterExpression: { is_active: true },
    name: 'uniq_active_calendar_title_date_per_user',
    collation: { locale: 'en', strength: 2 },
  },
);
