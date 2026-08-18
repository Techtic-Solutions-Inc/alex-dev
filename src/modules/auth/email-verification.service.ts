import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as sgMail from '@sendgrid/mail';
import { HttpException } from '../../common/exceptions/http.exception';

@Injectable()
export class EmailVerificationService {
  private readonly logger = new Logger(EmailVerificationService.name);

  constructor(private readonly configService: ConfigService) {}

  async sendVerificationEmail(email: string, firstName: string, token: string): Promise<void> {
    const apiKey = this.configService.get<string>('SENDGRID_API_KEY');
    const sender = this.configService.get<string>('SENDGRID_FROM_EMAIL');
    const appUrl = this.configService.get<string>('EMAIL_VERIFICATION_URL');

    if (!apiKey || !sender || !appUrl) {
      throw new HttpException(
        'Email verification is temporarily unavailable. Please try again later.',
        500,
        'EMAIL_DELIVERY_UNAVAILABLE',
      );
    }

    let verificationUrl: URL;
    try {
      verificationUrl = new URL(appUrl);
      if (!['http:', 'https:'].includes(verificationUrl.protocol)) {
        throw new TypeError('Unsupported verification URL protocol');
      }
    } catch {
      this.logger.error('EMAIL_VERIFICATION_URL is invalid');
      throw new HttpException(
        'Email verification is temporarily unavailable. Please try again later.',
        500,
        'EMAIL_DELIVERY_UNAVAILABLE',
      );
    }

    verificationUrl.searchParams.set('token', token);
    sgMail.setApiKey(apiKey);

    try {
      await sgMail.send({
        to: email,
        from: sender,
        subject: 'Verify your email address',
        text: `Hello ${firstName}, verify your email address: ${verificationUrl.toString()}`,
        html: `<p>Hello ${this.escapeHtml(firstName)},</p><p><a href="${verificationUrl.toString()}">Verify your email address</a></p>`,
      });
    } catch {
      this.logger.error('SendGrid failed to send a verification email');
      throw new HttpException(
        'We could not send your verification email. Please try again.',
        500,
        'EMAIL_DELIVERY_FAILED',
      );
    }
  }

  private escapeHtml(value: string): string {
    return value.replace(/[&<>"']/g, (character) => {
      const entities: Record<string, string> = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
      };
      return entities[character] ?? character;
    });
  }
}
