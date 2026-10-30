"""
motor_inferencia.py
-------------------
Motor de Inferência Baseado em Regras com Tratamento de Incerteza e
Pontuação Ponderada para o Sistema Especialista de Carreiras em TI.

Totalmente desacoplado da Base de Conhecimento (regras_carreiras.json).
Centro Universitário Presidente Antônio Carlos - UNIPAC Barbacena
Disciplina: Inteligência Artificial
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class RegraDisparada:
    id_regra: str
    descricao: str
    condicoes_atendidas: List[str]
    efeitos: Dict[str, float]


@dataclass
class ResultadoTrilha:
    id_trilha: str
    nome: str
    descricao: str
    pontuacao_base: float
    ajustes_regras: float
    pontuacao_final: float
    certificacoes: List[str] = field(default_factory=list)
    projetos: List[Dict[str, str]] = field(default_factory=list)
    requisitos_junior: List[str] = field(default_factory=list)


@dataclass
class DiagnosticoInferencia:
    ranking: List[ResultadoTrilha]
    top_3: List[ResultadoTrilha]
    regras_acionadas: List[RegraDisparada]
    houve_empate_ou_ambiguidade: bool
    mensagem_ambiguidade: Optional[str]
    respostas_processadas: Dict[str, int]


class MotorInferencia:
    """
    Motor de Inferência com Lógica Ponderada e Fatores de Certeza.
    Lê a base de conhecimento dinâmica em JSON e calcula a matriz
    de aderência multi-trilha aplicando bônus e penalidades lógicas.
    """

    def __init__(self, caminho_json: str | Path = "regras_carreiras.json"):
        self.caminho_json = Path(caminho_json)
        self.base_conhecimento = self._carregar_base_conhecimento()
        self._validar_base()

    def _carregar_base_conhecimento(self) -> Dict[str, Any]:
        if not self.caminho_json.exists():
            raise FileNotFoundError(
                f"Arquivo da base de conhecimento não encontrado: {self.caminho_json.resolve()}"
            )
        with open(self.caminho_json, "r", encoding="utf-8") as f:
            return json.load(f)

    def _validar_base(self) -> None:
        chaves_obrigatorias = ["metadados", "perguntas", "skills", "trilhas", "regras_ajuste"]
        for chave in chaves_obrigatorias:
            if chave not in self.base_conhecimento:
                raise ValueError(f"Base de conhecimento inválida: chave obrigatória '{chave}' ausente.")

    @property
    def metadados(self) -> Dict[str, Any]:
        return self.base_conhecimento.get("metadados", {})

    @property
    def perguntas(self) -> List[Dict[str, Any]]:
        return self.base_conhecimento.get("perguntas", [])

    @property
    def skills(self) -> Dict[str, Dict[str, Any]]:
        return self.base_conhecimento.get("skills", {})

    @property
    def trilhas(self) -> Dict[str, Dict[str, Any]]:
        return self.base_conhecimento.get("trilhas", {})

    @property
    def regras_ajuste(self) -> List[Dict[str, Any]]:
        return self.base_conhecimento.get("regras_ajuste", [])

    def obter_perguntas_por_passo(self, passo: int) -> List[Dict[str, Any]]:
        return [p for p in self.perguntas if p.get("passo") == passo]

    def _normalizar_resposta(self, valor: int | float) -> float:
        """
        Converte escala Likert (1 a 5) em Fator de Certeza [0.0, 1.0].
        1 = 0.0 (Sem afinidade/certeza mínima)
        3 = 0.5 (Neutro/Moderado)
        5 = 1.0 (Afinidade máxima/certeza total)
        """
        escala = self.metadados.get("escala_resposta", {"min": 1, "max": 5})
        val_min = float(escala.get("min", 1))
        val_max = float(escala.get("max", 5))

        v_clamped = max(val_min, min(val_max, float(valor)))
        if val_max == val_min:
            return 1.0
        return (v_clamped - val_min) / (val_max - val_min)

    def _avaliar_condicao(self, cond: Dict[str, Any], respostas: Dict[str, int | float]) -> Tuple[bool, str]:
        p_id = cond["pergunta"]
        op = cond["op"]
        alvo = cond["valor"]
        val = respostas.get(p_id, 3)  # default moderado

        atendida = False
        if op == "<=":
            atendida = val <= alvo
        elif op == ">=":
            atendida = val >= alvo
        elif op == "==":
            atendida = val == alvo
        elif op == "<":
            atendida = val < alvo
        elif op == ">":
            atendida = val > alvo

        desc = f"{p_id} ({val}) {op} {alvo}"
        return atendida, desc

    def avaliar_regras_ajuste(
        self, respostas: Dict[str, int | float]
    ) -> Tuple[Dict[str, float], List[RegraDisparada]]:
        """
        Avalia as regras lógicas de penalidade e bônus da base de conhecimento.
        Retorna:
          - Dicionário com soma de ajustes em pontos percentuais por trilha
          - Lista de Regras Disparadas com justificativa
        """
        ajustes_por_trilha: Dict[str, float] = {t_id: 0.0 for t_id in self.trilhas.keys()}
        regras_disparadas: List[RegraDisparada] = []

        for regra in self.regras_ajuste:
            todas_atendidas = True
            condicoes_txt = []

            for cond in regra.get("condicoes", []):
                atendeu, txt = self._avaliar_condicao(cond, respostas)
                condicoes_txt.append(txt)
                if not atendeu:
                    todas_atendidas = False
                    break

            if todas_atendidas:
                efeitos = regra.get("efeitos", {})
                for t_id, delta in efeitos.items():
                    if t_id in ajustes_por_trilha:
                        ajustes_por_trilha[t_id] += float(delta)

                regras_disparadas.append(
                    RegraDisparada(
                        id_regra=regra.get("id", ""),
                        descricao=regra.get("descricao", ""),
                        condicoes_atendidas=condicoes_txt,
                        efeitos=efeitos,
                    )
                )

        return ajustes_por_trilha, regras_disparadas

    def calcular_compatibilidade(
        self, respostas: Dict[str, int | float]
    ) -> DiagnosticoInferencia:
        """
        Executa o processo de inferência completo:
        1. Normalização das respostas em Fatores de Certeza [0, 1].
        2. Cálculo ponderado de aderência para cada uma das 10 trilhas.
        3. Aplicação do motor de regras (penalidades de conflito e sinergias).
        4. Normalização final [0%, 100%].
        5. Identificação de empates técnicos e perfis ambíguos.
        """
        ajustes_regras, regras_disparadas = self.avaliar_regras_ajuste(respostas)
        resultados: List[ResultadoTrilha] = []

        for t_id, t_dados in self.trilhas.items():
            pesos = t_dados.get("pesos", {})

            # Soma de pesos positivos máximos possíveis para a trilha
            soma_pesos_positivos = sum(w for w in pesos.values() if w > 0)
            if soma_pesos_positivos <= 0:
                soma_pesos_positivos = 1.0

            pontuacao_acumulada = 0.0
            for p_id, peso in pesos.items():
                val_bruto = respostas.get(p_id, 3)
                fator_certeza = self._normalizar_resposta(val_bruto)
                pontuacao_acumulada += peso * fator_certeza

            # Pontuação base percentual proporcional ao máximo positivo
            pontuacao_base_pct = (pontuacao_acumulada / soma_pesos_positivos) * 100.0
            pontuacao_base_pct = max(0.0, min(100.0, pontuacao_base_pct))

            # Ajustes das regras lógicas
            delta_regras = ajustes_regras.get(t_id, 0.0)
            pontuacao_final = pontuacao_base_pct + delta_regras
            pontuacao_final = max(0.0, min(100.0, pontuacao_final))

            resultados.append(
                ResultadoTrilha(
                    id_trilha=t_id,
                    nome=t_dados.get("nome", t_id),
                    descricao=t_dados.get("descricao", ""),
                    pontuacao_base=round(pontuacao_base_pct, 1),
                    ajustes_regras=round(delta_regras, 1),
                    pontuacao_final=round(pontuacao_final, 1),
                    certificacoes=t_dados.get("certificacoes", []),
                    projetos=t_dados.get("projetos", []),
                    requisitos_junior=t_dados.get("requisitos_junior", []),
                )
            )

        # Ordenar decrescente pela pontuação final
        resultados.sort(key=lambda r: r.pontuacao_final, reverse=True)
        top_3 = resultados[:3]

        # Análise de ambiguidade / empate técnico
        limiar_empate = float(self.metadados.get("limiar_empate_pp", 5.0))
        houve_empate = False
        msg_ambiguidade = None

        if len(top_3) >= 2:
            dif_1_2 = abs(top_3[0].pontuacao_final - top_3[1].pontuacao_final)
            if dif_1_2 <= limiar_empate:
                houve_empate = True
                msg_ambiguidade = (
                    f"Perfil Híbrido / Ambíguo Detectado: A diferença de afinidade entre "
                    f"'{top_3[0].nome}' ({top_3[0].pontuacao_final}%) e "
                    f"'{top_3[1].nome}' ({top_3[1].pontuacao_final}%) é de apenas {dif_1_2:.1f} pontos percentuais "
                    f"(limiar: {limiar_empate} pp). O usuário apresenta características multidisciplinares valiosas "
                    f"que interligam essas duas áreas."
                )

        # Respostas em formato inteiro para diagnóstico
        respostas_proc = {k: int(v) for k, v in respostas.items()}

        return DiagnosticoInferencia(
            ranking=resultados,
            top_3=top_3,
            regras_acionadas=regras_disparadas,
            houve_empate_ou_ambiguidade=houve_empate,
            mensagem_ambiguidade=msg_ambiguidade,
            respostas_processadas=respostas_proc,
        )
