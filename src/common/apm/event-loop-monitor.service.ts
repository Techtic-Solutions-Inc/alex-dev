import { Injectable, OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { monitorEventLoopDelay, IntervalHistogram } from 'perf_hooks';

@Injectable()
export class EventLoopMonitorService implements OnModuleInit, OnModuleDestroy {
  private histogram: IntervalHistogram | null = null;

  onModuleInit(): void {
    this.histogram = monitorEventLoopDelay({ resolution: 20 });
    this.histogram.enable();
  }

  onModuleDestroy(): void {
    this.histogram?.disable();
    this.histogram = null;
  }

  getMeanDelayMs(): number {
    if (!this.histogram) {
      return 0;
    }
    return Number((this.histogram.mean / 1_000_000).toFixed(2));
  }
}
