import { Injectable } from '@nestjs/common';
import { PrometheusMetricsConfig, readPrometheusMetricsConfig } from './prometheus-metrics.config';

type LabelMap = Record<string, string>;

interface CounterSeries {
  labels: LabelMap;
  value: number;
}

interface HistogramSeries {
  labels: LabelMap;
  buckets: Map<number, number>;
  sum: number;
  count: number;
}

interface GaugeSeries {
  labels: LabelMap;
  value: number;
}

@Injectable()
export class PrometheusMetricsService {
  private readonly config: PrometheusMetricsConfig;
  private readonly counters = new Map<string, CounterSeries>();
  private readonly histograms = new Map<string, HistogramSeries>();
  private readonly gauges = new Map<string, GaugeSeries>();

  constructor() {
    this.config = readPrometheusMetricsConfig();
  }

  isEnabled(): boolean {
    return this.config.enabled;
  }

  getConfig(): PrometheusMetricsConfig {
    return this.config;
  }

  incrementCounter(name: string, labels: LabelMap = {}, amount = 1): void {
    if (!this.config.enabled || amount <= 0) {
      return;
    }
    const seriesKey = this.seriesKey(name, labels);
    const existing = this.counters.get(seriesKey);
    if (existing) {
      existing.value += amount;
      return;
    }
    this.counters.set(seriesKey, { labels, value: amount });
  }

  observeHistogram(name: string, value: number, labels: LabelMap = {}): void {
    if (!this.config.enabled || value < 0) {
      return;
    }
    const seriesKey = this.seriesKey(name, labels);
    let series = this.histograms.get(seriesKey);
    if (!series) {
      series = { labels, buckets: new Map(), sum: 0, count: 0 };
      for (const upperBound of this.config.defaultHistogramBucketsMs) {
        series.buckets.set(upperBound, 0);
      }
      series.buckets.set(Number.POSITIVE_INFINITY, 0);
      this.histograms.set(seriesKey, series);
    }

    series.sum += value;
    series.count += 1;
    for (const upperBound of series.buckets.keys()) {
      if (value <= upperBound || !Number.isFinite(upperBound)) {
        series.buckets.set(upperBound, (series.buckets.get(upperBound) ?? 0) + 1);
      }
    }
  }

  setGauge(name: string, value: number, labels: LabelMap = {}): void {
    if (!this.config.enabled) {
      return;
    }
    const seriesKey = this.seriesKey(name, labels);
    this.gauges.set(seriesKey, { labels, value });
  }

  recordHttpRequest(params: {
    method: string;
    route: string;
    statusCode: number;
    durationMs: number;
    slow: boolean;
  }): void {
    const labels = {
      method: params.method,
      route: this.sanitizeRoute(params.route),
      status: String(params.statusCode),
    };
    this.incrementCounter('http_requests_total', labels);
    this.observeHistogram('http_request_duration_ms', params.durationMs, {
      method: params.method,
      route: labels.route,
    });
    if (params.slow) {
      this.incrementCounter('http_slow_requests_total', labels);
    }
    if (params.statusCode >= 500) {
      this.incrementCounter('http_server_errors_total', labels);
    }
  }

  recordError(name: string): void {
    this.incrementCounter('application_errors_total', { name });
  }

  updateRuntimeGauges(snapshot: {
    uptimeSeconds: number;
    heapUsedBytes: number;
    rssBytes: number;
    eventLoopDelayMs: number;
  }): void {
    this.setGauge('process_uptime_seconds', snapshot.uptimeSeconds);
    this.setGauge('process_heap_used_bytes', snapshot.heapUsedBytes);
    this.setGauge('process_resident_memory_bytes', snapshot.rssBytes);
    this.setGauge('event_loop_delay_ms', snapshot.eventLoopDelayMs);
  }

