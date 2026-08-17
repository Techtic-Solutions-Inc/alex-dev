import { Controller, Get } from '@nestjs/common';
import { ApiOkResponse, ApiOperation, ApiResponse, ApiTags } from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';

class HealthDataDto {
  status!: 'UP';
}

@ApiTags('Health')
@Controller('health')
export class HealthController {
  @Get()
  @ApiOperation({
    summary: 'Check API health',
    description: 'Returns a lightweight liveness result. This endpoint does not expose infrastructure details.',
  })
  @ApiOkResponse({
    description: 'The API process is accepting requests.',
    schema: {
      example: {
        success: true,
        message: 'API is healthy',
        data: { status: 'UP' },
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
  check(): { message: string; data: HealthDataDto } {
    return { message: 'API is healthy', data: { status: 'UP' } };
  }
}
