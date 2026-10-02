/**
 * TypeScript API definitions matching FastAPI backend Pydantic models.
 * Strictly typed - 0 hardcoded or 'any' types for financial data.
 */

export type LiquidityState = 'HEALTHY' | 'WATCH' | 'PRESSURED';

export interface FactorItem {
  factor_name: string;
  value: number;
  impact: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL';
  description: string;
}

export interface SpendableOverviewResponse {
  user_id: string;
  snapshot_time: string;
  current_balance: number;
  planning_horizon_days: number;
  spendable_amount: number;
  protected_amount: number;
  expected_inflow: number;
  expected_outflow: number;
  upcoming_commitments: number;
  forecasted_minimum_balance: number;
  safety_reserve: number;
  liquidity_state: LiquidityState;
  explanation_summary: string;
  factors: FactorItem[];
}

export interface DailyBalance {
  date: string;
  balance: number;
  minimum_balance: number;
  is_historical: boolean;
}

export interface SpendableForecastItem {
  horizon_days: number;
  expected_inflow: number;
  expected_outflow: number;
  upcoming_commitments: number;
  forecasted_minimum_balance: number;
  safety_reserve: number;
  liquidity_state: LiquidityState;
  daily_balances: DailyBalance[];
}

export interface SpendableForecastResponse {
  user_id: string;
  forecast_7d: SpendableForecastItem;
  forecast_14d: SpendableForecastItem;
  forecast_30d: SpendableForecastItem;
}

export interface FinancialActivityItem {
  id: string;
  account_id: string;
  amount: number;
  currency: string;
  direction: 'INFLOW' | 'OUTFLOW';
  activity_type: string;
  timestamp_utc: string;
  category?: string;
  channel?: string;
  counterparty_name?: string;
  reference_id?: string;
  balance_after?: number;
  provenance: string;
}

export interface SpendableActivityListResponse {
  user_id: string;
  total_count: number;
  limit: number;
  offset: number;
  activities: FinancialActivityItem[];
}

export interface RecommendationItem {
  rule_id: string;
  category: string;
  title: string;
  message: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  action_suggested?: string;
}

export interface GeminiExplanationData {
  summary: string;
  bullet_points: string[];
  key_driver?: string;
  action_advice?: string;
  confidence_score: number;
  is_fallback: boolean;
}

export interface SpendableRecommendationsResponse {
  user_id: string;
  liquidity_state: LiquidityState;
  recommendations: RecommendationItem[];
  explanation?: GeminiExplanationData;
}

export type ScenarioType =
  | 'ONE_TIME_EXPENSE'
  | 'ONE_TIME_INCOME'
  | 'RECURRING_EXPENSE'
  | 'INCOME_CHANGE'
  | 'INCOME_DELAY';

export interface ScenarioRequest {
  scenario_type: ScenarioType;
  amount?: number;
  change_percentage?: number;
  delay_days?: number;
  description?: string;
}

export interface ScenarioResult {
  user_id: string;
  scenario_type: ScenarioType;
  description: string;
  base_spendable: number;
  scenario_spendable: number;
  spendable_delta: number;
  base_liquidity_state: LiquidityState;
  scenario_liquidity_state: LiquidityState;
  state_changed: boolean;
  horizon_days: number;
  scenario_factors: Record<string, number | string>;
  explanation?: string;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  account_id: string;
  username?: string;
  display_name?: string;
  is_demo_account: boolean;
}

export interface UserAccountResponse {
  account_id: string;
  username?: string;
  display_name?: string;
  currency: string;
  current_balance: number;
  is_demo_account: boolean;
}
