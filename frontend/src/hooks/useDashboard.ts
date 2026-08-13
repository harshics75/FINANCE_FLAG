import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import type { DashboardPayload, DocumentItem } from "../types";
import type { CommodityMap, CorrelationPair, MarketIntelligencePayload, NewsArticle } from "../types/market";

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

export const useCompanyIntel = () =>
  useQuery({
    queryKey: ["market", "company-intel"],
    queryFn: async () => (await api.get<NewsArticle[]>("/market/company-intel")).data,
    staleTime: 60 * 60_000,
  });

export const useMarketIntelligence = () =>
  useQuery({
    queryKey: ["market", "intelligence"],
    queryFn: async () => (await api.get<MarketIntelligencePayload>("/market/intelligence")).data,
    refetchInterval: 5 * 60_000,
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
