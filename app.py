"""
app.py
------
Interface Web Interativa (Streamlit) para o Sistema Especialista Inteligente de Carreiras em TI.
Centro Universitário Presidente Antônio Carlos - UNIPAC Barbacena
Disciplina: Inteligência Artificial
Professor: Felipe Roncalli de Paula Carneiro
"""

import json
from pathlib import Path
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from motor_inferencia import MotorInferencia
from recomendador import RecomendadorCarreira


# Configuração inicial da página
st.set_page_config(
    page_title="Sistema Especialista em Carreiras TI | UNIPAC",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS personalizada para um design moderno e profissional
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .step-badge {
        background-color: #EEF2FF;
        color: #3730A3;
        padding: 4px 12px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .metric-card {
        background: #F9FAFB;
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #E5E7EB;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-card-top1 {
        background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%);
        border: 2px solid #6366F1;
    }
    .badge-dominada {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }
    .badge-gap {
        background-color: #FEF08A;
        color: #854D0E;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def carregar_motor_e_recomendador():
    caminho = Path("regras_carreiras.json")
    motor = MotorInferencia(caminho)
    recomendador = RecomendadorCarreira(motor)
    return motor, recomendador


motor, recomendador = carregar_motor_e_recomendador()

# Inicialização de Session State
if "passo" not in st.session_state:
    st.session_state.passo = 1

if "nome" not in st.session_state:
    st.session_state.nome = "Estudante UNIPAC"

if "horas_semanais" not in st.session_state:
    st.session_state.horas_semanais = 12

if "skills_conhecidas" not in st.session_state:
    st.session_state.skills_conhecidas = ["git", "python", "sql"]

if "respostas" not in st.session_state:
    st.session_state.respostas = {p["id"]: 3 for p in motor.perguntas}

if "trilha_selecionada_detalhes" not in st.session_state:
    st.session_state.trilha_selecionada_detalhes = None


# Barra Lateral Informativa
with st.sidebar:
    st.title("Sistema Especialista")
    st.markdown("**Consultor de Carreiras em TI**")
    st.caption("Inteligência Artificial — UNIPAC Barbacena")
    st.caption("Professor: Felipe Roncalli de Paula Carneiro")

    st.divider()

    st.subheader("Navegação em Etapas (Wizard)")
    etapas = {
        1: "1. Perfil e Habilidades Atuais",
        2: "2. Afinidades Técnicas",
        3: "3. Objetivos de Carreira",
        4: "4. Diagnóstico e Roadmap",
    }

    for num, rotulo in etapas.items():
        if st.session_state.passo == num:
            st.markdown(f"**{rotulo}** *(Etapa Atual)*")
        else:
            if st.button(rotulo, key=f"nav_btn_{num}", use_container_width=True):
                st.session_state.passo = num
                st.rerun()

    st.divider()

    # Predefinições de teste rápido (Edge Cases e Perfis Típicos)
    st.subheader("Predefinições de Teste Rápido")
    st.caption("Facilita a validação de casos limite e regras:")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("Web e Dados (Ambíguo)", use_container_width=True):
            st.session_state.respostas = {p["id"]: 2 for p in motor.perguntas}
            st.session_state.respostas.update({
                "web": 5, "design": 5, "obj_visual": 5,
                "dados": 5, "matematica": 5, "ml": 5, "obj_pesquisa": 5,
                "logica": 4, "obj_codar": 4
            })
            st.session_state.skills_conhecidas = ["git", "python", "html_css", "sql"]
            st.session_state.passo = 4
            st.rerun()

        if st.button("DevOps / SRE Clássico", use_container_width=True):
            st.session_state.respostas = {p["id"]: 2 for p in motor.perguntas}
            st.session_state.respostas.update({
                "infra": 5, "automacao": 5, "incidentes": 5,
                "obj_plantao": 5, "cloud": 5, "logica": 4
            })
            st.session_state.skills_conhecidas = ["linux", "bash", "git", "docker"]
            st.session_state.passo = 4
            st.rerun()

    with col_p2:
        if st.button("Cientista de Dados", use_container_width=True):
            st.session_state.respostas = {p["id"]: 2 for p in motor.perguntas}
            st.session_state.respostas.update({
                "matematica": 5, "dados": 5, "ml": 5, "obj_pesquisa": 5, "logica": 4
            })
            st.session_state.skills_conhecidas = ["python", "sql", "pandas", "estatistica"]
            st.session_state.passo = 4
            st.rerun()

        if st.button("Penalidade Conflito", use_container_width=True):
            st.session_state.respostas = {p["id"]: 4 for p in motor.perguntas}
            st.session_state.respostas["matematica"] = 1
            st.session_state.respostas["obj_plantao"] = 1
            st.session_state.passo = 4
            st.rerun()


# Cabeçalho Principal
st.markdown('<div class="main-title">Consultor Especialista de Carreiras e Desenvolvimento em TI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Sistema Especialista com Tratamento de Incerteza (Fatores de Certeza Likert 1-5), Pontuação Ponderada, Skill Gap Analysis e Geração de Roadmap Individualizado.</div>', unsafe_allow_html=True)

# Barra de Progresso do Wizard
progresso_val = (st.session_state.passo - 1) / 3.0
st.progress(progresso_val, text=f"Progresso: Etapa {st.session_state.passo} de 4 — {etapas[st.session_state.passo]}")
st.write("")


# ==============================================================================
# PASSO 1: PERFIL PESSOAL E BAGAGEM ATUAL
# ==============================================================================
if st.session_state.passo == 1:
    st.subheader("Passo 1: Perfil Pessoal e Conhecimento Atual")
    st.info("Informe seus dados básicos e selecione as tecnologias que você já domina no momento. O sistema usará essas informações para calcular o Skill Gap em relação aos requisitos de nível Júnior.")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.session_state.nome = st.text_input("Nome ou Identificação do Estudante/Profissional:", value=st.session_state.nome)
    with col2:
        st.session_state.horas_semanais = st.slider(
            "Horas semanais disponíveis para estudo/projetos:",
            min_value=2,
            max_value=40,
            value=st.session_state.horas_semanais,
            step=1,
            help="Utilizado para estimar a duração do seu Roadmap de estudos."
        )

    st.markdown("#### Habilidades Técnicas que você já domina:")
    st.caption("Marque todas as tecnologias/ferramentas com as quais você já tem prática ou experiência prévia:")

    # Agrupar skills por categoria
    skills_por_cat = {}
    for s_id, s_info in motor.skills.items():
        cat = s_info.get("categoria", "Geral")
        skills_por_cat.setdefault(cat, []).append((s_id, s_info["nome"]))

    selecionadas = set(st.session_state.skills_conhecidas)

    # Exibir em colunas por categoria
    cols = st.columns(2)
    cat_keys = list(skills_por_cat.keys())
    for idx, cat in enumerate(cat_keys):
        with cols[idx % 2]:
            st.markdown(f"**{cat}**")
            for s_id, s_nome in skills_por_cat[cat]:
                marcado = s_id in selecionadas
                check = st.checkbox(s_nome, value=marcado, key=f"chk_skill_{s_id}")
                if check:
                    selecionadas.add(s_id)
                else:
                    selecionadas.discard(s_id)

    st.session_state.skills_conhecidas = list(selecionadas)

    st.divider()
    col_nav1, col_nav2 = st.columns([6, 1])
    with col_nav2:
        if st.button("Próximo", type="primary", use_container_width=True):
            st.session_state.passo = 2
            st.rerun()


# ==============================================================================
# PASSO 2: AFINIDADES TÉCNICAS (LIKERT 1-5)
# ==============================================================================
elif st.session_state.passo == 2:
    st.subheader("Passo 2: Afinidades Técnicas")
    st.info("Responda ao seu grau de afinidade gradual (Escala Likert de 1 a 5) com cada uma das áreas abaixo. Não responda pensando em empregabilidade, mas sim no seu gosto genuíno.")

    perguntas_p2 = motor.obter_perguntas_por_passo(2)
    rotulos_escala = motor.metadados.get("escala_resposta", {}).get("rotulos", {
        "1": "1 - Nada",
        "2": "2 - Pouco",
        "3": "3 - Moderado",
        "4": "4 - Bastante",
        "5": "5 - Muito"
    })

    cols = st.columns(2)
    for idx, p in enumerate(perguntas_p2):
        with cols[idx % 2]:
            st.markdown(f"**{p['rotulo']}**")
            st.caption(p["texto"])
            val_atual = st.session_state.respostas.get(p["id"], 3)
            novo_val = st.select_slider(
                label=f"Afinidade com {p['rotulo']}",
                options=[1, 2, 3, 4, 5],
                value=val_atual,
                format_func=lambda x: f"{x} - {rotulos_escala.get(str(x), '')}",
                key=f"slider_{p['id']}",
                label_visibility="collapsed"
            )
            st.session_state.respostas[p["id"]] = novo_val
            st.write("")

    st.divider()
    col_b1, col_b2, col_b3 = st.columns([1, 4, 1])
    with col_b1:
        if st.button("Anterior", use_container_width=True):
            st.session_state.passo = 1
            st.rerun()
    with col_b3:
        if st.button("Próximo", type="primary", use_container_width=True):
            st.session_state.passo = 3
            st.rerun()


# ==============================================================================
# PASSO 3: OBJETIVOS DE CARREIRA E ESTILO DE TRABALHO
# ==============================================================================
elif st.session_state.passo == 3:
    st.subheader("Passo 3: Objetivos de Carreira e Estilo de Trabalho")
    st.info("Aqui avaliamos preferências de rotina, tolerância a certas responsabilidades e aspirações futuras. Essas preferências ativam regras lógicas de sinergia ou penalidade.")

    perguntas_p3 = motor.obter_perguntas_por_passo(3)
    rotulos_escala = motor.metadados.get("escala_resposta", {}).get("rotulos", {
        "1": "1 - Nada",
        "2": "2 - Pouco",
        "3": "3 - Moderado",
        "4": "4 - Bastante",
        "5": "5 - Muito"
    })

    for p in perguntas_p3:
        st.markdown(f"**{p['rotulo']}**")
        st.caption(p["texto"])
        val_atual = st.session_state.respostas.get(p["id"], 3)
        novo_val = st.select_slider(
            label=f"Grau de acordo com {p['rotulo']}",
            options=[1, 2, 3, 4, 5],
            value=val_atual,
            format_func=lambda x: f"{x} - {rotulos_escala.get(str(x), '')}",
            key=f"slider_{p['id']}",
            label_visibility="collapsed"
        )
        st.session_state.respostas[p["id"]] = novo_val
        st.write("")

    st.divider()
    col_b1, col_b2, col_b3 = st.columns([1, 4, 1])
    with col_b1:
        if st.button("Anterior", use_container_width=True):
            st.session_state.passo = 2
            st.rerun()
    with col_b3:
        if st.button("Calcular Diagnóstico", type="primary", use_container_width=True):
            st.session_state.passo = 4
            st.rerun()


# ==============================================================================
# PASSO 4: DIAGNÓSTICO DO SISTEMA ESPECIALISTA & PLANO DE AÇÃO
# ==============================================================================
elif st.session_state.passo == 4:
    # Executa o Motor de Inferência
    diagnostico = motor.calcular_compatibilidade(st.session_state.respostas)
    top_3 = diagnostico.top_3
    vencedora = top_3[0]

    st.subheader(f"Diagnóstico Especialista para {st.session_state.nome}")

    # Alerta de Perfil Híbrido / Ambíguo (Caso Limite tratado no PDF)
    if diagnostico.houve_empate_ou_ambiguidade:
        st.warning(f"Atenção: {diagnostico.mensagem_ambiguidade}")

    # CARDS DO TOP 3
    st.markdown("### Top 3 Carreiras Recomendadas")
    col_top1, col_top2, col_top3 = st.columns(3)

    with col_top1:
        st.markdown(
            f"""
            <div class="metric-card metric-card-top1">
                <span class="step-badge">1º Lugar Recomendado</span>
                <h3 style="margin-top:8px; margin-bottom:4px; color:#1E1B4B;">{top_3[0].nome}</h3>
                <h1 style="color:#4338CA; margin:0;">{top_3[0].pontuacao_final}%</h1>
                <p style="font-size:0.85rem; color:#4B5563; margin-top:6px;">{top_3[0].descricao}</p>
                <small style="color:#6B7280;">Base: {top_3[0].pontuacao_base}% | Regras: {top_3[0].ajustes_regras:+0.1f} pp</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_top2:
        st.markdown(
            f"""
            <div class="metric-card">
                <span class="step-badge" style="background:#F3F4F6; color:#374151;">2º Lugar</span>
                <h3 style="margin-top:8px; margin-bottom:4px; color:#111827;">{top_3[1].nome}</h3>
                <h1 style="color:#374151; margin:0;">{top_3[1].pontuacao_final}%</h1>
                <p style="font-size:0.85rem; color:#4B5563; margin-top:6px;">{top_3[1].descricao}</p>
                <small style="color:#6B7280;">Base: {top_3[1].pontuacao_base}% | Regras: {top_3[1].ajustes_regras:+0.1f} pp</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_top3:
        st.markdown(
            f"""
            <div class="metric-card">
                <span class="step-badge" style="background:#F3F4F6; color:#374151;">3º Lugar</span>
                <h3 style="margin-top:8px; margin-bottom:4px; color:#111827;">{top_3[2].nome}</h3>
                <h1 style="color:#374151; margin:0;">{top_3[2].pontuacao_final}%</h1>
                <p style="font-size:0.85rem; color:#4B5563; margin-top:6px;">{top_3[2].descricao}</p>
                <small style="color:#6B7280;">Base: {top_3[2].pontuacao_base}% | Regras: {top_3[2].ajustes_regras:+0.1f} pp</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.divider()

    # VISUALIZAÇÕES GRÁFICAS: BARRAS HORIZONTAIS E RADAR
    st.markdown("### Matriz Completa de Compatibilidade (10 Trilhas)")
    tab_graf1, tab_graf2, tab_tabela = st.tabs(["Gráfico de Barras", "Gráfico de Radar", "Tabela Detalhada"])

    df_ranking = pd.DataFrame([
        {
            "Trilha": t.nome,
            "Compatibilidade (%)": t.pontuacao_final,
            "Pontuação Base (%)": t.pontuacao_base,
            "Ajustes Lógicos (pp)": t.ajustes_regras,
            "ID": t.id_trilha,
        }
        for t in diagnostico.ranking
    ])

    with tab_graf1:
        fig_bar = px.bar(
            df_ranking.sort_values("Compatibilidade (%)", ascending=True),
            x="Compatibilidade (%)",
            y="Trilha",
            orientation="h",
            color="Compatibilidade (%)",
            color_continuous_scale="Blues",
            range_x=[0, 100],
            text="Compatibilidade (%)",
            title="Aderência Percentual Ponderada por Trilha de Tecnologia"
        )
        fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_bar.update_layout(height=450, margin=dict(l=20, r=40, t=40, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab_graf2:
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=df_ranking["Compatibilidade (%)"].tolist() + [df_ranking["Compatibilidade (%)"].iloc[0]],
            theta=df_ranking["Trilha"].tolist() + [df_ranking["Trilha"].iloc[0]],
            fill='toself',
            name='Compatibilidade',
            line=dict(color='#4F46E5', width=2),
            fillcolor='rgba(79, 70, 229, 0.25)'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            showlegend=False,
            height=450,
            margin=dict(l=40, r=40, t=40, b=40),
            title="Diagrama de Radar de Afinidade Multifacetada"
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with tab_tabela:
        st.dataframe(
            df_ranking[["Trilha", "Compatibilidade (%)", "Pontuação Base (%)", "Ajustes Lógicos (pp)"]],
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # MOTOR DE REGRAS DISPARADAS (EXPLICABILIDADE DO SISTEMA ESPECIALISTA)
    st.markdown("### Motor de Inferência: Regras e Ajustes Aplicados")
    st.caption("Conforme a especificação do Sistema Especialista, as regras lógicas avaliam inconsistências ou sinergias:")

    if diagnostico.regras_acionadas:
        for r in diagnostico.regras_acionadas:
            with st.expander(f"Regra: {r.id_regra} — {r.descricao}", expanded=False):
                st.markdown(f"- **Condições avaliadas:** `{', '.join(r.condicoes_atendidas)}`")
                st.markdown(f"- **Efeitos nos percentuais:** `{r.efeitos}`")
    else:
        st.success("Nenhuma penalidade ou regra de ajuste especial foi acionada para as respostas fornecidas.")

    st.divider()

    # SELETOR DE TRILHA PARA ANÁLISE DE SKILL GAP E ROADMAP
    st.markdown("### Análise de Skill Gap e Roadmap para Nível Júnior")
    st.caption("Por padrão analisamos a trilha recomendada em 1º lugar, mas você pode selecionar qualquer trilha do ranking para análise:")

    nomes_trilhas = {t.nome: t.id_trilha for t in diagnostico.ranking}
    trilha_escolhida_nome = st.selectbox(
        "Selecione a trilha para detalhamento do Roadmap:",
        options=list(nomes_trilhas.keys()),
        index=0
    )
    trilha_alvo_id = nomes_trilhas[trilha_escolhida_nome]
    posicao_ranking = next(idx + 1 for idx, t in enumerate(diagnostico.ranking) if t.id_trilha == trilha_alvo_id)
    trilha_obj = next(t for t in diagnostico.ranking if t.id_trilha == trilha_alvo_id)

    # Executa Análise de Gaps
    relatorio_gap = recomendador.analisar_gaps(
        trilha_id=trilha_alvo_id,
        skills_conhecidas=st.session_state.skills_conhecidas,
        horas_semanais=st.session_state.horas_semanais
    )

    # Indicadores de Prontidão
    col_gap1, col_gap2, col_gap3, col_gap4 = st.columns(4)
    with col_gap1:
        st.metric("Prontidão para Júnior", f"{relatorio_gap.prontidao_junior_pct}%")
    with col_gap2:
        st.metric("Competências Requeridas", f"{relatorio_gap.total_requisitos}")
    with col_gap3:
        st.metric("Lacunas a Desenvolver (Gaps)", f"{relatorio_gap.total_faltantes}")
    with col_gap4:
        st.metric("Tempo Estimado de Estudo", f"{relatorio_gap.horas_totais_estudo}h (~{relatorio_gap.semanas_estimadas} sem)")

    # Barra visual de prontidão
    st.progress(relatorio_gap.prontidao_junior_pct / 100.0)

    # Divisão de Competências Dominadas vs Faltantes
    col_hab1, col_hab2 = st.columns(2)
    with col_hab1:
        st.markdown("#### Competências já dominadas:")
        if relatorio_gap.skills_dominadas:
            for s in relatorio_gap.skills_dominadas:
                st.markdown(f'<span class="badge-dominada">[OK] {s.nome} ({s.categoria})</span>', unsafe_allow_html=True)
        else:
            st.write("*Nenhuma das competências essenciais foi marcada como dominada ainda.*")

    with col_hab2:
        st.markdown("#### Competências Faltantes (Skill Gaps):")
        if relatorio_gap.skills_faltantes:
            for s in relatorio_gap.skills_faltantes:
                st.markdown(f'<span class="badge-gap">[Pendente] {s.nome} ({s.categoria} — {s.horas_estimadas}h)</span>', unsafe_allow_html=True)
        else:
            st.success("Você já possui todas as competências essenciais para uma posição Júnior nesta trilha.")

    st.write("")

    # ROADMAP DE ESTUDOS
    st.markdown("#### Sequência Pedagógica Recomendada de Estudos:")
    if relatorio_gap.skills_faltantes:
        for i, s in enumerate(relatorio_gap.skills_faltantes, start=1):
            prioridade_rotulo = "Prioridade Alta (Fundamento)" if s.prioridade == 1 else "Especialização Técnica"
            st.markdown(f"**Passo {i}: {s.nome}** — `{s.categoria}` | Estimativa: **{s.horas_estimadas} horas** | *{prioridade_rotulo}*")
    else:
        st.info("Com todas as bases adquiridas, dedique-se aos projetos práticos e certificações abaixo.")

    # CERTIFICAÇÕES RECOMENDADAS
    st.markdown("#### Certificações Estratégicas para o Mercado:")
    for cert in relatorio_gap.certificacoes_sugeridas:
        st.markdown(f"- **{cert}**")

    # PROJETOS DE PORTFÓLIO GITHUB
    st.markdown("#### Projetos Recomendados para Portfólio no GitHub:")
    for p in relatorio_gap.projetos_portfolio:
        with st.container():
            st.markdown(f"**{p.get('titulo')}**")
            st.write(p.get("descricao"))

    st.divider()

    # EXPORTAÇÃO DO RELATÓRIO
    relatorio_md = recomendador.gerar_markdown_relatorio(
        relatorio=relatorio_gap,
        nome_usuario=st.session_state.nome,
        posicao_ranking=posicao_ranking,
        compatibilidade_pct=trilha_obj.pontuacao_final
    )

    col_exp1, col_exp2 = st.columns([2, 1])
    with col_exp1:
        st.markdown("##### Exportar Plano de Carreira e Diagnóstico:")
        st.download_button(
            label="Baixar Relatório Completo (.md)",
            data=relatorio_md,
            file_name=f"plano_carreira_{trilha_alvo_id}_{st.session_state.nome.lower().replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col_exp2:
        if st.button("Reiniciar Diagnóstico", use_container_width=True):
            st.session_state.passo = 1
            st.rerun()

    st.divider()
    col_nav1, col_nav2 = st.columns([1, 6])
    with col_nav1:
        if st.button("Revisar Respostas", use_container_width=True):
            st.session_state.passo = 3
            st.rerun()
