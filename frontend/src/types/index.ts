export interface UserProfile {
  id: string;
  email: string;
  cpf: string;
  nome: string;
  telefone: string | null;
  endereco: string | null;
  cidade: string | null;
  estado: string | null;
  cep: string | null;
  data_nascimento: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface UserStats {
  total_documents: number;
  documents_processed: number;
  total_tax_events: number;
  declarations_count: number;
  last_activity: string | null;
}

export interface Document {
  id: string;
  nome_original: string;
  tipo: string;
  mime_type: string;
  status: string;
  created_at: string;
}

export interface UploadingFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  error?: string;
  documentId?: string;
}

export interface Declaration {
  id: number;
  ano_base: number;
  status: string;
  restituicao_estimada: number;
  imposto_devido: number;
  created_at?: string;
  updated_at?: string;
  total_rendimentos?: number;
  total_deducoes?: number;
  base_calculo?: number;
  total_retencao?: number;
  imposto_pagar?: number;
}

export interface DashboardSummary {
  ano_base: number;
  restituicao_estimada: number;
  imposto_devido: number;
  total_rendimentos: number;
  documentos_enviados: number;
  documentos_processados: number;
  total_tax_events: number;
  alertas: Array<{ severidade: string; mensagem: string }>;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface ChatResponse {
  resposta: string;
  conversation_id: string;
  model: string;
  fontes: string[];
}

export interface Conversation {
  id: string;
  titulo: string;
  created_at: string;
}

export interface Alerta {
  severidade: 'info' | 'warning' | 'error';
  mensagem: string;
}

export interface TaxEvent {
  id: number;
  user_id: number;
  document_id: number | null;
  categoria: string;
  subcategoria: string | null;
  valor: number;
  competencia: string;
  origem: string;
  metadata_json: Record<string, unknown> | null;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface RegisterRequest {
  nome: string;
  email: string;
  cpf: string;
  senha: string;
  lgpd_consent: boolean;
}

export interface LoginRequest {
  email: string;
  senha: string;
}
