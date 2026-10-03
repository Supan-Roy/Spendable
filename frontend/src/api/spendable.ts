/**
 * Product & Spendable financial intelligence API client functions.
 * All financial data originates from authenticated backend endpoints.
 */

import { apiFetch } from './client';
import type {
  SpendableOverviewResponse,
  SpendableForecastResponse,
  SpendableActivityListResponse,
  SpendableRecommendationsResponse,
  ScenarioRequest,
  ScenarioResult,
  GeminiExplanationData,
} from './types';

export async function getOverviewApi(): Promise<SpendableOverviewResponse> {
  return apiFetch<SpendableOverviewResponse>('/overview', {
    method: 'GET',
  });
}

export async function getForecastApi(): Promise<SpendableForecastResponse> {
  return apiFetch<SpendableForecastResponse>('/forecast', {
    method: 'GET',
  });
}

export async function getActivityApi(limit: number = 50, offset: number = 0): Promise<SpendableActivityListResponse> {
  return apiFetch<SpendableActivityListResponse>(`/activity?limit=${limit}&offset=${offset}`, {
    method: 'GET',
  });
}

export async function getRecommendationsApi(): Promise<SpendableRecommendationsResponse> {
  return apiFetch<SpendableRecommendationsResponse>('/recommendations', {
    method: 'GET',
  });
}

export async function postSimulateApi(payload: ScenarioRequest): Promise<ScenarioResult> {
  return apiFetch<ScenarioResult>('/simulate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function postExplainApi(): Promise<GeminiExplanationData> {
  return apiFetch<GeminiExplanationData>('/explain', {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export async function postChatApi(
  message: string,
  chatHistory: import('./types').ChatMessage[] = [],
  scenarioResult?: Record<string, any>
): Promise<import('./types').ChatResponse> {
  return apiFetch<import('./types').ChatResponse>('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      chat_history: chatHistory,
      scenario_result: scenarioResult,
    }),
  });
}

