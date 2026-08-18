import { Controller, Get, Headers } from '@nestjs/common';
import { ApiOkResponse, ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { AuthService, SessionBootstrap } from '../auth/auth.service';

@ApiTags('Health')
@Controller('health')
export class HealthController {
  constructor(private readonly authService: AuthService) {}

  @Get()
  @ApiOperation({
    summary: 'Check API health',
    description:
      'Returns a lightweight liveness result and the frontend session bootstrap shape. When an Authorization bearer token is supplied, user profile fields are populated; otherwise they are null.',
  })
  @ApiOkResponse({
    description: 'The API process is accepting requests.',
    schema: {
      example: {
        success: true,
        message: 'API is healthy',
        data: {
          status: 'UP',
          id: null,
          name: null,
          first_name: null,
          last_name: null,
          email: null,
          token: null,
        },
      },
    },
  })
  @ApiResponse({ status: 400, description: 'Bad request.', type: ApiErrorResponseDto })
  @ApiResponse({ status: 401, description: 'Authentication required.', type: ApiErrorResponseDto })
  @ApiResponse({ status: 403, description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiResponse({ status: 404, description: 'Health resource not found.', type: ApiErrorResponseDto })
  @ApiResponse({ status: 409, description: 'Request conflict.', type: ApiErrorResponseDto })
  @ApiResponse({ status: 422, description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiResponse({ status: 500, description: 'Unexpected server error', type: ApiErrorResponseDto })
  async check(@Headers('authorization') authorization?: string): Promise<{ message: string; data: SessionBootstrap }> {
    return {
      message: 'API is healthy',
      data: await this.authService.resolveSession(authorization),
    };
  }
}
