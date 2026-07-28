// Consumption-side contract for Market Intelligence. The actual provider swap
// (Alpha Vantage -> Bloomberg/LME/Reuters) happens server-side in
// backend/app/services/providers/ — the frontend only ever needs to know these
// shapes, tagged by `status`, so no UI change is required when a provider changes.

export type DataStatus = "live" | "demo" | "not_configured" | "unavailable";

export interface CommoditySeries {
  name?: string;
  value?: number;
  rate?: number; // usd_inr uses `rate` instead of `value`
  unit?: string;
  as_of?: string;
  month_change_pct?: number | null;
  status: DataStatus;
  source: string;
  future_integration?: string;
}

export type CommodityMap = Record<string, CommoditySeries>;

export interface CorrelationPair {
  pair: [string, string];
  status: "computed" | "insufficient_history";
  correlation?: number;
  strength?: "strong" | "moderate" | "weak";
  points_used?: number;
  points_collected?: number;
  points_needed?: number;
}

export interface BusinessImpact {
  series: string;
  label: string;
  headline: string;
  magnitude: "small" | "moderate" | "large";
  risk_level: "low" | "medium" | "high";
  affected_departments: string[];
  business_impact: string[];
  basis: string;
}

export interface InfrastructureProject {
  name: string;
  country: string;
  state?: string;
  sector: string;
  value_cr: number;
  stage: string;
  material_demand: string[];
  busduct_relevance?: "high" | "medium" | "low";
  opportunity_score: number;
  status: DataStatus;
  source: string;
  future_integration: string;
}

export interface CompetitorMove {
  name: string;
  move: string;
  detail: string;
  status: DataStatus;
  source: string;
  future_integration: string;
}

export interface GovernmentItem {
  title: string;
  kind: "policy" | "tender";
  detail: string;
  status: DataStatus;
  source: string;
  future_integration: string;
}

export interface EconomicIndicator {
  name: string;
  value?: number;
  unit?: string;
  as_of?: string;
  is_forecast?: boolean;
  status: DataStatus;
  source: string;
  future_integration?: string;
}

export type EconomicIndicatorMap = Record<string, EconomicIndicator>;

export interface WeatherRisk {
  hub: string;
  key: string;
  max_rain_mm_3d?: number;
  max_wind_kmh_3d?: number;
  max_temp_c_3d?: number;
  flags?: string[];
  risk_level?: "low" | "high";
  status: DataStatus;
  source: string;
}

export interface GlobalEvent {
  title: string;
  url: string;
  domain: string;
  source_country: string;
  seen_date: string;
  status: DataStatus;
  source: string;
}

export interface NewsArticle {
  title?: string;
  headline?: string;
  summary?: string;
  url?: string;
  source_name?: string;
  published_at?: string;
  datetime?: number;
  status: DataStatus;
  source: string;
  future_integration?: string;
}

export interface TradeIntelligence {
  comtrade: EconomicIndicatorMap;
  data_gov_in: GovernmentItem[];
}
