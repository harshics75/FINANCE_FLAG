import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import type { DashboardPayload, DocumentItem } from "../types";

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
