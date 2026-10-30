"""
test_sistema_especialista.py
----------------------------
Suíte de testes de robustez, casos limite (edge cases) e regras de inferência
para o Sistema Especialista de Carreiras em TI.
"""

import pytest
from motor_inferencia import MotorInferencia
from recomendador import RecomendadorCarreira


@pytest.fixture
def motor():
    return MotorInferencia("regras_carreiras.json")


@pytest.fixture
def recomendador(motor):
    return RecomendadorCarreira(motor)


class TestIntegridadeBaseConhecimento:
    """Verifica a consistência e desacoplamento da base de conhecimento JSON."""

    def test_quantidade_de_trilhas(self, motor):
        trilhas = motor.trilhas
        # Requisito do PDF: 10 principais trilhas de tecnologia
        assert len(trilhas) == 10
        trilhas_esperadas = {
            "backend", "frontend_ux", "cientista_dados", "engenheiro_dados",
            "ciberseguranca", "devops_sre", "cloud_architecture", "mobile",
            "qa", "product_management"
        }
        assert set(trilhas.keys()) == trilhas_esperadas

    def test_todas_as_skills_requeridas_existem(self, motor):
        todas_skills = set(motor.skills.keys())
        for t_id, t_dados in motor.trilhas.items():
            reqs = t_dados.get("requisitos_junior", [])
            for r in reqs:
                assert r in todas_skills, f"Skill '{r}' da trilha '{t_id}' não está definida na lista de skills."

    def test_todas_as_perguntas_das_regras_existem(self, motor):
        ids_perguntas = {p["id"] for p in motor.perguntas}
        for regra in motor.regras_ajuste:
            for cond in regra.get("condicoes", []):
                p_id = cond["pergunta"]
                assert p_id in ids_perguntas, f"Pergunta '{p_id}' da regra '{regra.get('id')}' não existe."


class TestMotorInferencia:
    """Testa os cálculos de pontuação ponderada, Fatores de Certeza e regras lógicas."""

    def test_respostas_todas_minimas(self, motor):
        """Caso Limite: Usuário responde '1' (Nada) para todas as perguntas."""
        respostas = {p["id"]: 1 for p in motor.perguntas}
        diag = motor.calcular_compatibilidade(respostas)

        assert len(diag.ranking) == 10
        # Todas as pontuações devem ser 0% (ou muito baixas por penalidades aplicadas)
        for t in diag.ranking:
            assert 0.0 <= t.pontuacao_final <= 100.0
            assert t.pontuacao_base == 0.0

    def test_respostas_todas_maximas(self, motor):
        """Caso Limite: Usuário responde '5' (Muito) para todas as perguntas."""
        respostas = {p["id"]: 5 for p in motor.perguntas}
        diag = motor.calcular_compatibilidade(respostas)

        assert len(diag.ranking) == 10
        for t in diag.ranking:
            assert 0.0 <= t.pontuacao_final <= 100.0
        # Com todas 5, as regras de sinergia ativam, e as pontuações ficam muito altas
        assert diag.top_3[0].pontuacao_final >= 90.0

    def test_perfil_especifico_backend(self, motor):
        """Usuário com perfil focado estritamente em APIs, lógica e código."""
        respostas = {p["id"]: 1 for p in motor.perguntas}
        respostas.update({
            "logica": 5,
            "apis": 5,
            "obj_codar": 5,
            "automacao": 4,
            "pipelines": 4,
            "cloud": 3,
            "matematica": 3
        })
        diag = motor.calcular_compatibilidade(respostas)
        # Back-end deve estar no topo
        assert diag.top_3[0].id_trilha == "backend"
        assert diag.top_3[0].pontuacao_final > 80.0

    def test_perfil_especifico_cientista_dados(self, motor):
        """Usuário apaixonado por matemática, dados e machine learning."""
        respostas = {p["id"]: 1 for p in motor.perguntas}
        respostas.update({
            "matematica": 5,
            "dados": 5,
            "ml": 5,
            "obj_pesquisa": 5,
            "logica": 4,
            "comunicacao": 3
        })
        diag = motor.calcular_compatibilidade(respostas)
        assert diag.top_3[0].id_trilha == "cientista_dados"
        assert diag.top_3[0].pontuacao_final > 85.0

    def test_penalidade_sem_matematica_para_data_science(self, motor):
        """Regra r_sem_matematica: matemática <= 2 deve penalizar cientista_dados em 20 pp."""
        respostas = {p["id"]: 4 for p in motor.perguntas}
        respostas["matematica"] = 1  # Conflito intencional

        diag = motor.calcular_compatibilidade(respostas)
        regras_ids = [r.id_regra for r in diag.regras_acionadas]
        assert "r_sem_matematica" in regras_ids

        cd_result = next(t for t in diag.ranking if t.id_trilha == "cientista_dados")
        assert cd_result.ajustes_regras <= -20.0

    def test_penalidade_sem_plantao_para_devops(self, motor):
        """Regra r_sem_plantao: obj_plantao <= 1 deve penalizar devops_sre em 15 pp."""
        respostas = {p["id"]: 3 for p in motor.perguntas}
        respostas["obj_plantao"] = 1  # Recusa on-call

        diag = motor.calcular_compatibilidade(respostas)
        regras_ids = [r.id_regra for r in diag.regras_acionadas]
        assert "r_sem_plantao" in regras_ids

        devops_result = next(t for t in diag.ranking if t.id_trilha == "devops_sre")
        assert devops_result.ajustes_regras == -15.0

    def test_perfil_ambiguo_web_e_dados(self, motor):
        """
        Requisito do PDF (Fase 5): Testar perfis ambíguos (ex: alguém que gosta
        tanto de dados quanto de desenvolvimento web) para verificar se o sistema
        lida bem com empates parciais e apresenta justificativas coerentes.
        """
        respostas = {p["id"]: 1 for p in motor.perguntas}
        # Usuário dá notas altas iguais tanto para Web/Front quanto para Ciência de Dados
        respostas.update({
            "design": 5,
            "web": 5,
            "obj_visual": 5,
            "matematica": 5,
            "dados": 5,
            "ml": 5,
            "obj_pesquisa": 5,
            "logica": 4,
            "obj_codar": 4,
            "comunicacao": 4,
        })
        diag = motor.calcular_compatibilidade(respostas)

        # O sistema deve calcular Top 3 com pontuações consistentes
        assert len(diag.top_3) == 3
        top_ids = [t.id_trilha for t in diag.top_3]
        assert "frontend_ux" in top_ids or "cientista_dados" in top_ids

        # Verifica se o mecanismo de detecção de empate/ambiguidade é ativado se a diferença for pequena
        dif = abs(diag.top_3[0].pontuacao_final - diag.top_3[1].pontuacao_final)
        if dif <= motor.metadados.get("limiar_empate_pp", 5.0):
            assert diag.houve_empate_ou_ambiguidade is True
            assert diag.mensagem_ambiguidade is not None
            assert "Perfil Híbrido" in diag.mensagem_ambiguidade


