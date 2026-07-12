import logging
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fpdf import FPDF
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.models.tax import Declaration, TaxEvent
from app.shared.models.user import User

logger = logging.getLogger(__name__)


class DeclarationPDF(FPDF):
    def __init__(self, user: User, ano_base: int, calc_result: dict, events: list[TaxEvent]):
        super().__init__()
        self.user = user
        self.ano_base = ano_base
        self.calc_result = calc_result
        self.events = events

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "CANMOS-NITI", new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_font("Helvetica", "", 10)
        self.cell(0, 6, f"Comprovante de Declaracao IRPF - Ano Base {self.ano_base}", new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(4)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} - Pagina {self.page_no()}/{{nb}}", align="C")

    def build(self) -> "DeclarationPDF":
        self.alias_nb_pages()
        self.add_page()

        self._section_dados_pessoais()
        self._section_resumo_financeiro()
        self._section_eventos()
        self._section_validacoes()

        return self

    def _section_dados_pessoais(self):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, "  Dados do Contribuinte", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

        self.set_font("Helvetica", "", 10)
        dados = [
            ("Nome", self.user.nome),
            ("CPF", self.user.cpf),
            ("Email", self.user.email),
            ("Ano Base", str(self.ano_base)),
            ("Status", self.calc_result.get("status", "rascunho").capitalize()),
        ]

        for label, value in dados:
            self.set_font("Helvetica", "B", 10)
            self.cell(40, 6, f"{label}:", new_x="END")
            self.set_font("Helvetica", "", 10)
            self.cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")

        self.ln(6)

    def _section_resumo_financeiro(self):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, "  Resumo Financeiro", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

        self.set_font("Helvetica", "", 10)
        resumo = [
            ("Total Rendimentos", self._fmt(self.calc_result.get("total_rendimentos", Decimal("0")))),
            ("Total Deducoes", self._fmt(self.calc_result.get("total_deducoes", Decimal("0")))),
            ("Base de Calculo", self._fmt(self.calc_result.get("base_calculo", Decimal("0")))),
            ("Imposto Devido", self._fmt(self.calc_result.get("imposto_devido", Decimal("0")))),
            ("Total Retencao (IRRF + DARFs)", self._fmt(self.calc_result.get("total_retencao", Decimal("0")))),
        ]

        for label, value in resumo:
            self.cell(100, 6, f"  {label}:", new_x="END")
            self.cell(0, 6, value, new_x="LMARGIN", new_y="NEXT", align="R")

        self.ln(3)

        restituicao = self.calc_result.get("restituicao_estimada", Decimal("0"))
        imposto_pagar = self.calc_result.get("imposto_pagar", Decimal("0"))

        if restituicao > 0:
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(0, 128, 0)
            self.cell(0, 8, f"  Restituicao Estimada: {self._fmt(restituicao)}", new_x="LMARGIN", new_y="NEXT")
        elif imposto_pagar > 0:
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(200, 0, 0)
            self.cell(0, 8, f"  Imposto a Pagar: {self._fmt(imposto_pagar)}", new_x="LMARGIN", new_y="NEXT")
        else:
            self.set_font("Helvetica", "B", 12)
            self.set_text_color(0, 0, 0)
            self.cell(0, 8, "  Imposto Quitado", new_x="LMARGIN", new_y="NEXT")

        self.set_text_color(0, 0, 0)
        self.ln(6)

    def _section_eventos(self):
        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, "  Eventos Fiscais Detalhados", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

        if not self.events:
            self.set_font("Helvetica", "I", 10)
            self.cell(0, 6, "  Nenhum evento fiscal encontrado.", new_x="LMARGIN", new_y="NEXT")
            self.ln(4)
            return

        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(220, 220, 220)
        self.cell(60, 6, "Categoria", border=1, fill=True)
        self.cell(40, 6, "Competencia", border=1, fill=True, align="C")
        self.cell(40, 6, "Valor", border=1, fill=True, align="R")
        self.cell(40, 6, "Origem", border=1, fill=True, align="C")
        self.ln()

        self.set_font("Helvetica", "", 9)
        for event in self.events:
            self.cell(60, 6, str(event.categoria)[:30], border=1)
            self.cell(40, 6, str(event.competencia), border=1, align="C")
            self.cell(40, 6, self._fmt(event.valor), border=1, align="R")
            self.cell(40, 6, str(event.origem), border=1, align="C")
            self.ln()

        self.ln(6)

    def _section_validacoes(self):
        validacoes = self.calc_result.get("validacoes", [])
        if not validacoes:
            return

        self.set_font("Helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, "  Validacoes e Alertas", new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

        self.set_font("Helvetica", "", 9)
        for v in validacoes:
            sev = v.get("severidade", "info").upper()
            msg = v.get("mensagem", "")

            if sev == "WARNING":
                self.set_text_color(200, 150, 0)
            elif sev == "ERROR":
                self.set_text_color(200, 0, 0)
            else:
                self.set_text_color(100, 100, 100)

            self.cell(0, 5, f"  [{sev}] {msg}", new_x="LMARGIN", new_y="NEXT")

        self.set_text_color(0, 0, 0)

    @staticmethod
    def _fmt(valor) -> str:
        try:
            v = Decimal(str(valor))
            return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except Exception:
            return "R$ 0,00"


async def gerar_pdf_declaracao(
    user: User,
    ano_base: int,
    db: AsyncSession,
) -> Optional[bytes]:
    stmt = select(Declaration).where(
        Declaration.user_id == user.id,
        Declaration.ano_base == ano_base,
    )
    result = await db.execute(stmt)
    declaration = result.scalar_one_or_none()

    if not declaration:
        return None

    from app.modules.tax_engine.calculator import TaxCalculator
    calc_result = await TaxCalculator.calculate_irpf(user, ano_base, db)
    calc_result["status"] = declaration.status

    stmt_events = select(TaxEvent).where(
        TaxEvent.user_id == user.id,
        TaxEvent.competencia.like(f"{ano_base}-%"),
    )
    result_events = await db.execute(stmt_events)
    events = result_events.scalars().all()

    pdf = DeclarationPDF(user, ano_base, calc_result, events)
    pdf.build()

    return pdf.output()
