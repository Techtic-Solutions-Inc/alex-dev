import { ArgumentMetadata, PipeTransform } from '@nestjs/common';
import { VisitorHomeAliasPipe } from './visitor-home-alias.pipe';

describe('VisitorHomeAliasPipe', () => {
  const pipe: PipeTransform = new VisitorHomeAliasPipe();
  const metadata = { type: 'body' } as ArgumentMetadata;

  it('composes full_name from first_name and last_name when full_name is omitted', () => {
    expect(
      pipe.transform(
        {
          first_name: 'Jane',
          last_name: 'Doe',
          email: 'jane.doe@example.com',
        },
        metadata,
      ),
    ).toMatchObject({ full_name: 'Jane Doe' });
  });

  it('copies phone_number onto phone when phone is omitted', () => {
    expect(
      pipe.transform(
        {
          email: 'jane.doe@example.com',
          phone_number: '+1-555-0100',
        },
        metadata,
      ),
    ).toMatchObject({ phone: '+1-555-0100' });
  });

  it('leaves non-object values unchanged', () => {
    expect(pipe.transform(undefined, metadata)).toBeUndefined();
    expect(pipe.transform('raw', metadata)).toBe('raw');
  });
});
