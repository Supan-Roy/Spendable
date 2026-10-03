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
  recommendations?: RecommendationItem[];
}

export interface DailyBalance {
  date: string;
  balance: number;
  minimum_balance?: number;
  is_historical?: boolean;
}

export interface DailyTrajectoryPoint {
  day_offset?: number;
  date?: string;
  date_str?: string;
  balance?: number;
  projected_balance?: number;
  required_buffer?: number;
  minimum_balance?: number;
  is_historical?: boolean;
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
  snapshot_time?: string;
  forecast_7d: SpendableForecastItem;
  forecast_14d: SpendableForecastItem;
  forecast_30d: SpendableForecastItem;
  daily_trajectory?: DailyTrajectoryPoint[];
  safety_threshold_bdt?: number;
}

export interface FinancialActivityItem {
  id?: string;
  transaction_id?: string;
  account_id: string;
  amount: number;
  currency?: string;
  direction: 'INFLOW' | 'OUTFLOW';
  activity_type?: string;
  timestamp_utc: string;
  category?: string;
  channel?: string;
  counterparty_name?: string;
  reference_id?: string;
  balance_after?: number;
  provenance?: string;
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
  | 'ADDITIONAL_INCOME'
  | 'ADDITIONAL_COMMITMENT'
  | 'SPENDING_REDUCTION'
  | 'INCOME_DELAY';

export interface ScenarioRequest {
  scenario_type: ScenarioType;
  amount?: number;
  percentage?: number;
  description?: string;
}

export interface ScenarioResult {
  user_id: string;
  snapshot_time?: string;
  scenario_type: ScenarioType;
  scenario_description?: string;
  description?: string;
  base_spendable_amount: number;
  scenario_spendable_amount: number;
  spendable_delta: number;
  base_current_balance: number;
  scenario_current_balance: number;
  base_forecasted_minimum_balance: number;
  scenario_forecasted_minimum_balance: number;
  base_safety_reserve: number;
  scenario_safety_reserve: number;
  base_liquidity_state: LiquidityState;
  scenario_liquidity_state: LiquidityState;
  assumptions?: Record<string, any>;
  factors?: FactorItem[];
  // Backwards compatibility fallbacks
  base_spendable?: number;
  scenario_spendable?: number;
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

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  message: string;
  chat_history?: ChatMessage[];
  scenario_result?: Record<string, any>;
}

export interface ChatResponse {
  reply: string;
  agent_name: string;
  context_used?: Record<string, any>;
}

