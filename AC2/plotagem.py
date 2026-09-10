# -*- coding: utf-8 -*-
"""
CAMADA DE PLOTAGEM — Matplotlib
================================
Ferramentas de desenho compartilhadas pelos dez exercícios, para que todas as
figuras tenham o mesmo eixo, a mesma escala e a mesma legenda de cores.

Duas decisões valem registro:

  * `aspect="equal"` é obrigatório aqui. Sem proporção 1:1 entre os eixos, uma
    rotação de 45° é desenhada como se fosse um cisalhamento e a figura mente
    sobre a transformação que ela deveria ilustrar.

  * o backend é o "Agg" (sem janela): as figuras são gravadas em `saida/*.png`
    em vez de exibidas com `plt.show()`. Isso torna a execução reprodutível e
    registrável em log — que é o que a entrega precisa.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch, Polygon
from matplotlib.transforms import blended_transform_factory

# paleta única da entrega
AZUL = "#3a7bd5"      # objeto original
LARANJA = "#e0762a"   # objeto transformado (resultado final)
VERDE = "#2e9e6b"     # passo intermediário 1
ROXO = "#a05fc4"      # passo intermediário 2
CINZA = "#5a6478"     # eixos, textos auxiliares
GRADE = "#ccd3df"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 10.5,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "legend.framealpha": 0.94,
    "legend.edgecolor": "#d5dae3",
})


# --------------------------------------------------------------------------
# estrutura da figura
# --------------------------------------------------------------------------


def nova_figura(titulo, subtitulo=None, tamanho=(7.6, 6.8)):
    fig, ax = plt.subplots(figsize=tamanho)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, linestyle=":", linewidth=0.9, color=GRADE, zorder=0)
    ax.axhline(0, color=CINZA, linewidth=1.3, zorder=1)
    ax.axvline(0, color=CINZA, linewidth=1.3, zorder=1)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(titulo, pad=26 if subtitulo else 10)
    if subtitulo:
        ax.text(0.5, 1.016, subtitulo, transform=ax.transAxes, ha="center",
                va="bottom", fontsize=10, color=CINZA, style="italic")
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color("#b6bfcd")
    return fig, ax


def legenda(ax, colunas=2):
    """
    Legenda ABAIXO do eixo, e não dentro dele.

    Nestas figuras a área de dados está sempre ocupada — objeto original,
    objeto transformado, arcos e rótulos de vértice. Uma legenda flutuante
    inevitavelmente cobriria algum desses elementos (chegou a esconder o
    ponto-resposta do exercício 9), então ela sai do quadro.
    """
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.085), ncol=colunas,
              frameon=False, fontsize=9.6, handlelength=1.9, columnspacing=1.8,
              borderaxespad=0.0)


def ajustar(ax, *conjuntos, margem=1.2, incluir_origem=True):
    """Enquadra todos os pontos informados mantendo a proporção 1:1."""
    pontos = [np.atleast_2d(np.asarray(c, dtype=float)) for c in conjuntos]
    if incluir_origem:
        pontos.append(np.zeros((1, 2)))
    P = np.vstack(pontos)
    minimo, maximo = P.min(axis=0), P.max(axis=0)
    centro = (minimo + maximo) / 2
    raio = max((maximo - minimo).max() / 2, 1.0) + margem
    ax.set_xlim(centro[0] - raio, centro[0] + raio)
    ax.set_ylim(centro[1] - raio, centro[1] + raio)


def salvar(fig, caminho, dpi=130):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(caminho, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return caminho


# --------------------------------------------------------------------------
# primitivas de desenho
# --------------------------------------------------------------------------


def desenhar_poligono(ax, vertices, cor, rotulo, *, estilo="-", preenchimento=0.16,
                      nomes=None, sufixo="", largura=2.4, zorder=3, marcador="o",
                      deslocamentos=(11, 9)):
    """
    Desenha o polígono fechado, os vértices e (opcionalmente) seus nomes.

    `deslocamentos` é o afastamento do rótulo em PONTOS: um par (dx, dy) para
    todos os vértices, ou uma lista com um par por vértice quando é preciso
    desviar de rótulos vizinhos.
    """
    V = np.asarray(vertices, dtype=float)
    fechado = np.vstack([V, V[0]])
    if preenchimento:
        ax.add_patch(Polygon(V, closed=True, facecolor=cor, alpha=preenchimento,
                             edgecolor="none", zorder=zorder - 1))
    ax.plot(fechado[:, 0], fechado[:, 1], estilo, color=cor, linewidth=largura,
            label=rotulo, zorder=zorder, solid_capstyle="round")
    ax.plot(V[:, 0], V[:, 1], marcador, color=cor, markersize=6.5,
            markeredgecolor="white", markeredgewidth=1.2, zorder=zorder + 1)
    if nomes:
        offsets = (list(deslocamentos) if isinstance(deslocamentos[0], (list, tuple))
                   else [deslocamentos] * len(V))
        for nome, (x, y), off in zip(nomes, V, offsets):
            ax.annotate(f"{nome}{sufixo}({_n(x)}, {_n(y)})",
                        (x, y), textcoords="offset points", xytext=tuple(off),
                        fontsize=9, color=cor, fontweight="bold", zorder=zorder + 2)
    return V


def desenhar_ponto(ax, ponto, cor, rotulo, *, nome="P", sufixo="",
                   deslocamento=(10, 12), tamanho=13, zorder=5):
    x, y = np.asarray(ponto, dtype=float).ravel()
    ax.plot([x], [y], "o", color=cor, markersize=tamanho, markeredgecolor="white",
            markeredgewidth=1.8, label=rotulo, zorder=zorder)
    ax.annotate(f"{nome}{sufixo}({_n(x)}, {_n(y)})", (x, y),
                textcoords="offset points", xytext=deslocamento,
                fontsize=11, fontweight="bold", color=cor, zorder=zorder + 1)
    return np.array([x, y])


def seta(ax, origem, destino, cor, *, curvatura=0.0, largura=2.0, estilo="-",
         zorder=4, alpha=1.0):
    ax.add_patch(FancyArrowPatch(tuple(origem), tuple(destino), arrowstyle="-|>",
                                 mutation_scale=17, linewidth=largura, color=cor,
                                 linestyle=estilo, alpha=alpha, zorder=zorder,
                                 connectionstyle=f"arc3,rad={curvatura}",
                                 shrinkA=3, shrinkB=3))


def ligacao(ax, a, b, cor=CINZA, alpha=0.55):
    """Linha pontilhada ligando um ponto ao seu correspondente transformado."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    ax.plot([a[0], b[0]], [a[1], b[1]], linestyle=(0, (3, 3)), linewidth=1.2,
            color=cor, alpha=alpha, zorder=2)


