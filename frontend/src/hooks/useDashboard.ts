import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import type { DashboardPayload, DocumentItem } from "../types";
import type {
  BusinessImpact, CommodityMap, CompetitorMove, CorrelationPair, EconomicIndicatorMap, GlobalEvent,
  GovernmentItem, InfrastructureProject, NewsArticle, TradeIntelligence, WeatherRisk,
} from "../types/market";

export const useDashboard = (page: string) =>
  useQuery({
    queryKey: ["dashboard", page],
    queryFn: async () => (await api.get<DashboardPayload>(`/dashboard/${page}`)).data,
    refetchInterval: 30_000,
  });

export const useDocuments = () =>
  useQuery({
    queryKey: ["documents"],
    queryFn: async () => (await api.get<DocumentItem[]>("/documents")).data,
    refetchInterval: 10_000,
  });

export const useMarketData = () =>
  useQuery({
    queryKey: ["market", "live"],
    queryFn: async () => (await api.get<Record<string, any>>("/market/live")).data,
    refetchInterval: 5 * 60_000,
  });

export const useMarketNews = () =>
  useQuery({
    queryKey: ["market", "news"],
    queryFn: async () => (await api.get<any[]>("/market/news")).data,
    refetchInterval: 15 * 60_000,
  });

export const useIndustrialNews = () =>
  useQuery({
    queryKey: ["market", "industrial-news"],
    queryFn: async () => (await api.get<any[]>("/market/industrial-news")).data,
    refetchInterval: 15 * 60_000,
  });

export const useCommodities = () =>
  useQuery({
    queryKey: ["market", "commodities"],
    queryFn: async () => (await api.get<CommodityMap>("/market/commodities")).data,
    refetchInterval: 5 * 60_000,
  });

export const useSeriesHistory = (series: string) =>
  useQuery({
    queryKey: ["market", "history", series],
    queryFn: async () => (await api.get<{ date: string; value: number }[]>(`/market/history/${series}`)).data,
    staleTime: 5 * 60_000,
  });

export const useCorrelations = () =>
  useQuery({
    queryKey: ["market", "correlations"],
    queryFn: async () => (await api.get<CorrelationPair[]>("/market/correlations")).data,
    refetchInterval: 5 * 60_000,
  });

export const useBusinessImpact = () =>
  useQuery({
    queryKey: ["market", "impact"],
    queryFn: async () => (await api.get<BusinessImpact[]>("/market/impact")).data,
    refetchInterval: 5 * 60_000,
  });

export const useInfrastructureProjects = () =>
  useQuery({
    queryKey: ["market", "infrastructure"],
    queryFn: async () => (await api.get<InfrastructureProject[]>("/market/infrastructure")).data,
    staleTime: 60 * 60_000,
  });

export const useCompetitors = () =>
  useQuery({
    queryKey: ["market", "competitors"],
    queryFn: async () => (await api.get<CompetitorMove[]>("/market/competitors")).data,
    staleTime: 60 * 60_000,
  });

export const useGovernmentItems = () =>
  useQuery({
    queryKey: ["market", "government"],
    queryFn: async () => (await api.get<GovernmentItem[]>("/market/government")).data,
    staleTime: 60 * 60_000,
  });

export const useEconomicIndicators = () =>
  useQuery({
    queryKey: ["market", "economic-indicators"],
    queryFn: async () => (await api.get<EconomicIndicatorMap>("/market/economic-indicators")).data,
    staleTime: 60 * 60_000,
  });

export const useEnergyIndicators = () =>
  useQuery({
    queryKey: ["market", "energy"],
    queryFn: async () => (await api.get<EconomicIndicatorMap>("/market/energy")).data,
    staleTime: 60 * 60_000,
  });

export const useWeatherRisk = () =>
  useQuery({
    queryKey: ["market", "weather-risk"],
    queryFn: async () => (await api.get<WeatherRisk[]>("/market/weather-risk")).data,
    refetchInterval: 30 * 60_000,
  });

export const useGlobalEvents = () =>
  useQuery({
    queryKey: ["market", "global-events"],
    queryFn: async () => (await api.get<GlobalEvent[]>("/market/global-events")).data,
    refetchInterval: 15 * 60_000,
  });

export const useManufacturingNews = () =>
  useQuery({
    queryKey: ["market", "manufacturing-news"],
    queryFn: async () => (await api.get<NewsArticle[]>("/market/manufacturing-news")).data,
    staleTime: 60 * 60_000,
  });

export const useCompanyIntel = () =>
  useQuery({
    queryKey: ["market", "company-intel"],
    queryFn: async () => (await api.get<NewsArticle[]>("/market/company-intel")).data,
    staleTime: 60 * 60_000,
  });

export const useTradeIntelligence = () =>
  useQuery({
    queryKey: ["market", "trade"],
    queryFn: async () => (await api.get<TradeIntelligence>("/market/trade")).data,
    staleTime: 60 * 60_000,
  });

export const useSystemInfo = () =>
  useQuery({
    queryKey: ["system", "info"],
    queryFn: async () => (await api.get<{ provider: string; label: string; chat_model: string; embedding_model: string }>("/system/info")).data,
    staleTime: 5 * 60_000,
  });

export interface AnalysisProgress {
  completed: string[];
  status: "running" | "done" | "failed" | "unknown";
  nodes: string[];
}

export const useAnalysisProgress = (runId: string | null) =>
  useQuery({
    queryKey: ["analysis", "progress", runId],
    queryFn: async () => (await api.get<AnalysisProgress>(`/analysis/progress/${runId}`)).data,
    enabled: !!runId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "done" || status === "failed" ? false : 2500;
    },
  });

export interface AgentResult { agent: string; status: string; result: Record<string, any>; created_at: string; }

export const useRunResults = (runId: string | null, ready: boolean) =>
  useQuery({
    queryKey: ["analysis", "runs", runId],
    queryFn: async () => (await api.get<AgentResult[]>(`/analysis/runs/${runId}`)).data,
    enabled: !!runId && ready,
  });