class TestRecomendadorSkillGap:
    """Testa a análise de gaps e geração de roadmap."""

    def test_skill_gap_sem_nenhuma_skill(self, recomendador):
        relatorio = recomendador.analisar_gaps("backend", skills_conhecidas=[])
        assert relatorio.total_requisitos == len(relatorio.skills_faltantes)
        assert relatorio.total_dominadas == 0
        assert relatorio.prontidao_junior_pct == 0.0
        assert relatorio.horas_totais_estudo > 0
        assert len(relatorio.certificacoes_sugeridas) > 0
        assert len(relatorio.projetos_portfolio) > 0

    def test_skill_gap_com_todas_as_skills(self, recomendador, motor):
        trilha_backend = motor.trilhas["backend"]
        todas_reqs = trilha_backend["requisitos_junior"]

        relatorio = recomendador.analisar_gaps("backend", skills_conhecidas=todas_reqs)
        assert relatorio.total_dominadas == len(todas_reqs)
        assert relatorio.total_faltantes == 0
        assert relatorio.prontidao_junior_pct == 100.0
        assert relatorio.horas_totais_estudo == 0
        assert relatorio.semanas_estimadas == 0.0

    def test_skill_gap_parcial(self, recomendador):
        # Usuário domina git e python apenas
        relatorio = recomendador.analisar_gaps("backend", skills_conhecidas=["git", "python"], horas_semanais=10)
        assert relatorio.total_dominadas == 2
        assert relatorio.prontidao_junior_pct > 0.0 and relatorio.prontidao_junior_pct < 100.0
        assert relatorio.semanas_estimadas > 0.0

    def test_geracao_relatorio_markdown(self, recomendador):
        relatorio = recomendador.analisar_gaps("backend", skills_conhecidas=["git", "python"])
        texto_md = recomendador.gerar_markdown_relatorio(
            relatorio=relatorio,
            nome_usuario="Carlos Silva",
            posicao_ranking=1,
            compatibilidade_pct=88.5
        )
        assert "Carlos Silva" in texto_md
        assert "Back-end" in texto_md
        assert "Skill Gap" in texto_md
        assert "Certificações Recomendadas" in texto_md
        assert "Projetos Estratégicos" in texto_md
