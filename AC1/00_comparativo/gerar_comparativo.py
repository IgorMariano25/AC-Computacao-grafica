# -*- coding: utf-8 -*-
"""
QUADRO COMPARATIVO DAS QUATRO ÁREAS DA COMPUTAÇÃO VISUAL
=========================================================
Gera duas figuras de síntese a partir dos resultados já produzidos pelos
quatro programas das pastas 01 a 04:

  1) painel_areas.png   - um resultado de cada área, com entrada e saída
  2) diagrama_areas.png - o diagrama de relacionamento entre as áreas
                          (slide 12 do arquivo aula01/intro.pdf e slide 66 do
                          arquivo aula02/intro_computacao_visual.pdf)

Execute os quatro programas antes deste.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from PIL import Image

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
SAIDA = AQUI / "saida"
SAIDA.mkdir(exist_ok=True)

AREAS = [
    ("1. SÍNTESE DE IMAGENS\n(Computação Gráfica)",
     BASE / "01_sintese_imagens" / "saida" / "d_phong.png",
     "ENTRADA: modelo geométrico\n19.895 vértices / 37.986 triângulos",
     "SAÍDA: imagem 900x900\nrasterizada pela GPU",
     "#e0762a"),
    ("2. PROCESSAMENTO DE IMAGENS",
     BASE / "02_processamento_imagens" / "saida" / "pi_canny.png",
     "ENTRADA: imagem 512x480x3\n(fotografia)",
     "SAÍDA: imagem 512x480\n(mesma natureza de dado)",
     "#3a7bd5"),
    ("3. VISÃO COMPUTACIONAL\n(Visão Artificial)",
     BASE / "03_visao_computacional" / "saida" / "passo6_deteccoes_yolo.png",
     "ENTRADA: imagem 810x1080x3\n(2,6 MB de pixels)",
     "SAÍDA: 6 objetos nomeados\n(974 bytes de JSON)",
     "#2e9e6b"),
    ("4. VISUALIZAÇÃO COMPUTACIONAL",
     BASE / "04_visualizacao_computacional" / "saida" / "A3_dvr_osso.png",
     "ENTRADA: campo escalar 3D\n10.368.384 voxels (9,9 MB)",
     "SAÍDA: imagem para ANÁLISE\n(ray casting / DVR)",
     "#a05fc4"),
]


def painel_areas():
    fig, eixos = plt.subplots(1, 4, figsize=(19, 6.6), constrained_layout=True)
    for ax, (titulo, caminho, entrada, saida, cor) in zip(eixos, AREAS):
        if not caminho.exists():
            raise FileNotFoundError(
                f"{caminho} não existe — execute os programas das pastas 01 a 04 antes.")
        ax.imshow(Image.open(caminho).convert("RGB"))
        ax.set_title(titulo, fontsize=12.5, fontweight="bold", color=cor, pad=10)
        ax.set_xlabel(f"{entrada}\n{'':->34}\n{saida}", fontsize=9.5, linespacing=1.5)
        ax.set_xticks([])
        ax.set_yticks([])
        for lado in ax.spines.values():
            lado.set_edgecolor(cor)
            lado.set_linewidth(2.5)
    fig.suptitle("As quatro áreas da Computação Visual — um resultado executado de cada uma",
                 fontsize=16, fontweight="bold")
    fig.savefig(SAIDA / "painel_areas.png", dpi=115)
    plt.close(fig)
    print("-> saida/painel_areas.png")


def diagrama_areas():
    """
    Diagrama de relacionamento entre as áreas.

    As CAIXAS são os tipos de dado; as SETAS são as áreas. É essa leitura que
    separa as quatro áreas sem ambiguidade: cada uma é definida pelo par
    (o que entra, o que sai).
    """
    fig, ax = plt.subplots(figsize=(14, 8.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(-12, 108)
    ax.axis("off")

    def caixa(x, y, w, h, titulo, detalhe):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=1.4",
                                    facecolor="#2b3340", edgecolor="none", zorder=2))
        ax.text(x + w / 2, y + h * 0.68, titulo, ha="center", va="center",
                fontsize=13, fontweight="bold", color="white", zorder=3)
        ax.text(x + w / 2, y + h * 0.28, detalhe, ha="center", va="center",
                fontsize=10, color="#b8c2d4", zorder=3, linespacing=1.4)

    def seta(p1, p2, cor, rad=0.0):
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=24,
                                     linewidth=3.0, color=cor, zorder=4,
                                     connectionstyle=f"arc3,rad={rad}"))

    def rotulo(x, y, texto, cor, tamanho=12):
        ax.text(x, y, texto, ha="center", va="center", fontsize=tamanho,
                fontweight="bold", color="white", zorder=6,
                bbox=dict(boxstyle="round,pad=0.5", facecolor=cor,
                          edgecolor="none"), linespacing=1.35)

    LARANJA, AZUL, VERDE, ROXO = "#e0762a", "#3a7bd5", "#2e9e6b", "#a05fc4"

    # --- os três tipos de dado ---
    caixa(4, 56, 28, 22, "MODELOS E DADOS",
          "vértices e malhas 3D\ncampos escalares medidos\ntabelas de indicadores")
    caixa(68, 56, 28, 22, "IMAGEM DIGITAL",
          "matriz de pixels\n(frame buffer)")
    caixa(68, 5, 28, 19, "DESCRIÇÃO SIMBÓLICA",
          "classes, posições,\nmedidas, decisões")

    # --- área 1: modelos -> imagem (seta superior, reta) ---
    seta((32, 72), (68, 72), LARANJA, 0.0)
    rotulo(50, 82, "1. SÍNTESE DE IMAGENS  (Computação Gráfica)\n"
                   "modelo geométrico  →  imagem realista", LARANJA, 11.5)

    # --- área 4: dados -> imagem (arco inferior) ---
    seta((32, 61), (68, 61), ROXO, 0.34)
    rotulo(50, 34, "4. VISUALIZAÇÃO COMPUTACIONAL\n"
                   "dado abstrato ou medido  →  imagem para análise", ROXO, 11.5)
    ax.text(50, 25, "a área entrega a imagem;\nquem extrai a informação é o usuário",
            ha="center", va="center", fontsize=9.5, color="#6b7488",
            style="italic", linespacing=1.4)

    # --- área 2: imagem -> imagem (laço sobre a própria caixa) ---
    seta((76, 78), (88, 78), AZUL, -1.9)
    rotulo(82, 93, "2. PROCESSAMENTO DE IMAGENS\nimagem  →  imagem", AZUL, 11.5)

    # --- área 3: imagem -> descrição ---
    seta((82, 55), (82, 25), VERDE, 0.0)
    rotulo(82, 41, "3. VISÃO COMPUTACIONAL\nimagem  →  significado", VERDE, 11.5)

    ax.text(50, 105, "Relacionamento entre as áreas da Computação Visual",
            ha="center", va="center", fontsize=18, fontweight="bold", color="#1c2230")
    ax.text(50, -8,
            "As caixas são TIPOS DE DADO; as setas são as ÁREAS. Cada área se define pelo par "
            "(o que entra, o que sai).\n"
            "São áreas com identidade própria e focos distintos, mas que interagem: a "
            "Visualização usa o motor de síntese da área 1,\n"
            "e a Visão Computacional usa o Processamento de Imagens como etapa de "
            "pré-processamento.",
            ha="center", va="center", fontsize=10.5, color="#4a5468", style="italic",
            linespacing=1.7)

    fig.savefig(SAIDA / "diagrama_areas.png", dpi=125,
                facecolor="white", bbox_inches="tight")
    plt.close(fig)
    print("-> saida/diagrama_areas.png")


if __name__ == "__main__":
    print("Gerando quadro comparativo das quatro áreas...")
    painel_areas()
    diagrama_areas()
    print(f"Arquivos em: {SAIDA}")
