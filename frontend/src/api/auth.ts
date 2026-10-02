/**
 * Authentication & Account Management API client functions.
 */

import { apiFetch } from './client';
import type { AuthTokenResponse, UserAccountResponse } from './types';

export async function demoLoginApi(accountId: string): Promise<AuthTokenResponse> {
  return apiFetch<AuthTokenResponse>(`/auth/demo-login/${encodeURIComponent(accountId)}`, {
    method: 'POST',
  });
}

export async function loginApi(payload: { username: string; password: string }): Promise<AuthTokenResponse> {
  return apiFetch<AuthTokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function registerApi(payload: {
  username: string;
  password: string;
  display_name?: string;
}): Promise<AuthTokenResponse> {
  return apiFetch<AuthTokenResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function getDemoAccountsApi(): Promise<UserAccountResponse[]> {
  return apiFetch<UserAccountResponse[]>('/auth/demo-accounts', {
    method: 'GET',
  });
}

export async function getMeApi(): Promise<UserAccountResponse> {
  return apiFetch<UserAccountResponse>('/auth/me', {
    method: 'GET',
  });
}

export async function injectSampleDataApi(): Promise<{
  status: string;
  message: string;
  activities_inserted: number;
  current_balance: number;
}> {
  return apiFetch('/auth/inject-sample-data', {
    method: 'POST',
  });
}

export async function deleteAccountApi(): Promise<{ status: string; detail: string }> {
  return apiFetch('/auth/delete-account', {
    method: 'DELETE',
  });
}

