# -*- coding: utf-8 -*-
"""
FIGURAS DE SÍNTESE
===================
Três figuras que não pertencem a um exercício específico, mas amarram o
conjunto:

  * mapa_matrizes.png        as seis matrizes canônicas usadas nos exercícios
  * sintese_propriedades.png o que cada transformação preserva e o que destrói
  * nao_comutatividade.png   por que a ORDEM da composição altera o resultado
  * painel_exercicios.png    as dez figuras em uma folha só
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

import transformacoes as tg
import plotagem as pl

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida"


# --------------------------------------------------------------------------


def mapa_matrizes():
    """Cartão de referência: as seis matrizes 3x3 em coordenadas homogêneas."""
    fig, ax = plt.subplots(figsize=(13.6, 8.4))
    ax.axis("off")

    MATRIZES = [
        ("TRANSLAÇÃO   T(tx, ty)",
         [["1", "0", "tx"], ["0", "1", "ty"], ["0", "0", "1"]],
         "x' = x + tx\ny' = y + ty",
         "det = 1 · a única NÃO linear:\nsó existe como matriz 3x3",
         pl.VERDE, "exercícios 1, 9, 10"),
        ("ESCALA   S(sx, sy)",
         [["sx", "0", "0"], ["0", "sy", "0"], ["0", "0", "1"]],
         "x' = sx · x\ny' = sy · y",
         "det = sx·sy · em relação à ORIGEM:\nescalar também afasta a figura",
         pl.AZUL, "exercícios 2, 3, 9, 10"),
        ("ROTAÇÃO   R(θ)",
         [["cos θ", "-sen θ", "0"], ["sen θ", "cos θ", "0"], ["0", "0", "1"]],
         "x' = x·cos θ - y·sen θ\ny' = x·sen θ + y·cos θ",
         "det = 1 · θ > 0 é anti-horário;\ngira em torno da ORIGEM",
         pl.LARANJA, "exercícios 4, 5, 9"),
        ("REFLEXÃO no eixo x   Fx",
         [["1", "0", "0"], ["0", "-1", "0"], ["0", "0", "1"]],
         "x' = x\ny' = -y",
         "det = -1 · o sinal negativo\nINVERTE a orientação",
         pl.ROXO, "exercício 7"),
        ("REFLEXÃO no eixo y   Fy",
         [["-1", "0", "0"], ["0", "1", "0"], ["0", "0", "1"]],
         "x' = -x\ny' = y",
         "det = -1 · espelha a coordenada\nPERPENDICULAR ao eixo",
         "#c0392b", "exercícios 6, 10"),
        ("CISALHAMENTO horizontal   H(k)",
         [["1", "k", "0"], ["0", "1", "0"], ["0", "0", "1"]],
         "x' = x + k · y\ny' = y",
         "det = 1 · preserva área,\nmas destrói os ângulos",
         "#0e8f8f", "exercício 8"),
    ]

    colunas = [0.045, 0.375, 0.705]
    linhas = [0.84, 0.32]

    for indice, (titulo, M, formulas, obs, cor, onde) in enumerate(MATRIZES):
        x = colunas[indice % 3]
        y = linhas[indice // 3]
        ax.text(x, y + 0.132, titulo, transform=ax.transAxes, fontsize=11.5,
                fontweight="bold", color=cor)
        ax.text(x, y + 0.098, onde, transform=ax.transAxes, fontsize=8.8,
                color="#8d95a5", style="italic")
        pl.desenhar_matriz(ax, x, y, np.array(M, dtype=object),
                           largura_celula=0.058, altura_celula=0.046)
        ax.text(x, y - 0.168, formulas, transform=ax.transAxes, fontsize=9.8,
                color="#2b3340", va="top", linespacing=1.7)
        ax.text(x, y - 0.245, obs, transform=ax.transAxes, fontsize=9,
                color=cor, va="top", linespacing=1.7)

    fig.suptitle("As seis matrizes do Estudo Dirigido 02 — coordenadas homogêneas 3x3",
                 fontsize=16, fontweight="bold", y=0.99)
    ax.text(0.5, 1.005, "aplicadas a vetores-coluna [x  y  1]ᵀ  por pré-multiplicação:  "
                        "P' = M · P",
            transform=ax.transAxes, ha="center", va="bottom", fontsize=11,
            color=pl.CINZA, style="italic")
    ax.text(0.5, -0.035,
            "A terceira linha é sempre [0  0  1]: ela mantém w = 1 e é o que permite "
            "somar a translação dentro de uma multiplicação.\n"
            "Com todas as transformações no mesmo formato, qualquer sequência delas "
            "colapsa em UMA matriz — é esse o motivo de existirem as coordenadas homogêneas.",
            transform=ax.transAxes, ha="center", va="top", fontsize=9.8,
            color="#6b7488", style="italic", linespacing=1.7)

    return pl.salvar(fig, SAIDA / "mapa_matrizes.png", dpi=125)


# --------------------------------------------------------------------------


def sintese_propriedades():
    """Grade do que cada transformação preserva — apurado numericamente."""
    LINHAS = [
        ("Translação  T(4, -2)", tg.translacao(4, -2), "1"),
        ("Escala uniforme  S(2, 2)", tg.escala(2), "4"),
        ("Escala não unif.  S(2 ; 0,5)", tg.escala(2, 0.5), "1"),
        ("Rotação  R(-45°)", tg.rotacao(-45), "1"),
        ("Reflexão  Fx / Fy", tg.reflexao_eixo_x(), "-1"),
        ("Cisalhamento  H(k=2)", tg.cisalhamento_horizontal(2), "1"),
    ]
    COLUNAS = ["distâncias", "ângulos", "áreas", "orientação", "paralelismo"]
    # S = preserva, N = não preserva, C = condicional
    TABELA = [
        ["S", "S", "S", "S", "S"],
        ["N", "S", "N", "S", "S"],
        ["N", "N", "C", "S", "S"],
        ["S", "S", "S", "S", "S"],
        ["S", "S", "S", "N", "S"],
        ["N", "N", "S", "S", "S"],
    ]
    CORES = {"S": ("#dcf0e4", "#1f7a4d", "preserva"),
             "N": ("#fadedc", "#b23b2e", "não preserva"),
             "C": ("#fdf0d6", "#a4770f", "depende")}
    ROTULO = {"S": "sim", "N": "não", "C": "só se\nsx·sy = 1"}

    fig, ax = plt.subplots(figsize=(12.2, 6.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.9, 8)
    ax.axis("off")

    x0, larg = 3.05, 1.15
    y0, alt = 6.1, 0.82

    for j, nome in enumerate(COLUNAS):
        ax.text(x0 + (j + 0.5) * larg, y0 + 0.52, nome, ha="center", va="bottom",
                fontsize=10.5, fontweight="bold", color="#2b3340")
    ax.text(x0 + 5 * larg + 0.62, y0 + 0.52, "det", ha="center", va="bottom",
            fontsize=10.5, fontweight="bold", color="#2b3340")

    for i, (nome, M, det) in enumerate(LINHAS):
        y = y0 - i * alt
        ax.text(x0 - 0.22, y, nome, ha="right", va="center", fontsize=10.3,
                color="#2b3340")
        for j in range(len(COLUNAS)):
            chave = TABELA[i][j]
            fundo, texto, _ = CORES[chave]
            ax.add_patch(plt.Rectangle((x0 + j * larg + 0.04, y - alt * 0.42),
                                       larg - 0.08, alt * 0.84, facecolor=fundo,
                                       edgecolor="white", linewidth=1.6))
            ax.text(x0 + (j + 0.5) * larg, y, ROTULO[chave], ha="center",
                    va="center", fontsize=9.2, color=texto, fontweight="bold",
                    linespacing=1.2)
        ax.text(x0 + 5 * larg + 0.62, y, det, ha="center", va="center",
                fontsize=10.5, color="#2b3340", fontweight="bold")

    for k, (_, cor, rot) in enumerate(CORES.values()):
        ax.text(x0 + k * 2.35, y0 - 5.5 * alt - 0.42, f"■ {rot}", fontsize=9.5,
                color=cor, fontweight="bold", va="top")

    ax.text(5.0, 7.72, "O que cada transformação preserva",
            ha="center", fontsize=16, fontweight="bold", color="#1c2230")
    ax.text(5.0, 7.30, "verificado numericamente pelos dez exercícios — "
                       "área, perímetro e ângulos medidos antes e depois",
            ha="center", fontsize=10.5, color=pl.CINZA, style="italic")
    ax.text(5.0, 0.72,
            "Ler de baixo para cima é ler uma hierarquia: rígidas (translação, "
            "rotação, reflexão) preservam distâncias; semelhanças acrescentam a\n"
            "escala uniforme e ainda preservam ângulos; afins (escala não uniforme, "
            "cisalhamento) preservam apenas o paralelismo das retas.\n"
            "O determinante resume tudo em um número: |det| é o fator de área, e o "
            "sinal diz se a orientação sobreviveu.",
            ha="center", va="top", fontsize=9.8, color="#6b7488", style="italic",
            linespacing=1.75)

    return pl.salvar(fig, SAIDA / "sintese_propriedades.png", dpi=125)


# --------------------------------------------------------------------------


def nao_comutatividade():
    """Mesmo ponto, mesmas três transformações, ordens diferentes."""
    P = np.array([3.0, 2.0])
    T, R, S = tg.translacao(1, -1), tg.rotacao(90), tg.escala(2)

    def caminho(sequencia):
        atual, pontos = P.copy(), [P.copy()]
        for M in sequencia:
            atual = np.round(tg.aplicar(M, atual)[0], 12) + 0.0
            pontos.append(atual)
        return pontos

    a = caminho([T, R, S])       # translação -> rotação -> escala (enunciado)
    b = caminho([S, R, T])       # escala -> rotação -> translação

    fig, ax = pl.nova_figura(
        "Por que a ordem importa: as MESMAS três transformações, invertidas",
        "translação (1,-1), rotação +90° e escala x2 aplicadas ao mesmo P(3, 2)",
        tamanho=(9.4, 7.6))

    for pontos, cor, rotulo, estilo in ((a, pl.LARANJA,
                                         "T → R → S  (ordem do exercício 9)", "-"),
                                        (b, pl.ROXO,
                                         "S → R → T  (ordem invertida)", "--")):
        for p, q in zip(pontos[:-1], pontos[1:]):
            pl.seta(ax, p, q, cor, largura=2.1, estilo=estilo)
        caminho_arr = np.array(pontos)
        ax.plot(caminho_arr[1:, 0], caminho_arr[1:, 1], "o", color=cor,
                markersize=8, markeredgecolor="white", markeredgewidth=1.5,
                label=rotulo, zorder=6)
        for i, p in enumerate(pontos[1:], start=1):
            ax.annotate(f"{i}: {tg.fmt_ponto(p)}", p, textcoords="offset points",
                        xytext=(9, 8), fontsize=9, color=cor, fontweight="bold")

    pl.desenhar_ponto(ax, P, pl.AZUL, "P inicial (3, 2)", nome="P", tamanho=12)
    pl.nota(ax, f"T → R → S  =>  P' = {tg.fmt_ponto(a[-1])}\n"
                f"S → R → T  =>  P' = {tg.fmt_ponto(b[-1])}\n\n"
                "S·R·T  ≠  T·R·S\n"
                "o produto de matrizes não é comutativo",
            posicao="inferior direita")
    pl.ajustar(ax, np.array(a), np.array(b), margem=1.9)
    pl.legenda(ax, 3)

    return pl.salvar(fig, SAIDA / "nao_comutatividade.png")


# --------------------------------------------------------------------------


def painel_exercicios():
    """Monta as dez figuras dos exercícios em uma única folha."""
    nomes = ["ex01_translacao", "ex02_escala_uniforme", "ex03_escala_nao_uniforme",
             "ex04_rotacao_ponto", "ex05_rotacao_poligono", "ex06_reflexao_ponto",
             "ex07_reflexao_triangulo", "ex08_cisalhamento",
             "ex09_composicao_ponto", "ex10_composicao_figura"]
    legendas = ["1 · translação", "2 · escala uniforme", "3 · escala não uniforme",
                "4 · rotação (ponto)", "5 · rotação (polígono)",
                "6 · reflexão (ponto)", "7 · reflexão (triângulo)",
                "8 · cisalhamento", "9 · composição (ponto)",
                "10 · composição (figura)"]

    fig, eixos = plt.subplots(2, 5, figsize=(22, 9.4), constrained_layout=True)
    for ax, nome, legenda in zip(eixos.ravel(), nomes, legendas):
        caminho = SAIDA / f"{nome}.png"
        if not caminho.exists():
            raise FileNotFoundError(f"{caminho} não existe — rode os exercícios antes.")
        ax.imshow(plt.imread(caminho))
        ax.set_title(legenda, fontsize=12, fontweight="bold", color="#2b3340")
        ax.set_xticks([])
        ax.set_yticks([])
        for lado in ax.spines.values():
            lado.set_edgecolor("#d5dae3")
    fig.suptitle("Estudo Dirigido 02 — os dez exercícios de transformação geométrica 2D",
                 fontsize=18, fontweight="bold")
    return pl.salvar(fig, SAIDA / "painel_exercicios.png", dpi=95)


EXTRAS = [mapa_matrizes, sintese_propriedades, nao_comutatividade]
