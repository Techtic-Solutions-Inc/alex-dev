import { Global, Module } from '@nestjs/common';
import { ApmService } from './apm.service';
import { EventLoopMonitorService } from './event-loop-monitor.service';

@Global()
@Module({
  providers: [EventLoopMonitorService, ApmService],
  exports: [EventLoopMonitorService, ApmService],
})
export class ApmModule {}
