export const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  informe_rendimentos: 'Informe de Rendimentos',
  recibo_medico: 'Recibo Médico',
  comprovante_educacao: 'Comprovante de Educação',
  darfs: 'DARF',
  informe_investimentos: 'Informe de Investimentos',
  pensao_alimenticia: 'Pensão Alimentícia',
}

export function getDocumentTypeLabel(tipo: string | null | undefined): string {
  if (!tipo) return 'Não classificado'
  return DOCUMENT_TYPE_LABELS[tipo] || tipo
}