def arco_de_rotacao(ax, ponto, graus, cor, *, rotulo=None):
    """Arco centrado na origem mostrando o caminho de um ponto ao girar."""
    p = np.asarray(ponto, dtype=float)
    raio = float(np.linalg.norm(p))
    if raio < 1e-9:
        return
    inicio = np.degrees(np.arctan2(p[1], p[0]))
    t1, t2 = (inicio, inicio + graus) if graus >= 0 else (inicio + graus, inicio)
    ax.add_patch(Arc((0, 0), 2 * raio, 2 * raio, theta1=t1, theta2=t2,
                     color=cor, linewidth=1.5, linestyle=(0, (4, 3)),
                     alpha=0.85, zorder=2))
    if rotulo:
        meio = np.radians(inicio + graus / 2)
        ax.text(raio * 1.07 * np.cos(meio), raio * 1.07 * np.sin(meio), rotulo,
                fontsize=10.5, color=cor, fontweight="bold", ha="center",
                va="center", zorder=6)


def raio_de_escala(ax, ponto_origem, ponto_destino, cor=CINZA):
    """Reta que passa pela origem — evidencia que a origem é o ponto fixo."""
    b = np.asarray(ponto_destino, dtype=float)
    ax.plot([0, b[0]], [0, b[1]], linestyle=(0, (2, 4)), linewidth=1.1,
            color=cor, alpha=0.6, zorder=1)


