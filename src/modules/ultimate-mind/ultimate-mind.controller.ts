import {
  BadRequestException,
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Post,
  Put,
  Req,
  UseGuards,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiBearerAuth,
  ApiBody,
  ApiConflictResponse,
  ApiCreatedResponse,
  ApiForbiddenResponse,
  ApiInternalServerErrorResponse,
  ApiNoContentResponse,
  ApiNotFoundResponse,
  ApiOkResponse,
  ApiOperation,
  ApiParam,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { AuthenticatedRequest, JwtAuthGuard } from '../../common/guards/jwt.guard';
import {
  CreateUltimateMindAiCreditDto,
  UltimateMindAiCreditCreateResponseDto,
  UltimateMindAiCreditListDataDto,
  UltimateMindAiCreditListResponseDto,
  UltimateMindAiCreditRecordDataDto,
  UltimateMindAiCreditUpdateResponseDto,
  UpdateUltimateMindAiCreditDto,
} from './dto/ultimate-mind.dto';
import { UltimateMindService } from './ultimate-mind.service';

const ultimateMindValidationPipe = new ValidationPipe({
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

@ApiTags('Ultimate Mind')
@ApiBearerAuth('access-token')
@UseGuards(JwtAuthGuard)
@Controller('v1/real-estate-professional/ultimate-mind')
export class UltimateMindController {
  constructor(private readonly ultimateMindService: UltimateMindService) {}

  @Get('ai-credits')
  @ApiOperation({
    summary: 'List AI credit usage records',
    description:
      'Returns AI credit usage records for the Ultimate Mind screen. Authenticated users receive their own records; administrators receive all active records. The response includes profile header fields full_name and phone for the requesting user.',
  })
  @ApiOkResponse({
    description: 'AI credit usage records retrieved successfully.',
    type: UltimateMindAiCreditListResponseDto,
    schema: {
      example: {
        success: true,
        message: 'AI credit usage records retrieved successfully',
        data: {
          ai_credit_usage: [
            {
              id: '66df0b7814b3e891e4ebcd21',
              user: 'Joseph Stanley',
              usage: 1420,
              limit: 5000,
            },
          ],
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Malformed request parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have permission to access AI credit usage records.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'AI credit usage record was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'AI credit usage request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async listRecords(
    @Req() request: AuthenticatedRequest,
  ): Promise<{ message: string; data: UltimateMindAiCreditListDataDto }> {
    return {
      message: 'AI credit usage records retrieved successfully',
      data: await this.ultimateMindService.listRecords(request.user.sub),
    };
  }

  @Post('ai-credits')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Create an AI credit usage record',
    description:
      'Creates a new AI credit usage record for a linked user. Requires an administrator role. The typed JSON request body includes all Figma-backed fields such as full_name and phone, and synchronizes credits on the linked user account.',
  })
  @ApiBody({ type: CreateUltimateMindAiCreditDto, description: 'New AI credit usage record payload.' })
  @ApiCreatedResponse({
    description: 'AI credit usage record created successfully.',
    type: UltimateMindAiCreditCreateResponseDto,
  })
  @ApiBadRequestResponse({
    description: 'Required fields are missing or invalid, including malformed phone values.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have administrator permission to create AI credit usage records.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Linked user was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'An active AI credit usage record already exists for the linked user.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async createRecord(
    @Req() request: AuthenticatedRequest,
    @Body(ultimateMindValidationPipe) dto: CreateUltimateMindAiCreditDto,
  ): Promise<{ message: string; data: UltimateMindAiCreditRecordDataDto }> {
    return {
      message: 'AI credit usage record created successfully',
      data: await this.ultimateMindService.createRecord(request.user.sub, dto),
    };
  }

  @Put('ai-credits/:id')
  @ApiOperation({
    summary: 'Update an AI credit usage record',
    description:
      'Updates an existing active AI credit usage record. Requires an administrator role. Supports partial updates across usage, limit, full_name, and phone fields.',
  })
  @ApiParam({
    name: 'id',
    description: 'MongoDB ObjectId of the AI credit usage record.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @ApiBody({ type: UpdateUltimateMindAiCreditDto, description: 'Partial AI credit usage record update payload.' })
  @ApiOkResponse({
    description: 'AI credit usage record updated successfully.',
    type: UltimateMindAiCreditUpdateResponseDto,
  })
  @ApiBadRequestResponse({ description: 'Malformed request payload.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have administrator permission to update AI credit usage records.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'AI credit usage record was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'AI credit usage request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async updateRecord(
    @Req() request: AuthenticatedRequest,
    @Param('id') id: string,
    @Body(ultimateMindValidationPipe) dto: UpdateUltimateMindAiCreditDto,
  ): Promise<{ message: string; data: UltimateMindAiCreditRecordDataDto }> {
    return {
      message: 'AI credit usage record updated successfully',
      data: await this.ultimateMindService.updateRecord(request.user.sub, id, dto),
    };
  }

  @Delete('ai-credits/:id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({
    summary: 'Delete an AI credit usage record',
    description:
      'Soft-deletes an active AI credit usage record by marking it inactive. Requires an administrator role. Returns no response body on success.',
  })
  @ApiParam({
    name: 'id',
    description: 'MongoDB ObjectId of the AI credit usage record.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @ApiNoContentResponse({ description: 'AI credit usage record deleted successfully.' })
  @ApiBadRequestResponse({ description: 'Malformed request parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have administrator permission to delete AI credit usage records.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'AI credit usage record was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'AI credit usage request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async deleteRecord(@Req() request: AuthenticatedRequest, @Param('id') id: string): Promise<void> {
    await this.ultimateMindService.deleteRecord(request.user.sub, id);
  }
}
