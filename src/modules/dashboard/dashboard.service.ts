import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { ProfileDownload } from './entities/profile-download.schema';
import { DashboardAnalytics } from './interfaces/dashboard-analytics.interface';

@Injectable()
export class DashboardService {
  constructor(@InjectModel(ProfileDownload.name) private profileDownloadModel: Model<ProfileDownload>) {}

  async getAnalytics(userId: string): Promise<DashboardAnalytics> {
    const downloads = await this.profileDownloadModel.countDocuments({ user_id: userId, is_active: true });
    return {
      downloads,
      // other analytics data
    };
  }
}