import {
  BadRequestException,
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Post,
  Query,
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
  ApiOkResponse,
  ApiOperation,
  ApiQuery,
  ApiServiceUnavailableResponse,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { AuthService, LoginResult, RegisteredUser, TokenPair } from './auth.service';
import { LoginResponseDto, SignupResponseDto, VerifyEmailResponseDto } from './dto/auth-response.dto';
import { LoginDto } from './dto/login.dto';
import { RefreshTokenDto } from './dto/refresh-token.dto';
import { SignupDto } from './dto/signup.dto';
import { VerifyEmailDto } from './dto/verify-email.dto';

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

@ApiTags('Authentication')
@Controller('auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('login')
  @HttpCode(HttpStatus.CREATED)
  @UsePipes(signupValidationPipe)
  @ApiOperation({
    summary: 'Authenticate a user',
    description:
      'Authenticates a user with their email address and password. This public endpoint accepts no bearer token and returns a JWT only after credentials are valid and the local account is active and email verified. When Auth0 is configured, Auth0 validates credentials and issues the token; otherwise the locally managed credential store is used. Passwords are never returned.',
  })
  @ApiBody({ type: LoginDto, description: 'Sign-in form payload containing email and password.' })
  @ApiCreatedResponse({
    description: 'Credentials were accepted and a JWT token pair was issued.',
    type: LoginResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Signed in successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          email: 'john.doe@example.com',
          token: 'eyJhbGciOiJIUzI1NiJ9.access-token',
          accessToken: 'eyJhbGciOiJIUzI1NiJ9.access-token',
          refreshToken: 'eyJhbGciOiJIUzI1NiJ9.refresh-token',
          tokenType: 'Bearer',
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'Email or password input fails validation. Field-level details are included.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'The supplied email address or password is incorrect.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({
    description:
      'The account is inactive (USER_INACTIVE) or its email address has not been verified (EMAIL_NOT_VERIFIED).',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Authentication resource was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Authentication request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  @ApiServiceUnavailableResponse({
    description: 'Auth0 could not complete authentication after a retry.',
    type: ApiErrorResponseDto,
  })
  async login(@Body() dto: LoginDto): Promise<{ message: string; data: LoginResult }> {
    return {
      message: 'Signed in successfully',
      data: await this.authService.login(dto),
    };
  }

  @Post('signup')
  @HttpCode(HttpStatus.CREATED)
  @UsePipes(signupValidationPipe)
  @ApiOperation({
    summary: 'Register a new user',
    description:
      'Creates an unverified user account and sends a single-use email verification link through SendGrid. This is a public endpoint and does not require a bearer token. Passwords are never returned.',
  })
  @ApiBody({ type: SignupDto, description: 'Sign-up form payload.' })
  @ApiCreatedResponse({
    description: 'Account created and verification email requested.',
    type: SignupResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Account created. Please check your email to verify your address.',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          name: 'John Doe',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com',
          email_verified: false,
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'A required field is missing, invalid, the password is weak, or terms were not accepted.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'No authentication is required for this endpoint.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Authentication resource was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'The submitted email already belongs to an account.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async signup(@Body() dto: SignupDto): Promise<{ message: string; data: RegisteredUser }> {
    return {
      message: 'Account created. Please check your email to verify your address.',
      data: await this.authService.signup(dto),
    };
  }

  @Get('verify-email')
  @UsePipes(signupValidationPipe)
  @ApiOperation({
    summary: 'Verify a registered email address',
    description:
      'Consumes the single-use token sent after registration and marks the account email as verified. This is a public endpoint and does not require a bearer token.',
  })
  @ApiQuery({ type: VerifyEmailDto, description: 'Email verification token.' })
  @ApiOkResponse({
    description: 'The email address was successfully verified.',
    type: VerifyEmailResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Email address verified successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          name: 'John Doe',
          first_name: 'John',
          last_name: 'Doe',
          email: 'john.doe@example.com',
          email_verified: true,
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'The verification token is missing, invalid, expired, or already used.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'No authentication is required for this endpoint.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Authentication resource was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Verification conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async verifyEmail(@Query() dto: VerifyEmailDto): Promise<{ message: string; data: RegisteredUser }> {
    return {
      message: 'Email address verified successfully',
      data: await this.authService.verifyEmail(dto.token),
    };
  }

  @Post('refresh')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Refresh an access token',
    description:
      'Validates a refresh token and returns a rotated access/refresh token pair. No bearer authorization header is required.',
  })
  @ApiBody({ type: RefreshTokenDto, description: 'Refresh-token request payload.' })
  @ApiOkResponse({
    description: 'A new access and refresh token pair was issued.',
    schema: {
      example: {
        success: true,
        message: 'Tokens refreshed successfully',
        data: {
          accessToken: 'eyJhbGciOiJIUzI1NiJ9.access-token',
          refreshToken: 'eyJhbGciOiJIUzI1NiJ9.refresh-token',
          tokenType: 'Bearer',
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Malformed request payload.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Refresh token is invalid or expired.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Authentication resource was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Token refresh conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({
    description: 'Request validation failed.',
    type: ApiErrorResponseDto,
  })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  refresh(@Body() dto: RefreshTokenDto): { message: string; data: TokenPair } {
    return {
      message: 'Tokens refreshed successfully',
      data: this.authService.refresh(dto.refreshToken),
    };
  }
}
