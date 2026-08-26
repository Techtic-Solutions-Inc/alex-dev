import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument } from 'mongoose';

export type VisitorHomeSubscriptionDocument = HydratedDocument<VisitorHomeSubscription>;

@Schema({ collection: 'visitor_home_subscriptions', timestamps: true, versionKey: false })
export class VisitorHomeSubscription {
  @Prop({ required: true, trim: true, maxlength: 160, default: '' })
  full_name!: string;

  @Prop({ type: String, trim: true, maxlength: 100, default: null })
  first_name!: string | null;

  @Prop({ type: String, trim: true, maxlength: 100, default: null })
  last_name!: string | null;

  @Prop({ required: true, trim: true, lowercase: true, maxlength: 254 })
  email!: string;

  @Prop({ type: String, trim: true, maxlength: 40, default: null })
  phone!: string | null;

  @Prop({ required: true, default: false })
  terms_accepted!: boolean;

  @Prop({ required: true, default: false })
  subscribed!: boolean;

  @Prop({ type: Date, default: null })
  terms_accepted_at!: Date | null;

  @Prop({ type: Date, default: null })
  subscribed_at!: Date | null;

  createdAt!: Date;
  updatedAt!: Date;
}

export const VisitorHomeSubscriptionSchema = SchemaFactory.createForClass(VisitorHomeSubscription);

VisitorHomeSubscriptionSchema.index(
  { email: 1 },
  {
    unique: true,
    name: 'uniq_visitor_home_subscriptions_email',
    collation: { locale: 'en', strength: 2 },
  },
);
