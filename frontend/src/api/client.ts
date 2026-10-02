/**
 * Centralized API client wrapper with JWT token insertion and error handling.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.status = status;
    this.data = data;
    this.name = 'ApiError';
  }
}

let onUnauthorizedCallback: (() => void) | null = null;

export function setUnauthorizedHandler(handler: () => void) {
  onUnauthorizedCallback = handler;
}

export function getStoredToken(): string | null {
  return localStorage.getItem('spendable_jwt_token');
}

export function setStoredToken(token: string | null) {
  if (token) {
    localStorage.setItem('spendable_jwt_token', token);
  } else {
    localStorage.removeItem('spendable_jwt_token');
  }
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getStoredToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      setStoredToken(null);
      if (onUnauthorizedCallback) {
        onUnauthorizedCallback();
      }
      const errData = await response.json().catch(() => ({}));
      throw new ApiError(401, errData.detail || 'Unauthorized session expired', errData);
    }

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new ApiError(
        response.status,
        errData.detail || `HTTP Error ${response.status}`,
        errData
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(500, (error as Error).message || 'Network error connecting to Spendable API');
  }
}
