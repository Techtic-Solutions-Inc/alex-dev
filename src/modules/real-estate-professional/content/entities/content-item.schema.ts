import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';
import { User } from '../../../auth/entities/user.schema';

export type RealEstateContentItemDocument = HydratedDocument<RealEstateContentItem>;

@Schema({ collection: 'real_estate_professional_contents', timestamps: true, versionKey: false })
export class RealEstateContentItem {
  @Prop({ type: Types.ObjectId, ref: User.name, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, trim: true, maxlength: 160 })
  title!: string;

  @Prop({ required: true, trim: true, maxlength: 5000 })
  description!: string;

  @Prop({ required: true, trim: true, maxlength: 2048 })
  image_url!: string;

  @Prop({ type: String, trim: true, maxlength: 2048, default: null })
  link!: string | null;

  @Prop({ type: String, trim: true, maxlength: 100, default: null })
  city!: string | null;

  @Prop({ type: [String], default: [] })
  tags!: string[];

  @Prop({ required: true, trim: true, maxlength: 40 })
  phone!: string;

  @Prop({ required: true, default: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const RealEstateContentItemSchema = SchemaFactory.createForClass(RealEstateContentItem);

RealEstateContentItemSchema.index(
  { user_id: 1, title: 1, is_active: 1 },
  {
    unique: true,
    partialFilterExpression: { is_active: true },
    name: 'uniq_active_rep_content_title_per_user',
    collation: { locale: 'en', strength: 2 },
  },
);

RealEstateContentItemSchema.index({ title: 'text', description: 'text', tags: 'text', city: 'text' });