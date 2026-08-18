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
  Query,
  Req,
  UseGuards,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiBody,
  ApiBearerAuth,
  ApiConflictResponse,
  ApiCreatedResponse,
  ApiForbiddenResponse,
  ApiInternalServerErrorResponse,
  ApiNotFoundResponse,
  ApiOkResponse,
  ApiOperation,
  ApiQuery,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { AuthenticatedRequest, JwtAuthGuard } from '../../common/guards/jwt.guard';
import {
  ChangePasswordDto,
  ChangePasswordResponseDto,
  ContentGeneratedItemDto,
  ContentGeneratedMutationResponseDto,
  ContentGeneratedResponseDataDto,
  ContentGeneratedResponseDto,
  CreateProfileContentDto,
  DownloadsResponseDataDto,
  DownloadsResponseDto,
  GetDownloadsQueryDto,
  ProfileResponseDataDto,
  ProfileResponseDto,
  RedownloadDto,
  RedownloadResponseDataDto,
  RedownloadResponseDto,
  UpdateProfileContentDto,
  UpdateProfileDto,
} from './dto/profile.dto';
import { ProfileService } from './profile.service';

const profileValidationPipe = new ValidationPipe({
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

@ApiTags('Profile')
@ApiBearerAuth('access-token')
@UseGuards(JwtAuthGuard)
@Controller('profile')
export class ProfileController {
  constructor(private readonly profileService: ProfileService) {}

  @Get()
  @ApiOperation({
    summary: 'Retrieve the current user profile',
    description:
      'Returns the authenticated user profile for the Profile screen, including personal details, contact fields, biography, address fields, and frontend compatibility fields such as name, profile, address, image, link, and error.',
  })
  @ApiOkResponse({
    description: 'The authenticated user profile was retrieved successfully.',
    type: ProfileResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Profile retrieved successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          name: 'Joseph Stanley',
          full_name: 'Joseph Stanley',
          first_name: 'Joseph',
          last_name: 'Stanley',
          email: 'joseph.stanley@example.com',
          mobile_number: '123-456-7890',
          phone: '+1-555-0100',
          bio: 'How you show up across the studio.',
          description: 'How you show up across the studio.',
          time_zone: 'Washington, DC, USA (GMT-4)',
          street: '123 Main St',
          country: 'USA',
          state: 'DC',
          city: 'Washington',
          zip: '20001',
          address: '123 Main St, Washington, DC, 20001, USA',
          profile: {
            bio: 'How you show up across the studio.',
            description: 'How you show up across the studio.',
            image: 'https://cdn.example.com/profiles/joseph-stanley.png',
            name: 'Joseph Stanley',
          },
          address_details: {
            street: '123 Main St',
            city: 'Washington',
            state: 'DC',
            zip: '20001',
            country: 'USA',
          },
          image: 'https://cdn.example.com/profiles/joseph-stanley.png',
          link: 'https://agentwise.example.com/joseph-stanley',
          error: null,
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Malformed request.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'The authenticated user profile could not be found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Profile retrieval conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async getProfile(@Req() request: AuthenticatedRequest): Promise<{ message: string; data: ProfileResponseDataDto }> {
    return {
      message: 'Profile retrieved successfully',
      data: await this.profileService.getProfile(request.user.sub),
    };
  }

  @Get('content')
  @ApiOperation({
    summary: 'Retrieve generated content for the authenticated user',
    description:
      'Returns the Profile Content Generated screen payload for the authenticated user, including profile header fields, content history items, and AI credit usage metrics. Only authenticated users can access their own generated content through this endpoint.',
  })
  @ApiOkResponse({
    description: 'The authenticated user generated content history was retrieved successfully.',
    type: ContentGeneratedResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Generated content retrieved successfully',
        data: {
          id: 'profile_content_generated',
          title: 'Content history',
          message: 'Generated content retrieved successfully',
          description: 'Generated content history for the authenticated user',
          name: 'Jane Doe',
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
          profile: {
            id: '66df0b7814b3e891e4ebcd21',
            name: 'Jane Doe',
            full_name: 'Jane Doe',
            phone: '+1-555-0100',
          },
          contents: [
            {
              id: '66df0b7814b3e891e4ebcd51',
              content_id: '66df0b7814b3e891e4ebcd51',
              title: 'Luxury Condo Social Caption',
              description: 'Fresh social caption promoting a luxury condo open house in Miami.',
              created_at: '2026-08-18T09:30:00.000Z',
              updated_at: '2026-08-18T10:15:00.000Z',
              full_name: 'Jane Doe',
              phone: '+1-555-0100',
              profile: {
                id: '66df0b7814b3e891e4ebcd21',
                name: 'Jane Doe',
                full_name: 'Jane Doe',
                phone: '+1-555-0100',
              },
              link: null,
              error: null,
            },
          ],
          ai_credit_usage: {
            total_ai_credits: 5000,
            used_ai_credits: 1,
            remaining_ai_credits: 4999,
          },
          link: null,
          error: null,
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Malformed request.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'The authenticated user profile could not be found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Generated content retrieval conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async getGeneratedContent(
    @Req() request: AuthenticatedRequest,
  ): Promise<{ message: string; data: ContentGeneratedResponseDataDto }> {
    return {
      message: 'Generated content retrieved successfully',
      data: await this.profileService.getGeneratedContent(request.user.sub),
    };
  }

  @Get('downloads')
  @ApiOperation({
    summary: 'Retrieve the authenticated user download history',
    description:
      'Returns the authenticated user active download history for the Profile Downloads screen. The response includes the user header data from Figma such as full_name and phone, frontend compatibility fields like id, title, name, profile, link, message, description, and error, plus pagination metadata for the downloads list.',
  })
  @ApiQuery({
    name: 'page',
    required: false,
    type: Number,
    description: 'Page number for paginated results. Defaults to 1.',
    example: 1,
  })
  @ApiQuery({
    name: 'limit',
    required: false,
    type: Number,
    description: 'Maximum number of results per page. Defaults to 10 and cannot exceed 50.',
    example: 10,
  })
  @ApiOkResponse({
    description: 'The authenticated user download history was retrieved successfully.',
    type: DownloadsResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Download history retrieved successfully',
        data: {
          id: 'profile_downloads',
          title: 'Download history',
          name: 'Jane Doe',
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
          message: 'Download history retrieved successfully',
          description: 'Active download history for the authenticated user',
          profile: {
            id: '66df0b7814b3e891e4ebcd21',
            name: 'Jane Doe',
            full_name: 'Jane Doe',
            phone: '+1-555-0100',
          },
          downloads: [
            {
              id: '66df0b7814b3e891e4ebcd31',
              title: 'Luxury Listing Guide - 2026',
              name: 'Luxury Listing Guide - 2026',
              file_type: 'PDF',
              file_size: '4.2 MB',
              last_downloaded: '2026-06-04',
              downloaded_at: '2026-06-04T09:00:00.000Z',
              status: 'active',
              link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
              message: 'Download available for re-download',
              description: 'Luxury Listing Guide - 2026 (PDF, 4.2 MB)',
              error: null,
            },
          ],
          pagination: {
            page: 1,
            limit: 10,
            total: 1,
            total_pages: 1,
            has_next_page: false,
            has_previous_page: false,
          },
          link: null,
          error: null,
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'One or more pagination query parameters are missing, malformed, or outside the allowed range.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'The authenticated user profile could not be found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Download history retrieval conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async getDownloads(
    @Req() request: AuthenticatedRequest,
    @Query(profileValidationPipe) query: GetDownloadsQueryDto,
  ): Promise<{ message: string; data: DownloadsResponseDataDto }> {
    return {
      message: 'Download history retrieved successfully',
      data: await this.profileService.getDownloads(request.user.sub, query),
    };
  }

  @Put()
  @ApiOperation({
    summary: 'Update the current user profile',
    description:
      'Updates the authenticated user profile with validated personal, contact, biography, time zone, and address fields. The request body is typed so every profile form field appears in Swagger. Duplicate email addresses are rejected with a conflict response.',
  })
  @ApiBody({
    type: UpdateProfileDto,
    description:
      'Profile update payload containing the editable profile form fields, including first_name, last_name, email, mobile_number, phone, bio, time_zone, and address fields.',
  })
  @ApiOkResponse({
    description: 'The authenticated user profile was updated successfully.',
    type: ProfileResponseDto,
  })
  @ApiBadRequestResponse({
    description: 'One or more profile fields are missing, invalid, or fail format validation such as email or phone.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'The authenticated user profile could not be found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'Another account already uses the submitted email address.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async updateProfile(
    @Req() request: AuthenticatedRequest,
    @Body(profileValidationPipe) dto: UpdateProfileDto,
  ): Promise<{ message: string; data: ProfileResponseDataDto }> {
    return {
      message: 'Profile updated successfully',
      data: await this.profileService.updateProfile(request.user.sub, dto),
    };
  }

  @Post('content')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Create generated content for the authenticated user',
    description:
      'Creates a new generated content history item for the authenticated user. The typed JSON body exposes every frontend-required form field in Swagger, including full_name and phone from the Figma design. Creating content consumes one AI credit.',
  })
  @ApiBody({
    type: CreateProfileContentDto,
    description:
      'Generated content payload containing title, description, full_name, phone, and an optional link to the generated asset.',
  })
  @ApiCreatedResponse({
    description: 'The generated content item was created successfully.',
    type: ContentGeneratedMutationResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Generated content created successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd51',
          content_id: '66df0b7814b3e891e4ebcd51',
          title: 'Luxury Condo Social Caption',
          description: 'Fresh social caption promoting a luxury condo open house in Miami.',
          created_at: '2026-08-18T09:30:00.000Z',
          updated_at: '2026-08-18T09:30:00.000Z',
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
          profile: {
            id: '66df0b7814b3e891e4ebcd21',
            name: 'Jane Doe',
            full_name: 'Jane Doe',
            phone: '+1-555-0100',
          },
          link: null,
          error: null,
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'A required field is missing or one or more request fields fail validation.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'The authenticated user is not allowed to use AI content generation features.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'The authenticated user profile could not be found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'The authenticated user has reached the AI credit limit or the request conflicts with current state.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async createGeneratedContent(
    @Req() request: AuthenticatedRequest,
    @Body(profileValidationPipe) dto: CreateProfileContentDto,
  ): Promise<{ message: string; data: ContentGeneratedItemDto }> {
    return {
      message: 'Generated content created successfully',
      data: await this.profileService.createGeneratedContent(request.user.sub, dto),
    };
  }

  @Put('content/:id')
  @ApiOperation({
    summary: 'Update generated content for the authenticated user',
    description:
      'Updates an existing generated content history item that belongs to the authenticated user. The route parameter identifies the content item and the typed request body keeps Swagger aligned with the frontend form fields.',
  })
  @ApiBody({
    type: UpdateProfileContentDto,
    description: 'Full replacement payload for the targeted generated content record.',
  })
  @ApiOkResponse({
    description: 'The generated content item was updated successfully.',
    type: ContentGeneratedMutationResponseDto,
  })
  @ApiBadRequestResponse({
    description: 'A required field is missing or one or more request fields fail validation.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({
    description: 'The targeted generated content item does not exist for the authenticated user.',
    type: ApiErrorResponseDto,
  })
  @ApiConflictResponse({ description: 'Generated content update conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({
    description: 'The content identifier is invalid or validation failed.',
    type: ApiErrorResponseDto,
  })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async updateGeneratedContent(
    @Req() request: AuthenticatedRequest,
    @Param('id') id: string,
    @Body(profileValidationPipe) dto: UpdateProfileContentDto,
  ): Promise<{ message: string; data: ContentGeneratedItemDto }> {
    return {
      message: 'Generated content updated successfully',
      data: await this.profileService.updateGeneratedContent(request.user.sub, id, dto),
    };
  }

  @Delete('content/:id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({
    summary: 'Delete generated content for the authenticated user',
    description:
      'Soft-deletes an existing generated content history item that belongs to the authenticated user. Successful deletion returns HTTP 204 with no response body.',
  })
  @ApiBadRequestResponse({ description: 'Malformed request.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({
    description: 'The targeted generated content item does not exist for the authenticated user.',
    type: ApiErrorResponseDto,
  })
  @ApiConflictResponse({ description: 'Generated content deletion conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({
    description: 'The content identifier is invalid.',
    type: ApiErrorResponseDto,
  })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async deleteGeneratedContent(@Req() request: AuthenticatedRequest, @Param('id') id: string): Promise<void> {
    await this.profileService.deleteGeneratedContent(request.user.sub, id);
  }

  @Post('downloads/re-download')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Trigger a re-download for an authenticated user',
    description:
      'Validates the typed JSON request body and prepares a re-download for a specific active download history record belonging to the authenticated user. The request body must include download_id plus the Figma form fields full_name and phone so Swagger exposes all frontend fields.',
  })
  @ApiBody({
    type: RedownloadDto,
    description:
      'Re-download request payload containing the targeted download_id together with full_name and phone from the Profile Downloads form.',
  })
  @ApiOkResponse({
    description: 'The requested file was prepared for re-download successfully.',
    type: RedownloadResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Re-download prepared successfully',
        data: {
          id: 'profile_download_redownload',
          title: 'Re-download ready',
          name: 'Luxury Listing Guide - 2026',
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
          message: 'Re-download prepared successfully',
          description: 'The selected file is ready to be downloaded again',
          download: {
            id: '66df0b7814b3e891e4ebcd31',
            title: 'Luxury Listing Guide - 2026',
            name: 'Luxury Listing Guide - 2026',
            file_type: 'PDF',
            file_size: '4.2 MB',
            last_downloaded: '2026-06-04',
            downloaded_at: '2026-06-04T09:00:00.000Z',
            status: 'active',
            link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
            message: 'Download available for re-download',
            description: 'Luxury Listing Guide - 2026 (PDF, 4.2 MB)',
            error: null,
          },
          link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
          error: null,
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description:
      'The re-download request body is missing required fields or contains invalid download_id, full_name, or phone values.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({
    description: 'The requested active download history record does not exist for the authenticated user.',
    type: ApiErrorResponseDto,
  })
  @ApiConflictResponse({ description: 'Re-download request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async redownload(
    @Req() request: AuthenticatedRequest,
    @Body(profileValidationPipe) dto: RedownloadDto,
  ): Promise<{ message: string; data: RedownloadResponseDataDto }> {
    return {
      message: 'Re-download prepared successfully',
      data: await this.profileService.redownload(request.user.sub, dto),
    };
  }

  @Post('change-password')
  @HttpCode(HttpStatus.OK)
  @ApiOperation({
    summary: 'Change the current user password',
    description:
      'Validates the authenticated user current password and replaces it with a stronger new password. The new password must match the confirmation field and cannot equal the current password. Password values are write-only and are never returned.',
  })
  @ApiBody({
    type: ChangePasswordDto,
    description: 'Password change payload with current_password, new_password, and confirm_password.',
  })
  @ApiOkResponse({
    description: 'The password was changed successfully.',
    type: ChangePasswordResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Password changed successfully',
        data: {},
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'The request body is malformed or password inputs fail format validation.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'Missing or invalid bearer token, or the current password does not match.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'The authenticated user profile could not be found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Password change conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({
    description: 'Password confirmation failed or the new password reuses the current password.',
    type: ApiErrorResponseDto,
  })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async changePassword(
    @Req() request: AuthenticatedRequest,
    @Body(profileValidationPipe) dto: ChangePasswordDto,
  ): Promise<{ message: string; data: Record<string, never> }> {
    await this.profileService.changePassword(request.user.sub, dto);
    return {
      message: 'Password changed successfully',
      data: {},
    };
  }
}
