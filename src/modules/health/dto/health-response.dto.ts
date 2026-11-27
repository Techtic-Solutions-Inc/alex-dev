import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { SessionBootstrap } from '../../auth/auth.service';
import { SystemHealthSnapshot } from '../../../common/apm/apm.types';

export class SystemHealthSnapshotDto implements SystemHealthSnapshot {
  @ApiProperty({ example: 86400, description: 'Process uptime in seconds.' })
  uptime_seconds!: number;

  @ApiProperty({ example: 92.5, description: 'V8 heap used in megabytes.' })
  memory_heap_used_mb!: number;

  @ApiProperty({ example: 180.3, description: 'Resident set size in megabytes.' })
  memory_rss_mb!: number;

  @ApiProperty({ example: 1.2, description: 'Mean event-loop delay in milliseconds.' })
  event_loop_delay_ms!: number;

  @ApiProperty({ example: true, description: 'Whether external APM export is enabled.' })
  apm_enabled!: boolean;

  @ApiPropertyOptional({
    example: 'datadog',
    description: 'Active APM provider when enabled.',
    nullable: true,
  })
  apm_provider!: string | null;
}

export type HealthCheckData = SessionBootstrap & {
  system_health: SystemHealthSnapshot;
};