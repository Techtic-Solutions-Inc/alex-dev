import { Global, Module } from '@nestjs/common';
import { ApmService } from './apm.service';
import { EventLoopMonitorService } from './event-loop-monitor.service';
import { PrometheusMetricsService } from './prometheus-metrics.service';

@Global()
@Module({
  providers: [EventLoopMonitorService, PrometheusMetricsService, ApmService],
  exports: [EventLoopMonitorService, PrometheusMetricsService, ApmService],
})
export class ApmModule {}
