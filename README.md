# Sistema Especialista Inteligente para Mapeamento, Compatibilidade e Trilha de Carreira em TI

**Centro Universitário Presidente Antônio Carlos — UNIPAC Barbacena**  
**Disciplina:** Inteligência Artificial  
**Curso:** Ciência da Computação  
**Professor:** Felipe Roncalli de Paula Carneiro  

---

## 1. Contextualização e Objetivo

O desenvolvimento clássico de Sistemas Especialistas muitas vezes esbarra na rigidez das regras SE-ENTÃO tradicionais. O objetivo deste projeto é implementar um **Sistema Especialista Baseado em Regras com Tratamento de Incerteza e Pontuação Ponderada** em Python, atuando como um **Consultor Avançado de Carreiras e Desenvolvimento Profissional em TI**.

O sistema:
1. Analisa o perfil multifacetado do usuário lidando com **respostas graduais em escala Likert (1 a 5)**.
2. Mapeia a afinidade em relação às **10 principais trilhas de tecnologia**:
   - Back-end
   - Front-end/UX
   - Cientista de Dados
   - Engenheiro de Dados
   - Cibersegurança
   - DevOps/SRE
   - Cloud Architecture
   - Mobile
   - QA
   - Product Management
3. Retorna um **Top 3 de carreiras recomendadas** e a matriz completa de compatibilidade percentual [0% a 100%].
4. Trata **perfis ambíguos e empates técnicos** (diferença <= 5 pp), apresentando diagnóstico da sinergia entre áreas.
5. Executa **Análise de Lacunas de Competências (Skill Gap Analysis)** para atingir o nível **Júnior** na trilha recomendada.
6. Gera um **Roadmap Personalizado**, indicando ordem pedagógica de estudo, estimativa de horas e semanas, certificações recomendadas e projetos estratégicos para portfólio no GitHub.

---

## 2. Arquitetura e Desacoplamento

O projeto foi rigorosamente estruturado com separação clara de responsabilidades:

```text
├── regras_carreiras.json         # Base de Conhecimento desacoplada (pesos, regras de conflito, skills e trilhas)
├── motor_inferencia.py           # Motor de Inferência (Fatores de Certeza, soma ponderada, regras de ajuste e Top 3)
├── recomendador.py               # Módulo de Skill Gap Analysis, estimativa de prazos e Roadmap de estudos
├── app.py                        # Interface Web Interativa Streamlit (fluxo Wizard em 4 etapas e gráficos Plotly)
├── test_sistema_especialista.py  # Suíte de testes automatizados com pytest (robusteza e edge cases)
├── requirements.txt              # Dependências do projeto
├── run_app.sh                    # Script utilitário para execução imediata
└── README.md                     # Documentação completa
```

### Como Funciona o Motor de Inferência (motor_inferencia.py)
1. **Normalização Likert para Fator de Certeza:**
   $$CF(u) = \frac{u - 1}{4.0} \in [0.0, 1.0]$$
   - 1 (Nada) -> 0.0
   - 3 (Moderado) -> 0.5
   - 5 (Muito) -> 1.0
2. **Pontuação Ponderada Base:**
   Para cada trilha T com pesos w_i, calcula-se:
   $$S_{base}(T) = \max\left(0, \min\left(100, \frac{\sum w_i \cdot CF(u_i)}{\sum_{w_k > 0} w_k} \times 100\right)\right)$$
3. **Regras Lógicas de Ajuste (regras_ajuste):**
   Regras de produção SE-ENTÃO aplicam penalidades por incompatibilidade e bônus por sinergia:
   - Exemplo de Penalidade: Baixa afinidade com matemática (<= 2) penaliza Ciência de Dados em -20 pp (`r_sem_matematica`).
   - Exemplo de Penalidade: Recusa de plantões on-call (<= 1) penaliza DevOps/SRE em -15 pp (`r_sem_plantao`).
   - Exemplo de Sinergia: Afinidade conjunta por dados e pipelines (>= 4) bonifica Engenharia de Dados em +8 pp (`r_dados_e_pipelines`).
4. **Tratamento de Incerteza e Perfis Ambíguos:**
   Se a diferença entre o 1º e o 2º colocado for menor ou igual ao limiar configurado (`limiar_empate_pp = 5.0`), o sistema diagnostica um perfil híbrido e orienta o estudante sobre áreas de convergência.

---

## 3. Como Executar

### Pré-requisitos
- Python 3.10 ou superior (testado com Python 3.14).

### Passo a Passo

1. **Criar e Ativar Ambiente Virtual:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. **Instalar Dependências:**
```bash
pip install -r requirements.txt
```

3. **Executar a Interface Web (Streamlit):**
```bash
./run_app.sh
# ou diretamente:
streamlit run app.py
```
Acesse a aplicação no navegador em: `http://localhost:8501`.

---

## 4. Execução dos Testes Automatizados (Fase 5)

A suíte de testes cobre a integridade da base de conhecimento, casos limite e regras lógicas:

```bash
pytest -v test_sistema_especialista.py
```

### Casos de Teste Inclusos:
- **Integridade da Base:** Validação das 10 trilhas, integridade relacional entre perguntas, trilhas e catálogo de skills.
- **Caso Limite - Mínimo:** Todas as respostas em 1 (Nada) gerando compatibilidade 0%.
- **Caso Limite - Máximo:** Todas as respostas em 5 (Muito) ativando sinergias e pontuações máximas.
- **Perfil Ambíguo (Edge Case):** Teste de candidato com alta afinidade simultânea em Web e Dados, validando o mecanismo de detecção de empates e justificativas.
- **Penalidades Lógicas:** Validação do disparo de regras conflitantes (`r_sem_matematica`, `r_sem_plantao`).
- **Skill Gap Analysis:** Cenários com 0% de prontidão, prontidão parcial e 100% de prontidão júnior.
- **Geração de Relatório:** Validação da estrutura Markdown do PDI exportável.

---

## 5. Interface em Etapas (Wizard)

- **Passo 1: Perfil Pessoal e Bagagem Atual:** Coleta nome, disponibilidade semanal e checklist de tecnologias já dominadas.
- **Passo 2: Afinidades Técnicas:** Sliders com escala Likert (1 a 5) para preferências de programação, matemática, UX, nuvem, segurança, etc.
- **Passo 3: Objetivos de Carreira:** Preferências de rotina (código, liderança, pesquisa, resposta a incidentes e plantões).
- **Passo 4: Diagnóstico Especialista e Plano de Ação:**
  - Cards interativos do Top 3 com justificativas.
  - Gráficos de **Barras Horizontais** e **Radar** (Plotly).
  - Painel de transparência das **Regras Disparadas** pelo motor de inferência.
  - **Skill Gap Analysis** comparando competências dominadas vs faltantes.
  - **Roadmap Pedagógico** com previsão de carga horária e cronograma semanal.
  - Certificações recomendadas e projetos para portfólio GitHub.
  - Botão para download do relatório completo em Markdown (`.md`).
