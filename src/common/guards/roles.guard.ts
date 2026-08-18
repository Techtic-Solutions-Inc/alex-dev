import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { HttpException } from '../exceptions/http.exception';
import { AuthenticatedRequest } from './jwt.guard';
import { ROLES_KEY } from './roles.decorator';
import { User, UserRole } from '../../modules/auth/entities/user.schema';

@Injectable()
export class RolesGuard implements CanActivate {
  constructor(
    private readonly reflector: Reflector,
    @InjectModel(User.name) private readonly userModel: Model<User>,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const requiredRoles = this.reflector.getAllAndOverride<UserRole[]>(ROLES_KEY, [
      context.getHandler(),
      context.getClass(),
    ]);

    if (!requiredRoles || requiredRoles.length === 0) {
      return true;
    }

    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const userId = request.user?.sub;
    if (!userId || !Types.ObjectId.isValid(userId)) {
      throw new HttpException('Authentication is required', 401, 'AUTHENTICATION_REQUIRED');
    }

    const user = await this.userModel.findById(userId).select('role is_active').lean().exec();
    if (!user || user.is_active === false) {
      throw new HttpException('Authentication token is invalid or expired', 401, 'INVALID_TOKEN');
    }

    if (!requiredRoles.includes((user.role ?? 'agent') as UserRole)) {
      throw new HttpException(
        'You do not have permission to access the content library',
        403,
        'CONTENT_LIBRARY_ACCESS_FORBIDDEN',
      );
    }

    return true;
  }
}
