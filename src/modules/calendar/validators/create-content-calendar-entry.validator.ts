import { BadRequestException } from '@nestjs/common';
import { plainToInstance } from 'class-transformer';
import { validate, ValidationError } from 'class-validator';
import { CreateContentCalendarEntryDto } from '../dto/content-calendar.dto';

const validationDetails = (errors: ValidationError[]): Record<string, string[]> =>
  errors.reduce<Record<string, string[]>>((details, error) => {
    const messages = Object.values(error.constraints ?? {});
    if (messages.length > 0) {
      details[error.property] = messages;
    }
    if (error.children?.length) {
      Object.assign(details, validationDetails(error.children));
    }
    return details;
  }, {});

export async function validateCreateContentCalendarEntry(
  body: Record<string, unknown>,
): Promise<CreateContentCalendarEntryDto> {
  const dto = plainToInstance(CreateContentCalendarEntryDto, body);
  const errors = await validate(dto, {
    whitelist: true,
    forbidNonWhitelisted: true,
  });

  if (errors.length > 0) {
    throw new BadRequestException({
      message: 'Validation failed',
      errors: validationDetails(errors),
    });
  }

  return dto;
}
