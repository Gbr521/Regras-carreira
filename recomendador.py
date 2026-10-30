"""
recomendador.py
---------------
Módulo de Recomendação de Skill Gaps, Roadmap de Aprendizado e Portfólio.
Analisa as lacunas de conhecimento do usuário em relação aos requisitos de nível Júnior
da trilha selecionada e gera um plano de ação completo e estruturado.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set
from motor_inferencia import MotorInferencia


@dataclass
class ItemSkill:
    id_skill: str
    nome: str
    categoria: str
    horas_estimadas: int
    prioridade: int  # 1 = Alta (Fundacional), 2 = Média, 3 = Especialização


@dataclass
class RelatorioSkillGap:
    trilha_id: str
    trilha_nome: str
    total_requisitos: int
    total_dominadas: int
    total_faltantes: int
    prontidao_junior_pct: float
    skills_dominadas: List[ItemSkill]
    skills_faltantes: List[ItemSkill]
    horas_totais_estudo: int
    semanas_estimadas: float
    certificacoes_sugeridas: List[str]
    projetos_portfolio: List[Dict[str, str]]


class RecomendadorCarreira:
    """
    Analisa os Skill Gaps e gera o Roadmap de Carreira para o nível Júnior.
    """

    # Categorias organizadas por ordem pedagógica recomendada
    ORDEM_PEDAGOGICA = {
        "Programação": 1,
        "Front-end e Design": 2,
        "Dados": 2,
        "Infra e DevOps": 2,
        "Cloud": 3,
        "Segurança": 3,
        "Qualidade": 3,
        "Produto e Gestão": 2,
    }

    def __init__(self, motor: MotorInferencia):
        self.motor = motor

    def _obter_item_skill(self, id_skill: str) -> ItemSkill:
        dados = self.motor.skills.get(id_skill, {})
        categoria = dados.get("categoria", "Geral")
        prioridade = self.ORDEM_PEDAGOGICA.get(categoria, 2)
        return ItemSkill(
            id_skill=id_skill,
            nome=dados.get("nome", id_skill),
            categoria=categoria,
            horas_estimadas=int(dados.get("horas", 20)),
            prioridade=prioridade,
        )

    def analisar_gaps(
        self,
        trilha_id: str,
        skills_conhecidas: List[str] | Set[str],
        horas_semanais: int = 10,
    ) -> RelatorioSkillGap:
        """
        Cruza os requisitos para nível Júnior da trilha com as habilidades
        que o usuário declarou possuir.
        """
        trilha = self.motor.trilhas.get(trilha_id)
        if not trilha:
            raise KeyError(f"Trilha '{trilha_id}' não encontrada na base de conhecimento.")

        requisitos_ids: List[str] = trilha.get("requisitos_junior", [])
        conhecidas_set = set(skills_conhecidas)

        dominadas: List[ItemSkill] = []
        faltantes: List[ItemSkill] = []

        for req_id in requisitos_ids:
            item = self._obter_item_skill(req_id)
            if req_id in conhecidas_set:
                dominadas.append(item)
            else:
                faltantes.append(item)

        # Ordenar as faltantes pedagogicamente (prioridade -> horas)
        faltantes.sort(key=lambda s: (s.prioridade, s.horas_estimadas))

        total_requisitos = len(requisitos_ids)
        total_dominadas = len(dominadas)
        total_faltantes = len(faltantes)

        if total_requisitos > 0:
            prontidao = round((total_dominadas / total_requisitos) * 100.0, 1)
        else:
            prontidao = 100.0

        horas_totais = sum(s.horas_estimadas for s in faltantes)
        horas_semana_segura = max(1, horas_semanais)
        semanas_estimadas = round(horas_totais / horas_semana_segura, 1)

        return RelatorioSkillGap(
            trilha_id=trilha_id,
            trilha_nome=trilha.get("nome", trilha_id),
            total_requisitos=total_requisitos,
            total_dominadas=total_dominadas,
            total_faltantes=total_faltantes,
            prontidao_junior_pct=prontidao,
            skills_dominadas=dominadas,
            skills_faltantes=faltantes,
            horas_totais_estudo=horas_totais,
            semanas_estimadas=semanas_estimadas,
            certificacoes_sugeridas=trilha.get("certificacoes", []),
            projetos_portfolio=trilha.get("projetos", []),
        )

    def gerar_markdown_relatorio(
        self,
        relatorio: RelatorioSkillGap,
        nome_usuario: str = "Candidato(a)",
        posicao_ranking: int = 1,
        compatibilidade_pct: float = 0.0,
    ) -> str:
        """
        Gera um relatório completo e formatado em Markdown para exportação ou exibição.
        """
        md = []
        md.append(f"# Plano de Desenvolvimento Individual (PDI) - Nível Júnior")
        md.append(f"**Profissional:** {nome_usuario}")
        md.append(f"**Trilha Alvo:** {relatorio.trilha_nome} (#{posicao_ranking} com {compatibilidade_pct:.1f}% de aderência)")
        md.append(f"**Prontidão Técnica Atual:** {relatorio.prontidao_junior_pct}%")
        md.append(f"**Tempo Estimado:** {relatorio.horas_totais_estudo} horas (~{relatorio.semanas_estimadas} semanas)\n")

        md.append("## 1. Diagnóstico de Competências (Skill Gap)")
        if relatorio.skills_dominadas:
            md.append("### Competências Já Dominadas:")
            for s in relatorio.skills_dominadas:
                md.append(f"- **{s.nome}** ({s.categoria})")
        else:
            md.append("*Nenhuma das competências essenciais de nível Júnior foi marcada como previamente dominada.*")

        md.append("\n### Lacunas de Competências a Desenvolver (Gaps):")
        if relatorio.skills_faltantes:
            for i, s in enumerate(relatorio.skills_faltantes, start=1):
                md.append(f"{i}. **{s.nome}** ({s.categoria}) — Carga estimada: {s.horas_estimadas}h")
        else:
            md.append("*Você já domina todas as competências essenciais para a posição Júnior nesta trilha.*")

        md.append("\n## 2. Certificações Recomendadas para o Mercado")
        for cert in relatorio.certificacoes_sugeridas:
            md.append(f"- {cert}")

        md.append("\n## 3. Projetos Estratégicos para o Portfólio GitHub")
        for proj in relatorio.projetos_portfolio:
            md.append(f"### {proj.get('titulo')}")
            md.append(f"{proj.get('descricao')}\n")

        return "\n".join(md)
