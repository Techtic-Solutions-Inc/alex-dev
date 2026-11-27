import {
  BadRequestException,
  Body,
  Controller,
  HttpCode,
  HttpStatus,
  Post,
  UsePipes,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiBody,
  ApiConflictResponse,
  ApiCreatedResponse,
  ApiForbiddenResponse,
  ApiInternalServerErrorResponse,
  ApiNotFoundResponse,
  ApiOperation,
  ApiServiceUnavailableResponse,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { SignupDto } from '../auth/dto/signup.dto';
import { VisitorSignupResponseDto } from './dto/visitor-signup-response.dto';
import { VisitorSignupService, VisitorSignupUser } from './signup.service';

const signupValidationPipe = new ValidationPipe({
  whitelist: true,
  forbidNonWhitelisted: true,
  transform: true,
  errorHttpStatusCode: HttpStatus.BAD_REQUEST,
  exceptionFactory: (errors) =>
    new BadRequestException({
      message: 'Validation failed',
      errors: errors.reduce<Record<string, string[]>>((details, error) => {
        const messages = Object.values(error.constraints ?? {});
        if (messages.length > 0) {
          details[error.property] = messages;
        }
        return details;
      }, {}),
    }),
});

@ApiTags('Visitor')
@Controller('visitor')
export class VisitorSignupController {
  constructor(private readonly visitorSignupService: VisitorSignupService) {}

  @Post('signup')
  @HttpCode(HttpStatus.CREATED)
  @UsePipes(signupValidationPipe)
  @ApiOperation({
    summary: 'Register a visitor account',
    description:
      'Public Sign Up endpoint for the Visitor module. Validates first name, last name, email, password strength, and mandatory terms acceptance. Creates the local account, sends a verification email, and registers the user with Auth0 when Auth0 credentials are configured. Passwords are never returned.',
  })
  @ApiBody({ type: SignupDto, description: 'Sign Up form payload from the Visitor module.' })
  @ApiCreatedResponse({
    description: 'Account created successfully.',
    type: VisitorSignupResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Account created. Please check your email to verify your address.',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          name: 'John Doe',
          full_name: 'John Doe',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com',
          phone: null,
          email_verified: false,
          description: 'Please check your email to verify your address before signing in.',
          link: '/sign-in',
          error: null,
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'Required fields missing, invalid email, weak password, or terms not accepted.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'No authentication is required for sign up.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'An account with the submitted email already exists.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiServiceUnavailableResponse({
    description: 'Auth0 registration or email delivery is temporarily unavailable.',
    type: ApiErrorResponseDto,
  })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async signup(@Body() dto: SignupDto): Promise<{ message: string; data: VisitorSignupUser }> {
    return {
      message: 'Account created. Please check your email to verify your address.',
      data: await this.visitorSignupService.signup(dto),
    };
  }
}