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

// Consolidated Market & Business Intelligence page (GET /market/intelligence). Every
// number here traces back to deterministic scoring server-side — see
// backend/app/services/relevance_scoring.py — the AI layer only ever phrases the
// executive brief, never computes a score itself.

export interface MarketOpportunity {
  title: string;
  sector: string;
  sector_label: string;
  is_emerging: boolean;
  location: string;
  project_value_cr: number | null;
  stardrive_opportunity_value_cr: number | null;
  stage: string;
  material_demand: string[];
  busduct_relevance: "high" | "medium" | "low";
  relevance_score: number;
  score_breakdown: Record<string, number>;
  confidence: number;
  source_name: string;
  status: DataStatus;
  future_integration: string;
}

export interface ExecutiveBriefItem {
  tone: "red" | "amber" | "green";
  headline: string;
  why_it_matters: string;
  source: string;
}

export interface CoreSectorIntelligence {
  sector: string;
  label: string;
  tier: number;
  stardrive_relevance: "very high" | "high" | "medium" | "low";
  relevant_opportunities: number;
  potential_project_value_cr: number | null;
  historical_enquiry_cr: number;
  historical_orders_cr: number;
  historical_conversion_pct: number;
}

export interface MacroLogistics {
  usd_inr?: CommoditySeries;
  logistics_risk_hubs: WeatherRisk[];
}

// Real, sourced news (newsdata.io) filtered and scored deterministically — see
// backend/app/services/news_relevance_service.py. "material" = bare commodity mention
// (copper/aluminium/steel price angle); "sector" = a specific project type Stardrive
// sells into.
export interface MarketSignal {
  title: string;
  summary: string;
  url: string;
  source_name: string;
  published_at: string;
  kind: "material" | "sector";
  sector: string;
  sector_label: string;
  relevance_score: number;
  score_breakdown: Record<string, number>;
}

export interface MarketIntelligencePayload {
  executive_brief: ExecutiveBriefItem[];
  opportunities: MarketOpportunity[];
  emerging_opportunities: MarketOpportunity[];
  material_margin: BusinessImpact[];
  core_sectors: CoreSectorIntelligence[];
  market_signals: MarketSignal[];
  competitors: CompetitorMove[];
  policy_tenders: GovernmentItem[];
  macro_logistics: MacroLogistics;
}
