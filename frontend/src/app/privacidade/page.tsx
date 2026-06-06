import Link from 'next/link';

export default function PrivacidadePage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <div className="mb-8">
          <Link href="/auth/register" className="text-blue-600 hover:underline text-sm">
            ← Voltar para Registro
          </Link>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Política de Privacidade (LGPD)
        </h1>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-blue-900">
            <strong>Conformidade LGPD:</strong> Esta política está em conformidade com a
            Lei Geral de Proteção de Dados (Lei 13.709/2018).
          </p>
        </div>

        <div className="prose prose-blue max-w-none space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              1. Dados Coletados
            </h2>
            <p>Coletamos e processamos os seguintes dados pessoais:</p>
            
            <h3 className="text-xl font-semibold text-gray-800 mt-4 mb-2">
              Dados de Cadastro:
            </h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>Nome completo</li>
              <li>CPF</li>
              <li>Email</li>
              <li>Senha (criptografada com bcrypt)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-4 mb-2">
              Dados Tributários:
            </h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>Documentos fiscais (upload)</li>
              <li>Rendimentos e despesas</li>
              <li>Declarações geradas</li>
              <li>Eventos tributários</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mt-4 mb-2">
              Dados de Uso:
            </h3>
            <ul className="list-disc pl-6 space-y-1">
              <li>Logs de acesso (IP, data/hora)</li>
              <li>Ações realizadas no sistema</li>
              <li>Interações com IA</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              2. Finalidade do Tratamento
            </h2>
            <p>Utilizamos seus dados para:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Prestação do Serviço:</strong> Cálculo de impostos, geração
                de declarações, armazenamento de documentos
              </li>
              <li>
                <strong>Autenticação e Segurança:</strong> Controle de acesso,
                proteção contra fraudes
              </li>
              <li>
                <strong>Auditoria e Compliance:</strong> Rastreabilidade de ações
                conforme LGPD
              </li>
              <li>
                <strong>Melhorias:</strong> Análise de uso para aprimorar o sistema
              </li>
              <li>
                <strong>Suporte:</strong> Atendimento e resolução de problemas
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              3. Base Legal (LGPD)
            </h2>
            <p>O tratamento de seus dados é fundamentado em:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Consentimento (Art. 7º, I):</strong> Você aceita
                expressamente esta política ao criar sua conta
              </li>
              <li>
                <strong>Execução de Contrato (Art. 7º, V):</strong> Necessário
                para prestação do serviço contratado
              </li>
              <li>
                <strong>Obrigação Legal (Art. 7º, II):</strong> Retenção de dados
                fiscais por prazo legal
              </li>
              <li>
                <strong>Legítimo Interesse (Art. 7º, IX):</strong> Segurança e
                prevenção de fraudes
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              4. Compartilhamento de Dados
            </h2>
            <p className="font-semibold text-blue-900">
              NÃO vendemos seus dados para terceiros.
            </p>
            <p className="mt-2">Compartilhamos dados apenas com:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Supabase (PostgreSQL):</strong> Armazenamento de dados
                estruturados
              </li>
              <li>
                <strong>MinIO (self-hosted):</strong> Armazenamento de documentos
              </li>
              <li>
                <strong>Ollama (local):</strong> Processamento de IA localmente
              </li>
              <li>
                <strong>Autoridades:</strong> Quando exigido por lei ou ordem
                judicial
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              5. Segurança dos Dados
            </h2>
            <p>Implementamos as seguintes medidas de segurança:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Criptografia de senhas (bcrypt com 12 rounds)</li>
              <li>Autenticação JWT com tokens de curta duração</li>
              <li>Conexões HTTPS/TLS</li>
              <li>Backup automático (Supabase)</li>
              <li>Auditoria de todas as ações (LGPD compliance)</li>
              <li>Controle de acesso rigoroso</li>
              <li>Monitoramento de segurança</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              6. Seus Direitos (LGPD Art. 18)
            </h2>
            <p>Você tem direito a:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Confirmação e Acesso:</strong> Saber quais dados temos sobre você
              </li>
              <li>
                <strong>Correção:</strong> Atualizar dados incompletos ou incorretos
              </li>
              <li>
                <strong>Anonimização/Bloqueio:</strong> Solicitar anonimização de dados
              </li>
              <li>
                <strong>Eliminação:</strong> Excluir dados não mais necessários
              </li>
              <li>
                <strong>Portabilidade:</strong> Receber seus dados em formato estruturado
              </li>
              <li>
                <strong>Revogação do Consentimento:</strong> Retirar consentimento a
                qualquer momento
              </li>
              <li>
                <strong>Informação sobre Compartilhamento:</strong> Saber com quem
                compartilhamos
              </li>
              <li>
                <strong>Oposição:</strong> Opor-se a tratamento realizado
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              7. Retenção de Dados
            </h2>
            <ul className="list-disc pl-6 space-y-2">
              <li>
                <strong>Dados de Cadastro:</strong> Enquanto conta estiver ativa
              </li>
              <li>
                <strong>Dados Tributários:</strong> Por 5 anos (prazo legal Receita Federal)
              </li>
              <li>
                <strong>Logs de Auditoria:</strong> Por 6 meses (LGPD)
              </li>
              <li>
                <strong>Após Exclusão:</strong> Backup retido por 30 dias, depois
                deletado permanentemente
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              8. Cookies e Tecnologias Similares
            </h2>
            <p>Utilizamos:</p>
            <ul className="list-disc pl-6 space-y-1">
              <li>
                <strong>Cookies Essenciais:</strong> JWT tokens para autenticação
                (localStorage)
              </li>
              <li>
                <strong>Cookies de Sessão:</strong> Manter sessão ativa
              </li>
            </ul>
            <p className="mt-2">
              NÃO utilizamos cookies de rastreamento ou analytics de terceiros.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              9. Transferência Internacional
            </h2>
            <p>
              Seus dados são armazenados em servidores no Brasil (Supabase região
              South America). Processamento de IA é realizado localmente.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              10. Encarregado de Dados (DPO)
            </h2>
            <p>Para exercer seus direitos ou tirar dúvidas sobre privacidade:</p>
            <ul className="list-none pl-0 space-y-1">
              <li><strong>Email:</strong> dpo@canmos-niti.com.br</li>
              <li><strong>Prazo de resposta:</strong> Até 15 dias</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              11. Alterações nesta Política
            </h2>
            <p>
              Podemos atualizar esta política periodicamente. Mudanças significativas
              serão notificadas por email com 30 dias de antecedência.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              12. Contato e Reclamações
            </h2>
            <p>
              Se não estivermos respondendo adequadamente às suas solicitações, você
              pode contatar a ANPD (Autoridade Nacional de Proteção de Dados):
            </p>
            <ul className="list-none pl-0 space-y-1">
              <li><strong>Site:</strong> https://www.gov.br/anpd</li>
              <li><strong>Email:</strong> atendimento@anpd.gov.br</li>
            </ul>
          </section>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              <strong>Última atualização:</strong> 04 de Junho de 2026
            </p>
            <p className="text-sm text-gray-600 mt-2">
              <strong>Versão:</strong> 1.0
            </p>
          </div>
        </div>

        <div className="mt-8 flex gap-4">
          <Link
            href="/auth/register"
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Aceitar e Continuar
          </Link>
          <Link
            href="/termos"
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Ver Termos de Uso
          </Link>
        </div>
      </div>
    </div>
  );
}
