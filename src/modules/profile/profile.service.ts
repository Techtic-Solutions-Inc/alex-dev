// Ensure ProfileService uses AuthService correctly
import { Injectable } from '@nestjs/common';
import { AuthService } from '../auth/auth.service';

@Injectable()
export class ProfileService {
  constructor(private readonly authService: AuthService) {}

  async changePassword(userId: string, currentPassword: string, newPassword: string): Promise<void> {
    const user = await this.findUserById(userId);
    const isPasswordValid = await this.authService.verifyPassword(currentPassword, user.password);
    if (!isPasswordValid) {
      throw new Error('Current password is incorrect');
    }
    const hashedPassword = await this.authService.hashPassword(newPassword);
    await this.updateUserPassword(userId, hashedPassword);
  }

  private async findUserById(userId: string) {
    // Implementation to find user by ID
  }

  private async updateUserPassword(userId: string, hashedPassword: string) {
    // Implementation to update user password
  }
}