  renderMetrics(): string {
    const lines: string[] = [];

    const metricGroups = new Map<string, Array<{ type: 'counter' | 'histogram' | 'gauge'; body: string }>>();

    for (const [key, counter] of this.counters) {
      const metricName = key.split('|')[0] ?? '';
      const rendered = this.formatCounter(metricName, counter);
      this.pushMetric(metricGroups, metricName, 'counter', rendered);
    }

    for (const [key, histogram] of this.histograms) {
      const metricName = key.split('|')[0] ?? '';
      const rendered = this.formatHistogram(metricName, histogram);
      this.pushMetric(metricGroups, metricName, 'histogram', rendered);
    }

    for (const [key, gauge] of this.gauges) {
      const metricName = key.split('|')[0] ?? '';
      const rendered = `${this.qualifiedName(metricName)}${this.formatLabels(gauge.labels)} ${this.formatNumber(gauge.value)}`;
      this.pushMetric(metricGroups, metricName, 'gauge', rendered);
    }

    for (const [metricName, entries] of metricGroups) {
      const type = entries[0]?.type ?? 'gauge';
      lines.push(`# HELP ${this.qualifiedName(metricName)} Backend API ${metricName.replaceAll('_', ' ')}`);
      lines.push(`# TYPE ${this.qualifiedName(metricName)} ${type}`);
      for (const entry of entries) {
        lines.push(entry.body);
      }
    }

    return `${lines.join('\n')}\n`;
  }

  private pushMetric(
    groups: Map<string, Array<{ type: 'counter' | 'histogram' | 'gauge'; body: string }>>,
    metricName: string,
    type: 'counter' | 'histogram' | 'gauge',
    body: string,
  ): void {
    const list = groups.get(metricName) ?? [];
    list.push({ type, body });
    groups.set(metricName, list);
  }

  private formatCounter(metricName: string, counter: CounterSeries): string {
    return `${this.qualifiedName(metricName)}${this.formatLabels(counter.labels)} ${this.formatNumber(counter.value)}`;
  }

  private formatHistogram(metricName: string, histogram: HistogramSeries): string {
    const name = this.qualifiedName(metricName);
    const labelBase = this.formatLabels(histogram.labels, false);
    const lines: string[] = [];
    let cumulative = 0;
    const sortedBounds = [...histogram.buckets.keys()].sort((left, right) => left - right);

    for (const upperBound of sortedBounds) {
      cumulative += histogram.buckets.get(upperBound) ?? 0;
      const boundLabel = Number.isFinite(upperBound) ? String(upperBound) : '+Inf';
      lines.push(`${name}_bucket${this.joinLabels(labelBase, { le: boundLabel })} ${this.formatNumber(cumulative)}`);
    }

    lines.push(`${name}_sum${labelBase} ${this.formatNumber(histogram.sum)}`);
    lines.push(`${name}_count${labelBase} ${this.formatNumber(histogram.count)}`);
    return lines.join('\n');
  }

  private qualifiedName(metricName: string): string {
    return `${this.config.prefix}_${metricName}`;
  }

  private seriesKey(metricName: string, labels: LabelMap): string {
    const labelKey = Object.keys(labels)
      .sort()
      .map((key) => `${key}=${labels[key]}`)
      .join(',');
    return `${metricName}|${labelKey}`;
  }

  private sanitizeRoute(route: string): string {
    const trimmed = route.trim() || 'unknown';
    return trimmed.length > 120 ? `${trimmed.slice(0, 117)}...` : trimmed;
  }

  private formatLabels(labels: LabelMap, leading = true): string {
    const keys = Object.keys(labels).sort();
    if (keys.length === 0) {
      return '';
    }
    const body = keys.map((key) => `${key}="${this.escapeLabel(labels[key] ?? '')}"`).join(',');
    return leading ? `{${body}}` : `{${body}}`;
  }

  private joinLabels(base: string, extra: LabelMap): string {
    if (!base) {
      return this.formatLabels(extra);
    }
    const merged = base.slice(1, -1);
    const extraBody = Object.keys(extra)
      .sort()
      .map((key) => `${key}="${this.escapeLabel(extra[key] ?? '')}"`)
      .join(',');
    return `{${merged},${extraBody}}`;
  }

  private escapeLabel(value: string): string {
    return value.replaceAll('\\', '\\\\').replaceAll('\n', '\\n').replaceAll('"', '\\"');
  }

  private formatNumber(value: number): string {
    if (!Number.isFinite(value)) {
      return '0';
    }
    if (Number.isInteger(value)) {
      return String(value);
    }
    return value.toFixed(4).replace(/\.?0+$/, '');
  }
}