"""
Tax Calculator
IRPF calculations for Brazilian tax system
"""

from decimal import Decimal
from typing import Dict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tax_engine.validators import IRPFValidator
from app.shared.models.tax import Declaration, TaxEvent
from app.shared.models.user import User


# IRPF Progressive Table 2025
IRPF_TABLE_2025 = [
    {"limite": Decimal("2259.20"), "aliquota": Decimal("0.00"), "deducao": Decimal("0.00")},
    {"limite": Decimal("2826.65"), "aliquota": Decimal("0.075"), "deducao": Decimal("169.44")},
    {"limite": Decimal("3751.05"), "aliquota": Decimal("0.15"), "deducao": Decimal("381.44")},
    {"limite": Decimal("4664.68"), "aliquota": Decimal("0.225"), "deducao": Decimal("662.77")},
    {"limite": Decimal("999999999"), "aliquota": Decimal("0.275"), "deducao": Decimal("896.00")},
]


class TaxCalculator:
    """Tax calculator for IRPF"""
    
    @staticmethod
    async def calculate_irpf(
        user: User,
        ano_base: int,
        db: AsyncSession
    ) -> Dict:
        """
        Calculate IRPF for user and year
        
        Args:
            user: User
            ano_base: Tax year
            db: Database session
            
        Returns:
            Dict with calculation results
        """
        # Get tax events for year
        stmt = select(TaxEvent).where(
            TaxEvent.user_id == user.id,
            TaxEvent.competencia.like(f"{ano_base}-%")
        )
        result = await db.execute(stmt)
        events = result.scalars().all()
        
        # Sum rendimentos
        total_rendimentos = sum(
            e.valor for e in events 
            if e.categoria in ("rendimento_trabalho", "rendimento_investimento")
        )
        
        # Sum deducoes
        total_deducoes = sum(
            e.valor for e in events 
            if e.categoria in [
                "despesa_medica", "despesa_educacao", "doacao",
                "despesa_previdencia", "pensao_paga",
            ]
        )
        
        # Calculate base de calculo
        base_calculo = max(Decimal("0"), total_rendimentos - total_deducoes)
        
        # Calculate imposto devido
        imposto_devido = TaxCalculator._calculate_imposto_progressivo(base_calculo)
        
        # Get retencao (IR ja retido + DARFs pagos)
        total_retencao = sum(
            e.valor for e in events
            if e.categoria in ("imposto_retencao", "imposto_pago")
        )
        
        # Calculate restituicao ou imposto a pagar
        if total_retencao > imposto_devido:
            restituicao = total_retencao - imposto_devido
            imposto_pagar = Decimal("0")
        else:
            restituicao = Decimal("0")
            imposto_pagar = imposto_devido - total_retencao
        
        eventos_dict = [
            {"categoria": e.categoria, "valor": e.valor, "competencia": e.competencia}
            for e in events
        ]
        validacoes = IRPFValidator.validar_eventos(eventos_dict, ano_base)

        return {
            "total_rendimentos": total_rendimentos,
            "total_deducoes": total_deducoes,
            "base_calculo": base_calculo,
            "imposto_devido": imposto_devido,
            "total_retencao": total_retencao,
            "restituicao_estimada": restituicao,
            "imposto_pagar": imposto_pagar,
            "validacoes": [v.to_dict() for v in validacoes],
        }
    
    @staticmethod
    def _calculate_imposto_progressivo(base: Decimal) -> Decimal:
        """
        Calculate tax using progressive table
        
        Args:
            base: Base de cálculo
            
        Returns:
            Imposto devido
        """
        for faixa in IRPF_TABLE_2025:
            if base <= faixa["limite"]:
                imposto = (base * faixa["aliquota"]) - faixa["deducao"]
                return max(Decimal("0"), imposto)
        
        return Decimal("0")
    
    @staticmethod
    async def create_or_update_declaration(
        user: User,
        ano_base: int,
        db: AsyncSession
    ) -> Declaration:
        """
        Create or update declaration for user and year
        
        Args:
            user: User
            ano_base: Tax year
            db: Database session
            
        Returns:
            Declaration
        """
        # Check if declaration exists
        stmt = select(Declaration).where(
            Declaration.user_id == user.id,
            Declaration.ano_base == ano_base
        )
        result = await db.execute(stmt)
        declaration = result.scalar_one_or_none()
        
        # Calculate IRPF
        calc_result = await TaxCalculator.calculate_irpf(user, ano_base, db)
        
        if declaration:
            # Update existing
            declaration.restituicao_estimada = calc_result["restituicao_estimada"]
            declaration.imposto_devido = calc_result["imposto_devido"]
        else:
            # Create new
            declaration = Declaration(
                user_id=user.id,
                ano_base=ano_base,
                status="rascunho",
                restituicao_estimada=calc_result["restituicao_estimada"],
                imposto_devido=calc_result["imposto_devido"]
            )
            db.add(declaration)
        
        await db.commit()
        await db.refresh(declaration)
        
        return declaration
