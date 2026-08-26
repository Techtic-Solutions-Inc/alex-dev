import { ArgumentMetadata, Injectable, PipeTransform } from '@nestjs/common';

/**
 * Copies Home-screen aliases onto Figma fields before class-validator runs.
 * class-transformer only transforms keys present in the JSON body, so first_name/last_name
 * and phone_number must be materialized onto full_name and phone first.
 */
@Injectable()
export class VisitorHomeAliasPipe implements PipeTransform {
  /**
   * Returns a shallow-copied body with full_name and phone filled from aliases when omitted.
   */
  transform(value: unknown, _metadata: ArgumentMetadata): unknown {
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
      return value;
    }

    const body = { ...(value as Record<string, unknown>) };
    const fullName = typeof body.full_name === 'string' ? body.full_name.trim() : '';
    if (!fullName) {
      const first = typeof body.first_name === 'string' ? body.first_name.trim() : '';
      const last = typeof body.last_name === 'string' ? body.last_name.trim() : '';
      const composed = `${first} ${last}`.trim();
      if (composed) {
        body.full_name = composed;
      }
    }

    const phone = typeof body.phone === 'string' ? body.phone.trim() : '';
    if (!phone && typeof body.phone_number === 'string' && body.phone_number.trim()) {
      body.phone = body.phone_number.trim();
    }

    return body;
  }
}
