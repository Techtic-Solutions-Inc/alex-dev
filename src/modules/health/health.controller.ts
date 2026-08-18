// Ensure HealthController uses AuthService correctly
import { Controller, Get, Headers } from '@nestjs/common';
import { AuthService } from '../auth/auth.service';

@Controller('health')
export class HealthController {
  constructor(private readonly authService: AuthService) {}

  @Get()
  async check(@Headers('authorization') authorization: string) {
    const user = await this.authService.resolveSession(authorization);
    return { status: 'ok', user };
  }
}