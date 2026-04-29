export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error: ApiError | null;
  metadata: {
    timestamp: string;
    request_id: string | null;
    cursor?: string;
    has_more?: boolean;
    limit?: number;
  };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string> | { validation_errors?: ValidationError[] };
}

export interface ValidationError {
  field: string;
  message: string;
  type: string;
}

export class ApiRequestError extends Error {
  code: string;
  details?: ApiError["details"];

  constructor(error: ApiError) {
    super(error.message);
    this.code = error.code;
    this.details = error.details;
    this.name = "ApiRequestError";
  }
}
