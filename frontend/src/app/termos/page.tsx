import Link from 'next/link';

export default function TermosPage() {
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <div className="mb-8">
          <Link href="/auth/register" className="text-blue-600 hover:underline text-sm">
            ← Voltar para Registro
          </Link>
        </div>

        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Termos de Uso - CANMOS-NITI
        </h1>

        <div className="prose prose-blue max-w-none space-y-6 text-gray-700">
          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              1. Aceitação dos Termos
            </h2>
            <p>
              Ao criar uma conta e utilizar o CANMOS-NITI (Núcleo de Infraestrutura
              Tributária Inteligente), você concorda com estes Termos de Uso e com
              nossa Política de Privacidade.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              2. Descrição do Serviço
            </h2>
            <p>
              O CANMOS-NITI é uma plataforma de gestão tributária que oferece:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Gestão de documentos fiscais</li>
              <li>Cálculo automatizado de impostos (IRPF)</li>
              <li>Geração de declarações</li>
              <li>Assistente inteligente via IA</li>
              <li>OCR para extração de dados de documentos</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              3. Responsabilidades do Usuário
            </h2>
            <p>Ao usar o sistema, você se compromete a:</p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Fornecer informações verdadeiras e precisas</li>
              <li>Manter a confidencialidade de suas credenciais de acesso</li>
              <li>Utilizar o sistema de acordo com a legislação vigente</li>
              <li>Verificar todas as informações antes de enviar declarações oficiais</li>
              <li>Não utilizar o sistema para fins ilícitos ou fraudulentos</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              4. Limitações e Isenções
            </h2>
            <p className="font-semibold text-red-600">
              IMPORTANTE: O CANMOS-NITI é uma ferramenta de apoio e não substitui
              a orientação de um contador ou profissional da área tributária.
            </p>
            <p>
              Você é o único responsável por:
            </p>
            <ul className="list-disc pl-6 space-y-2">
              <li>Revisar todos os cálculos e declarações gerados</li>
              <li>Validar as informações perante órgãos oficiais</li>
              <li>Decisões tomadas com base nas informações fornecidas</li>
              <li>Envio de declarações aos órgãos competentes</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              5. Propriedade Intelectual
            </h2>
            <p>
              Todo o conteúdo do sistema (código, textos, gráficos, logos) é
              propriedade do CANMOS-NITI e protegido por direitos autorais.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              6. Modificações dos Termos
            </h2>
            <p>
              Reservamo-nos o direito de modificar estes termos a qualquer momento.
              Usuários serão notificados sobre mudanças significativas.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              7. Encerramento de Conta
            </h2>
            <p>
              Você pode solicitar o encerramento de sua conta a qualquer momento.
              Reservamo-nos o direito de suspender contas que violem estes termos.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              8. Lei Aplicável
            </h2>
            <p>
              Estes termos são regidos pelas leis brasileiras, incluindo a LGPD
              (Lei 13.709/2018) e o Marco Civil da Internet (Lei 12.965/2014).
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              9. Contato
            </h2>
            <p>
              Para dúvidas sobre estes termos, entre em contato:
            </p>
            <ul className="list-none pl-0 space-y-1">
              <li><strong>Email:</strong> contato@canmos-niti.com.br</li>
              <li><strong>Suporte:</strong> suporte@canmos-niti.com.br</li>
            </ul>
          </section>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-600">
              <strong>Última atualização:</strong> 04 de Junho de 2026
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
            href="/privacidade"
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Ver Política de Privacidade
          </Link>
        </div>
      </div>
    </div>
  );
}
