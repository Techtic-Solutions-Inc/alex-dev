import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';
import { User } from '../../../auth/entities/user.schema';

export type RealEstateBlogPostDocument = HydratedDocument<RealEstateBlogPost>;

@Schema({ collection: 'real_estate_professional_blogs', timestamps: true, versionKey: false })
export class RealEstateBlogPost {
  @Prop({ type: Types.ObjectId, ref: User.name, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, trim: true, maxlength: 200 })
  title!: string;

  @Prop({ required: true, trim: true, lowercase: true, maxlength: 320 })
  author_email!: string;

  @Prop({ required: true, trim: true, maxlength: 100000 })
  content!: string;

  @Prop({ required: true, trim: true, maxlength: 2000 })
  description!: string;

  @Prop({ type: String, trim: true, maxlength: 2048, default: null })
  link!: string | null;

  @Prop({ required: true, trim: true, maxlength: 2048 })
  image_url!: string;

  @Prop({ required: true, trim: true, maxlength: 40 })
  phone!: string;

  @Prop({ required: true, default: true })
  terms_accepted!: boolean;

  @Prop({ required: true, default: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const RealEstateBlogPostSchema = SchemaFactory.createForClass(RealEstateBlogPost);

RealEstateBlogPostSchema.index(
  { user_id: 1, title: 1, is_active: 1 },
  {
    unique: true,
    partialFilterExpression: { is_active: true },
    name: 'uniq_active_rep_blog_title_per_user',
    collation: { locale: 'en', strength: 2 },
  },
);

RealEstateBlogPostSchema.index({ title: 'text', description: 'text', content: 'text' });
RealEstateBlogPostSchema.index({ createdAt: -1, _id: -1 });