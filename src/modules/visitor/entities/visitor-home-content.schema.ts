import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument } from 'mongoose';

export type VisitorHomeContentDocument = HydratedDocument<VisitorHomeContent>;

@Schema({ collection: 'visitor_home_contents', timestamps: true, versionKey: false })
export class VisitorHomeContent {
  @Prop({ required: true, trim: true, maxlength: 160 })
  title!: string;

  @Prop({ required: true, trim: true, maxlength: 5000 })
  description!: string;

  @Prop({ required: true, trim: true, maxlength: 120, index: true })
  category!: string;

  @Prop({ type: [String], default: [] })
  tags!: string[];

  @Prop({ required: true, trim: true, maxlength: 2048 })
  image_url!: string;

  @Prop({ required: true, trim: true, maxlength: 2048 })
  link!: string;

  @Prop({ required: true, default: true, index: true })
  is_active!: boolean;

  createdAt!: Date;
  updatedAt!: Date;
}

export const VisitorHomeContentSchema = SchemaFactory.createForClass(VisitorHomeContent);

VisitorHomeContentSchema.index({ title: 'text', description: 'text', category: 'text', tags: 'text' });
