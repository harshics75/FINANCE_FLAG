export interface User { id: string; email: string; full_name: string; role: string; }
export interface TokenPair { access_token: string; refresh_token: string; }
export interface DocumentItem {
  id: string; filename: string; doc_type: string; fiscal_period: string;
  status: string; is_scanned: boolean; page_count: number; size_bytes: number;
  version: number; created_at: string; error: string;
}
export interface SeriesPoint { period: string; value: number; }
export interface DashboardPayload { page: string; payload: Record<string, any>; generated_at: string; }
export interface Citation { document_id: string; filename: string; page_number: number; snippet: string; }
export interface ChatMessage { role: "user" | "assistant"; content: string; citations?: Citation[]; }
