import {
  BadRequestException,
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Post,
  Req,
  UseGuards,
  UsePipes,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiBearerAuth,
  ApiBody,
  ApiCreatedResponse,
  ApiForbiddenResponse,
  ApiInternalServerErrorResponse,
  ApiNotFoundResponse,
  ApiOkResponse,
  ApiOperation,
  ApiServiceUnavailableResponse,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../../common/dto/api-response.dto';
import { AuthenticatedRequest, JwtAuthGuard } from '../../../common/guards/jwt.guard';
import { AuthService, LoginResult } from '../../auth/auth.service';
import { LoginResponseDto } from '../../auth/dto/auth-response.dto';
import { LoginDto } from '../../auth/dto/login.dto';

const authValidationPipe = new ValidationPipe({
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

class RealEstateProfessionalLogoutResponseDto {
  success!: true;
  message!: string;
  data!: Record<string, never>;
}

@ApiTags('Real Estate Professional Authentication')
@Controller('real-estate-professional/auth')
export class RealEstateProfessionalAuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('login')
  @HttpCode(HttpStatus.CREATED)
  @UsePipes(authValidationPipe)
  @ApiOperation({
    summary: 'Sign in a Real Estate Professional',
    description:
      'Authenticates a Real Estate Professional with email and password. Public access. Returns a JWT on success when the account exists, is active, and email is verified. Unregistered emails return 404; incorrect passwords return 401.',
  })
  @ApiBody({ type: LoginDto, description: 'Sign-in form with email and password from the Real Estate Professional Sign In screen.' })
  @ApiCreatedResponse({
    description: 'Sign-in succeeded and a bearer token was issued.',
    type: LoginResponseDto,
  })
  @ApiBadRequestResponse({
    description: 'Email or password failed validation.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'Password does not match the registered account.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({
    description: 'Account is inactive or email is not verified.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({
    description: 'No user exists for the supplied email address.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  @ApiServiceUnavailableResponse({
    description: 'Auth0 authentication is temporarily unavailable.',
    type: ApiErrorResponseDto,
  })
  async login(@Body() dto: LoginDto): Promise<{ message: string; data: LoginResult }> {
    return {
      message: 'Signed in successfully',
      data: await this.authService.loginRealEstateProfessional(dto),
    };
  }

  @Get('logout')
  @HttpCode(HttpStatus.OK)
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Sign out the current Real Estate Professional session',
    description:
      'Invalidates the bearer access token presented in the Authorization header. Requires a valid access JWT. Refresh tokens are not accepted.',
  })
  @ApiOkResponse({
    description: 'Session ended and the access token was revoked.',
    type: RealEstateProfessionalLogoutResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Signed out successfully',
        data: {},
      },
    },
  })
  @ApiUnauthorizedResponse({
    description: 'Missing, invalid, expired, or revoked access token.',
    type: ApiErrorResponseDto,
  })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async logout(@Req() request: AuthenticatedRequest): Promise<{ message: string; data: Record<string, never> }> {
    const [scheme, token] = request.headers.authorization?.split(' ') ?? [];
    if (scheme === 'Bearer' && token) {
      await this.authService.logout(token);
    }
    return {
      message: 'Signed out successfully',
      data: {},
    };
  }
}