export class HttpException extends Error {
  public readonly status: number;
  public readonly code: string;
  public readonly details: Record<string, unknown> | null;

  constructor(message: string, status: number, code = 'HTTP_ERROR', details: Record<string, unknown> | null = null) {
    super(message);
    this.name = 'HttpException';
    this.status = status;
    this.code = code;
    this.details = details;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}