def eixo_espelho(ax, eixo, cor="#c0392b"):
    """Destaca a reta de reflexão ('x' ou 'y'), rotulada sobre a própria reta."""
    if eixo == "y":
        ax.axvline(0, color=cor, linewidth=2.6, alpha=0.55, zorder=2)
        transformada = blended_transform_factory(ax.transData, ax.transAxes)
        ax.text(0, 0.015, "  eixo y (espelho)", transform=transformada, color=cor,
                fontsize=9.5, fontweight="bold", rotation=90, ha="left",
                va="bottom", zorder=6)
    else:
        ax.axhline(0, color=cor, linewidth=2.6, alpha=0.55, zorder=2)
        transformada = blended_transform_factory(ax.transAxes, ax.transData)
        ax.text(0.988, 0, "eixo x (espelho)  ", transform=transformada, color=cor,
                fontsize=9.5, fontweight="bold", ha="right", va="bottom", zorder=6)


def orientacao(ax, vertices, cor, *, raio=0.34):
    """Setinhas ao longo do contorno, para revelar o sentido dos vértices."""
    V = np.asarray(vertices, dtype=float)
    fechado = np.vstack([V, V[0]])
    for a, b in zip(fechado[:-1], fechado[1:]):
        meio = (a + b) / 2
        direcao = b - a
        norma = np.linalg.norm(direcao)
        if norma < 1e-9:
            continue
        direcao = direcao / norma * raio
        seta(ax, meio - direcao / 2, meio + direcao / 2, cor, largura=1.6,
             zorder=6, alpha=0.9)


def nota(ax, texto, *, posicao="inferior direita", cor="#2b3340"):
    """Caixa de texto com as medidas apuradas na execução."""
    coord = {"inferior direita": (0.985, 0.018, "right", "bottom"),
             "inferior esquerda": (0.015, 0.018, "left", "bottom"),
             "superior esquerda": (0.015, 0.982, "left", "top"),
             "superior direita": (0.985, 0.982, "right", "top")}[posicao]
    x, y, ha, va = coord
    ax.text(x, y, texto, transform=ax.transAxes, ha=ha, va=va, fontsize=9.3,
            color=cor, linespacing=1.55, zorder=8,
            bbox=dict(boxstyle="round,pad=0.55", facecolor="#f4f6fa",
                      edgecolor="#d5dae3"))


def desenhar_matriz(ax, x, y, M, *, titulo=None, escala_texto=1.0, cor="#2b3340",
                    largura_celula=0.13, altura_celula=0.088, casas=None):
    """
    Desenha uma matriz com colchetes em coordenadas de eixo (0..1).
    O mathtext do Matplotlib não suporta ambientes de matriz, então os
    colchetes e as células são desenhados manualmente.
    """
    M = np.asarray(M, dtype=object)
    n_lin, n_col = M.shape
    largura = n_col * largura_celula
    altura = n_lin * altura_celula
    if titulo:
        ax.text(x + largura / 2, y + altura_celula * 0.62, titulo,
                transform=ax.transAxes, ha="center", va="bottom",
                fontsize=10.5 * escala_texto, fontweight="bold", color=cor)
    for i in range(n_lin):
        for j in range(n_col):
            valor = M[i, j]
            if casas is not None and isinstance(valor, (int, float, np.floating)):
                valor = f"{valor:.{casas}f}"
            ax.text(x + (j + 0.5) * largura_celula,
                    y - (i + 0.5) * altura_celula,
                    str(valor), transform=ax.transAxes, ha="center", va="center",
                    fontsize=11 * escala_texto, color=cor)
    orelha = largura_celula * 0.16
    for lado in (0, 1):
        base = x + lado * largura
        sinal = 1 if lado == 0 else -1
        ax.plot([base, base], [y, y - altura], color=cor, linewidth=1.5,
                transform=ax.transAxes, clip_on=False)
        for topo in (y, y - altura):
            ax.plot([base, base + sinal * orelha], [topo, topo], color=cor,
                    linewidth=1.5, transform=ax.transAxes, clip_on=False)


def _n(v):
    """Número curto: sem casas decimais quando é inteiro."""
    v = float(v)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.4f}".rstrip("0").rstrip(".")
