import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument } from 'mongoose';

export type RevokedAccessTokenDocument = HydratedDocument<RevokedAccessToken>;

@Schema({ collection: 'revoked_access_tokens', timestamps: { createdAt: true, updatedAt: false }, versionKey: false })
export class RevokedAccessToken {
  @Prop({ required: true, unique: true, index: true })
  token_hash!: string;

  @Prop({ required: true, trim: true })
  user_id!: string;

  @Prop({ required: true, index: true })
  expires_at!: Date;
}

export const RevokedAccessTokenSchema = SchemaFactory.createForClass(RevokedAccessToken);
RevokedAccessTokenSchema.index({ expires_at: 1 }, { expireAfterSeconds: 0, name: 'ttl_revoked_access_tokens' });