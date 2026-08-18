import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument, Types } from 'mongoose';
import { User } from '../../auth/entities/user.schema';

export type ContentLibraryItemDocument = HydratedDocument<ContentLibraryItem>;

@Schema({ collection: 'content_library_items', timestamps: true, versionKey: false })
export class ContentLibraryItem {
  @Prop({ type: Types.ObjectId, ref: User.name, required: true, index: true })
  user_id!: Types.ObjectId;

  @Prop({ required: true, trim: true, maxlength: 160 })
  title!: string;

  @Prop({ required: true, trim: true, maxlength: 5000 })
  description!: string;

  @Prop({ required: true, trim: true, maxlength: 2048 })
  image_url!: string;

  @Prop({ required: true, trim: true, maxlength: 2048 })
  link!: string;

  @Prop({ required: true, trim: true, maxlength: 120, index: true })
  category!: string;

  @Prop({ type: [String], default: [] })
  tags!: string[];

  @Prop({ required: true, trim: true, maxlength: 160 })
  full_name!: string;

  @Prop({ required: true, trim: true, maxlength: 40 })
  phone!: string;

  @Prop({ required: true, default: true, index: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const ContentLibraryItemSchema = SchemaFactory.createForClass(ContentLibraryItem);

ContentLibraryItemSchema.index(
  { user_id: 1, title: 1, category: 1, is_active: 1 },
  {
    unique: true,
    partialFilterExpression: { is_active: true },
    name: 'uniq_active_content_library_title_category_per_user',
    collation: { locale: 'en', strength: 2 },
  },
);

ContentLibraryItemSchema.index({ title: 'text', description: 'text', category: 'text', tags: 'text' });
