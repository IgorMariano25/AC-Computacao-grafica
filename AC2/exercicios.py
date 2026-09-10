# -*- coding: utf-8 -*-
"""
OS DEZ EXERCÍCIOS DO ESTUDO DIRIGIDO 02
========================================
Cada função resolve um exercício de `AC02.md`: monta a matriz da
transformação, aplica-a, imprime a resposta com as medidas que comprovam o
efeito e grava a figura correspondente em `saida/`.

Nenhum resultado é digitado à mão: todo número que aparece no README vem da
execução destas funções.
"""

from pathlib import Path

import numpy as np

import transformacoes as tg
import plotagem as pl

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida"


# --------------------------------------------------------------------------
# auxiliares de console
# --------------------------------------------------------------------------


def titulo(texto):
    print("\n" + "=" * 76)
    print(texto)
    print("=" * 76)


def bloco(texto):
    print("\n" + texto)


def resposta(texto):
    print("\n  >> RESPOSTA: " + texto)


def _lista(pontos, casas=4):
    return "  ".join(tg.fmt_ponto(p, casas) for p in np.asarray(pontos))


# ==========================================================================
# EXERCÍCIO 1 — TRANSLAÇÃO SIMPLES
# ==========================================================================


def ex01_translacao_simples():
    titulo("EXERCÍCIO 1 — Translação simples do ponto P(2, 3) pelo vetor (4, -2)")

    P = np.array([2.0, 3.0])
    T = tg.translacao(4, -2)
    P_linha = tg.aplicar(T, P)[0]

    bloco(tg.fmt_matriz(T, "T(4,-2)", casas=0))
    bloco(f"  P  = {tg.fmt_ponto(P)}   ->   P' = T . P = {tg.fmt_ponto(P_linha)}")
    print(f"  deslocamento por eixo ..: dx = {P_linha[0] - P[0]:+.0f}   "
          f"dy = {P_linha[1] - P[1]:+.0f}")
    print(f"  distância percorrida ...: {np.linalg.norm(P_linha - P):.4f}")
    print(f"  det da parte linear ....: {tg.fator_de_area(T):.0f}  "
          "(a translação não deforma nada)")

    resposta(f"P' = {tg.fmt_ponto(P_linha)}. AS DUAS coordenadas mudaram: "
             f"x de 2 para 6 (+4) e y de 3 para 1 (-2).")
    print("  A translação é a única das transformações básicas que NÃO é linear:")
    print("  ela não pode ser escrita como matriz 2x2. É por isso que todo o")
    print("  trabalho usa coordenadas homogêneas 3x3, onde (tx, ty) ocupa a 3ª coluna.")

    fig, ax = pl.nova_figura(
        "Exercício 1 — Translação de P(2, 3) pelo vetor (4, -2)",
        "a translação desloca; não gira, não deforma e não muda de tamanho")
    pl.desenhar_ponto(ax, P, pl.AZUL, "P original", nome="P")
    pl.desenhar_ponto(ax, P_linha, pl.LARANJA, "P' transladado", nome="P", sufixo="'")
    pl.seta(ax, P, P_linha, pl.VERDE, largura=2.4)
    ax.plot([P[0], P_linha[0]], [P[1], P[1]], linestyle=(0, (4, 3)),
            color=pl.CINZA, linewidth=1.3, zorder=2)
    ax.plot([P_linha[0], P_linha[0]], [P[1], P_linha[1]], linestyle=(0, (4, 3)),
            color=pl.CINZA, linewidth=1.3, zorder=2)
    ax.text((P[0] + P_linha[0]) / 2, P[1] + 0.22, "tx = +4", ha="center",
            color=pl.CINZA, fontsize=10, fontweight="bold")
    ax.text(P_linha[0] + 0.22, (P[1] + P_linha[1]) / 2, "ty = -2", va="center",
            color=pl.CINZA, fontsize=10, fontweight="bold")
    pl.nota(ax, "P  = (2, 3)\nP' = (6, 1)\ndeslocamento = 4.4721\ndet = 1  (área preservada)",
            posicao="superior direita")
    pl.ajustar(ax, [P], [P_linha], margem=1.6)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex01_translacao.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 1, "nome": "Translação simples",
            "matriz": T.tolist(), "original": P.tolist(),
            "resultado": P_linha.tolist(),
            "resposta": f"P' = {tg.fmt_ponto(P_linha)}"}


# ==========================================================================
# EXERCÍCIO 2 — ESCALA UNIFORME
# ==========================================================================


def ex02_escala_uniforme():
    titulo("EXERCÍCIO 2 — Escala uniforme de fator 2 no triângulo A(1,1) B(3,1) C(2,4)")

    nomes = ["A", "B", "C"]
    tri = np.array([[1.0, 1.0], [3.0, 1.0], [2.0, 4.0]])
    S = tg.escala(2)
    novo = tg.aplicar(S, tri)

    bloco(tg.fmt_matriz(S, "S(2,2)", casas=0))
    bloco(tg.tabela_vertices(nomes, tri, novo, casas=0))

    a0, a1 = tg.area_com_sinal(tri), tg.area_com_sinal(novo)
    p0, p1 = tg.perimetro(tri), tg.perimetro(novo)
    ang0, ang1 = tg.angulos_internos(tri), tg.angulos_internos(novo)

    bloco(f"  área ........: {abs(a0):.4f}  ->  {abs(a1):.4f}   "
          f"(x {abs(a1 / a0):.0f} = fator²)")
    print(f"  perímetro ...: {p0:.4f}  ->  {p1:.4f}   (x {p1 / p0:.0f} = fator)")
    print(f"  ângulos .....: {np.array2string(ang0, precision=2)}  ->  "
          f"{np.array2string(ang1, precision=2)}   (inalterados)")
    print(f"  det(S) ......: {tg.fator_de_area(S):.0f}  = fator de área")

    resposta(f"A' = {tg.fmt_ponto(novo[0], 0)}, B' = {tg.fmt_ponto(novo[1], 0)}, "
             f"C' = {tg.fmt_ponto(novo[2], 0)}.")
    print("  O triângulo DOBRA em cada dimensão linear, então a área QUADRUPLICA")
    print("  (3 -> 12). Os ângulos internos não mudam: a escala uniforme é uma")
    print("  semelhança, preserva a forma. E, por ser em relação à origem, ela")
    print("  também AFASTA a figura: o baricentro vai de (2, 2) para (4, 4).")

    fig, ax = pl.nova_figura(
        "Exercício 2 — Escala uniforme de fator 2",
        "a origem é o ponto fixo: todo vértice se afasta sobre a reta que o liga a ela")
    for a, b in zip(tri, novo):
        pl.raio_de_escala(ax, a, b)
    pl.desenhar_poligono(ax, tri, pl.AZUL, "original (área 3)", nomes=nomes,
                         deslocamentos=[(-48, -16), (10, -16), (-48, 6)])
    pl.desenhar_poligono(ax, novo, pl.LARANJA, "escalado x2 (área 12)",
                         estilo="--", nomes=nomes, sufixo="'",
                         deslocamentos=[(12, -15), (12, -6), (10, 8)])
    ax.plot([0], [0], "s", color=pl.CINZA, markersize=8, zorder=6)
    ax.annotate("origem\n(ponto fixo)", (0, 0), textcoords="offset points",
                xytext=(-14, -34), fontsize=9, color=pl.CINZA, ha="center")
    pl.nota(ax, f"área:      {abs(a0):.2f}  ->  {abs(a1):.2f}   (x4 = 2²)\n"
                f"perímetro: {p0:.2f}  ->  {p1:.2f}   (x2)\n"
                f"ângulos:   inalterados  (semelhança)\n"
                f"det(S) = 4", posicao="superior esquerda")
    pl.ajustar(ax, tri, novo, margem=1.4)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex02_escala_uniforme.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 2, "nome": "Escala uniforme",
            "matriz": S.tolist(), "original": tri.tolist(),
            "resultado": novo.tolist(),
            "area": [abs(a0), abs(a1)], "perimetro": [p0, p1],
            "resposta": f"A'={tg.fmt_ponto(novo[0],0)} B'={tg.fmt_ponto(novo[1],0)} "
                        f"C'={tg.fmt_ponto(novo[2],0)}; área x4"}


# ==========================================================================
# EXERCÍCIO 3 — ESCALA NÃO UNIFORME
# ==========================================================================


def ex03_escala_nao_uniforme():
    titulo("EXERCÍCIO 3 — Escala não uniforme (sx = 2, sy = 0,5) no mesmo triângulo")

    nomes = ["A", "B", "C"]
    tri = np.array([[1.0, 1.0], [3.0, 1.0], [2.0, 4.0]])
    S = tg.escala(2, 0.5)
    novo = tg.aplicar(S, tri)

    bloco(tg.fmt_matriz(S, "S(2 , 0.5)", casas=1))
    bloco(tg.tabela_vertices(nomes, tri, novo, casas=1))

    a0, a1 = tg.area_com_sinal(tri), tg.area_com_sinal(novo)
    p0, p1 = tg.perimetro(tri), tg.perimetro(novo)
    ang0, ang1 = tg.angulos_internos(tri), tg.angulos_internos(novo)

    bloco(f"  área ........: {abs(a0):.4f}  ->  {abs(a1):.4f}   "
          f"(x {abs(a1 / a0):.2f})")
    print(f"  perímetro ...: {p0:.4f}  ->  {p1:.4f}   (x {p1 / p0:.4f})")
    print(f"  ângulos .....: {np.array2string(ang0, precision=2)}  ->  "
          f"{np.array2string(ang1, precision=2)}   (MUDARAM)")
    print(f"  det(S) ......: {tg.fator_de_area(S):.2f}  = 2 x 0,5")

    resposta(f"A' = {tg.fmt_ponto(novo[0], 1)}, B' = {tg.fmt_ponto(novo[1], 1)}, "
             f"C' = {tg.fmt_ponto(novo[2], 1)}.")
    print("  Caso instrutivo: det(S) = 2 x 0,5 = 1, então a ÁREA SE MANTÉM em 3,0")
    print("  — mas o triângulo está claramente deformado. O que se perde aqui não")
    print("  é área: são os ÂNGULOS. A escala não uniforme é afim, não é")
    print("  semelhança; ela achata em y o mesmo tanto que estica em x.")

    fig, ax = pl.nova_figura(
        "Exercício 3 — Escala não uniforme (sx = 2, sy = 0,5)",
        "det = 2 x 0,5 = 1: a área não muda, mas os ângulos sim")
    pl.desenhar_poligono(ax, tri, pl.AZUL, "original", nomes=nomes,
                         deslocamentos=[(-48, 8), (6, 11), (-22, 10)])
    pl.desenhar_poligono(ax, novo, pl.LARANJA, "escalado (2 ; 0,5)", estilo="--",
                         nomes=nomes, sufixo="'",
                         deslocamentos=[(-54, -16), (10, -6), (10, 7)])
    for a, b in zip(tri, novo):
        pl.ligacao(ax, a, b)
    pl.nota(ax, f"área:      {abs(a0):.2f}  ->  {abs(a1):.2f}   (det = 1)\n"
                f"perímetro: {p0:.2f}  ->  {p1:.2f}\n"
                f"ângulo em C: {ang0[2]:.1f}°  ->  {ang1[2]:.1f}°\n"
                "estica em x, achata em y")
    pl.ajustar(ax, tri, novo, margem=1.3)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex03_escala_nao_uniforme.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 3, "nome": "Escala não uniforme",
            "matriz": S.tolist(), "original": tri.tolist(),
            "resultado": novo.tolist(),
            "area": [abs(a0), abs(a1)], "perimetro": [p0, p1],
            "resposta": f"A'={tg.fmt_ponto(novo[0],1)} B'={tg.fmt_ponto(novo[1],1)} "
                        f"C'={tg.fmt_ponto(novo[2],1)}; área preservada"}


# ==========================================================================
# EXERCÍCIO 4 — ROTAÇÃO EM TORNO DA ORIGEM
# ==========================================================================


def ex04_rotacao_ponto():
    titulo("EXERCÍCIO 4 — Rotação de P(1, 0) em 90° anti-horário em torno da origem")

    P = np.array([1.0, 0.0])
    R = tg.rotacao(90)
    P_linha = tg.aplicar(R, P)[0]
    P_linha = np.round(P_linha, 12) + 0.0   # remove o -0.0 do cosseno de 90°

    bloco("  R(θ) = | cos θ   -sen θ   0 |     com θ = 90°:  cos 90° = 0, sen 90° = 1")
    print("         | sen θ    cos θ   0 |")
    print("         |   0        0     1 |")
    bloco(tg.fmt_matriz(np.round(R, 12) + 0.0, "R(90°)", casas=0))
    bloco(f"  P  = {tg.fmt_ponto(P)}   ->   P' = R . P = {tg.fmt_ponto(P_linha)}")
    print(f"  raio ........: {np.linalg.norm(P):.4f}  ->  "
          f"{np.linalg.norm(P_linha):.4f}   (preservado)")
    print(f"  ângulo polar : {np.degrees(np.arctan2(*P[::-1])):.1f}°  ->  "
          f"{np.degrees(np.arctan2(*P_linha[::-1])):.1f}°")
    print(f"  det(R) ......: {tg.fator_de_area(R):.0f}  (rotação é rígida: "
          "não altera tamanhos nem orientação)")

    resposta(f"P' = {tg.fmt_ponto(P_linha)} — o ponto sai do eixo x e vai parar "
             "sobre o eixo y.")
    print("  Vale reparar em qual coluna da matriz o resultado está: as colunas de")
    print("  R são exatamente as imagens dos vetores da base. Como P(1,0) É o")
    print("  primeiro vetor da base, P' é literalmente a 1ª coluna de R: (0, 1).")

    fig, ax = pl.nova_figura(
        "Exercício 4 — Rotação de P(1, 0) em +90° (anti-horário)",
        "o raio até a origem é preservado; só o ângulo polar muda")
    circulo = np.array([[np.cos(t), np.sin(t)] for t in np.linspace(0, 2 * np.pi, 200)])
    ax.plot(circulo[:, 0], circulo[:, 1], linestyle=(0, (3, 4)), color=pl.CINZA,
            linewidth=1.2, alpha=0.7, zorder=1, label="raio = 1 (preservado)")
    pl.arco_de_rotacao(ax, P, 90, pl.VERDE, rotulo="θ = +90°")
    ax.plot([0, P[0]], [0, P[1]], color=pl.AZUL, linewidth=1.6, alpha=0.7, zorder=2)
    ax.plot([0, P_linha[0]], [0, P_linha[1]], color=pl.LARANJA, linewidth=1.6,
            alpha=0.7, zorder=2)
    pl.desenhar_ponto(ax, P, pl.AZUL, "P original", nome="P")
    pl.desenhar_ponto(ax, P_linha, pl.LARANJA, "P' rotacionado", nome="P", sufixo="'")
    pl.nota(ax, "P  = (1, 0)   ângulo polar 0°\n"
                "P' = (0, 1)   ângulo polar 90°\n"
                "raio 1.0 preservado\ndet(R) = 1  (transformação rígida)",
            posicao="inferior esquerda")
    pl.ajustar(ax, [P], [P_linha], circulo, margem=0.6)
    pl.legenda(ax, 3)
    caminho = pl.salvar(fig, SAIDA / "ex04_rotacao_ponto.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 4, "nome": "Rotação em torno da origem",
            "matriz": R.tolist(), "original": P.tolist(),
            "resultado": P_linha.tolist(),
            "resposta": f"P' = {tg.fmt_ponto(P_linha)}"}


# ==========================================================================
# EXERCÍCIO 5 — ROTAÇÃO DE UM POLÍGONO
# ==========================================================================


def ex05_rotacao_poligono():
    titulo("EXERCÍCIO 5 — Rotação de 45° no sentido HORÁRIO do quadrado "
           "A(1,1) B(1,4) C(4,4) D(4,1)")

    nomes = ["A", "B", "C", "D"]
    quad = np.array([[1.0, 1.0], [1.0, 4.0], [4.0, 4.0], [4.0, 1.0]])
    R = tg.rotacao(-45)          # horário => ângulo NEGATIVO
    novo = tg.aplicar(R, quad)

    bloco("  Sentido horário => θ = -45°.  cos(-45°) = +√2/2 ≈ 0,7071,  "
          "sen(-45°) = -√2/2")
    bloco(tg.fmt_matriz(R, "R(-45°)", casas=4))
    bloco(tg.tabela_vertices(nomes, quad, novo, casas=4))

    a0, a1 = tg.area_com_sinal(quad), tg.area_com_sinal(novo)
    l0, l1 = tg.lados(quad), tg.lados(novo)

    bloco(f"  área com sinal ..: {a0:+.4f}  ->  {a1:+.4f}   "
          "(módulo e sinal preservados)")
    print(f"  lados ...........: {np.array2string(l0, precision=4)}  ->  "
          f"{np.array2string(l1, precision=4)}")
    print(f"  baricentro ......: {tg.fmt_ponto(quad.mean(axis=0))}  ->  "
          f"{tg.fmt_ponto(novo.mean(axis=0))}")
    print(f"  det(R) ..........: {tg.fator_de_area(R):.4f}")

    resposta("A' = (1,4142; 0), B' = (3,5355; 2,1213), C' = (5,6569; 0), "
             "D' = (3,5355; -2,1213).")
    print("  O quadrado continua um quadrado de lado 3 e área 9 — rotação é")
    print("  transformação RÍGIDA. Mas repare no baricentro: ele saiu de (2,5; 2,5)")
    print("  e foi para (3,5355; 0). Como a rotação é EM TORNO DA ORIGEM e a figura")
    print("  não está centrada nela, o quadrado além de girar também ORBITA.")
    print("  Girar a figura no próprio lugar exigiria a composição T . R . T⁻¹.")

    fig, ax = pl.nova_figura(
        "Exercício 5 — Rotação de 45° no sentido horário (θ = -45°)",
        "todo vértice percorre um arco centrado na origem: o quadrado gira E orbita")
    for v in quad:
        pl.arco_de_rotacao(ax, v, -45, pl.VERDE)
    pl.desenhar_poligono(ax, quad, pl.AZUL, "original (lado 3, área 9)", nomes=nomes,
                         deslocamentos=[(-50, -16), (-50, 6), (10, 6), (12, -6)])
    pl.desenhar_poligono(ax, novo, pl.LARANJA, "rotacionado -45°", estilo="--",
                         nomes=nomes, sufixo="'",
                         deslocamentos=[(-74, -16), (10, 6), (-26, 12), (12, 4)])
    for a, b in zip(quad, novo):
        pl.ligacao(ax, a, b, alpha=0.35)
    ax.plot([0], [0], "s", color=pl.CINZA, markersize=8, zorder=6)
    ax.annotate("centro da rotação", (0, 0), textcoords="offset points",
                xytext=(-16, 12), fontsize=9, color=pl.CINZA, ha="right")
    pl.nota(ax, f"lado: 3.0 -> 3.0        área: 9.0 -> 9.0\n"
                f"det(R) = 1  (rígida, sem deformação)\n"
                f"baricentro: (2.5, 2.5) -> ({novo.mean(axis=0)[0]:.4f}, "
                f"{novo.mean(axis=0)[1]:.4f})",
            posicao="inferior esquerda")
    pl.ajustar(ax, quad, novo, margem=1.6)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex05_rotacao_poligono.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 5, "nome": "Rotação de um polígono",
            "matriz": R.tolist(), "original": quad.tolist(),
            "resultado": novo.tolist(),
            "area": [abs(a0), abs(a1)],
            "resposta": "A'=(1,4142; 0) B'=(3,5355; 2,1213) C'=(5,6569; 0) "
                        "D'=(3,5355; -2,1213)"}


# ==========================================================================
# EXERCÍCIO 6 — REFLEXÃO SIMPLES
# ==========================================================================


def ex06_reflexao_ponto():
    titulo("EXERCÍCIO 6 — Reflexão de P(2, 5) em relação ao eixo y")

    P = np.array([2.0, 5.0])
    F = tg.reflexao_eixo_y()
    P_linha = tg.aplicar(F, P)[0]

    bloco(tg.fmt_matriz(F, "Fy", casas=0))
    bloco(f"  P  = {tg.fmt_ponto(P)}   ->   P' = Fy . P = {tg.fmt_ponto(P_linha)}")
    print(f"  distância ao eixo y : {abs(P[0]):.1f}  ->  {abs(P_linha[0]):.1f}   "
          "(igual, do outro lado)")
    print(f"  det(Fy) ............: {tg.fator_de_area(F):.0f}   "
          "(NEGATIVO: inverte a orientação)")

    resposta(f"P' = {tg.fmt_ponto(P_linha)} — só o sinal de x troca; y fica intacto.")
    print("  Refletir em relação ao eixo y significa espelhar a coordenada")
    print("  PERPENDICULAR a esse eixo, que é o x. O det = -1 é a assinatura da")
    print("  reflexão: módulo 1 (não muda tamanho), sinal negativo (vira o avesso).")

    fig, ax = pl.nova_figura(
        "Exercício 6 — Reflexão de P(2, 5) em relação ao eixo y",
        "o eixo y funciona como espelho: x troca de sinal, y permanece")
    pl.eixo_espelho(ax, "y")
    pl.desenhar_ponto(ax, P, pl.AZUL, "P original", nome="P")
    pl.desenhar_ponto(ax, P_linha, pl.LARANJA, "P' refletido", nome="P", sufixo="'",
                      deslocamento=(-96, 12))
    ax.plot([P_linha[0], P[0]], [P[1], P[1]], linestyle=(0, (4, 3)),
            color=pl.CINZA, linewidth=1.3, zorder=2)
    ax.plot([0], [P[1]], "o", color="#c0392b", markersize=6, zorder=6)
    ax.annotate("mesma distância\nao espelho (2)", (0, P[1]),
                textcoords="offset points", xytext=(0, 20), ha="center",
                fontsize=9, color="#c0392b")
    pl.nota(ax, "P  = ( 2, 5)\nP' = (-2, 5)\ny inalterado | x espelhado\n"
                "det(Fy) = -1  (orientação invertida)",
            posicao="inferior direita")
    pl.ajustar(ax, [P], [P_linha], margem=1.8)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex06_reflexao_ponto.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 6, "nome": "Reflexão simples",
            "matriz": F.tolist(), "original": P.tolist(),
            "resultado": P_linha.tolist(),
            "resposta": f"P' = {tg.fmt_ponto(P_linha)}"}


# ==========================================================================
# EXERCÍCIO 7 — REFLEXÃO DE UM TRIÂNGULO
# ==========================================================================


def ex07_reflexao_triangulo():
    titulo("EXERCÍCIO 7 — Reflexão do triângulo A(2,3) B(4,3) C(3,5) "
           "em relação ao eixo x")

    nomes = ["A", "B", "C"]
    tri = np.array([[2.0, 3.0], [4.0, 3.0], [3.0, 5.0]])
    F = tg.reflexao_eixo_x()
    novo = tg.aplicar(F, tri)

    bloco(tg.fmt_matriz(F, "Fx", casas=0))
    bloco(tg.tabela_vertices(nomes, tri, novo, casas=0))

    a0, a1 = tg.area_com_sinal(tri), tg.area_com_sinal(novo)
    p0, p1 = tg.perimetro(tri), tg.perimetro(novo)

    bloco(f"  área com sinal ..: {a0:+.4f}  ->  {a1:+.4f}   "
          "(mesmo módulo, SINAL TROCADO)")
    print(f"  sentido .........: {'anti-horário' if a0 > 0 else 'horário'}  ->  "
          f"{'anti-horário' if a1 > 0 else 'horário'}")
    print(f"  perímetro .......: {p0:.4f}  ->  {p1:.4f}   (preservado)")
    print(f"  det(Fx) .........: {tg.fator_de_area(F):.0f}")

    resposta(f"A' = {tg.fmt_ponto(novo[0], 0)}, B' = {tg.fmt_ponto(novo[1], 0)}, "
             f"C' = {tg.fmt_ponto(novo[2], 0)} — todos os y trocam de sinal.")
    print("  O detalhe que a lista de coordenadas esconde e a área com sinal revela:")
    print("  a ordem A->B->C era ANTI-HORÁRIA (+2) e passou a ser HORÁRIA (-2).")
    print("  Reflexão não é rotação: nenhum giro leva o triângulo original ao")
    print("  refletido sem tirá-lo do plano. É por isso que det = -1, e não +1.")

    fig, ax = pl.nova_figura(
        "Exercício 7 — Reflexão do triângulo em relação ao eixo x",
        "as setas no contorno mostram a inversão de orientação (det = -1)")
    pl.eixo_espelho(ax, "x")
    pl.desenhar_poligono(ax, tri, pl.AZUL, "original — sentido anti-horário",
                         nomes=nomes,
                         deslocamentos=[(-50, -6), (10, -6), (-34, 11)])
    pl.desenhar_poligono(ax, novo, pl.LARANJA, "refletido — sentido horário",
                         estilo="--", nomes=nomes, sufixo="'",
                         deslocamentos=[(-52, -4), (10, -4), (-16, -20)])
    pl.orientacao(ax, tri, pl.AZUL)
    pl.orientacao(ax, novo, pl.LARANJA)
    for a, b in zip(tri, novo):
        pl.ligacao(ax, a, b, alpha=0.4)
    pl.nota(ax, f"área com sinal: {a0:+.1f}  ->  {a1:+.1f}\n"
                f"perímetro: {p0:.4f}  ->  {p1:.4f}  (igual)\n"
                "det(Fx) = -1  ->  orientação invertida",
            posicao="superior direita")
    pl.ajustar(ax, tri, novo, margem=1.2, incluir_origem=False)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex07_reflexao_triangulo.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 7, "nome": "Reflexão de um triângulo",
            "matriz": F.tolist(), "original": tri.tolist(),
            "resultado": novo.tolist(),
            "area_com_sinal": [a0, a1],
            "resposta": f"A'={tg.fmt_ponto(novo[0],0)} B'={tg.fmt_ponto(novo[1],0)} "
                        f"C'={tg.fmt_ponto(novo[2],0)}"}


# ==========================================================================
# EXERCÍCIO 8 — CISALHAMENTO HORIZONTAL
# ==========================================================================


def ex08_cisalhamento():
    titulo("EXERCÍCIO 8 — Cisalhamento horizontal com k = 2 no ponto P(2, 3)")

    P = np.array([2.0, 3.0])
    H = tg.cisalhamento_horizontal(2)
    P_linha = tg.aplicar(H, P)[0]

    bloco(tg.fmt_matriz(H, "H(k=2)", casas=0))
    bloco(f"  x' = x + k.y = 2 + 2 x 3 = {P_linha[0]:.0f}")
    print(f"  y' = y       = {P_linha[1]:.0f}   (o cisalhamento horizontal "
          "nunca altera y)")
    print(f"  P  = {tg.fmt_ponto(P)}   ->   P' = {tg.fmt_ponto(P_linha)}")
    print(f"  det(H) ......: {tg.fator_de_area(H):.0f}   "
          "(preserva área, mas não é rígida)")

    # retângulo de referência que tem P como vértice, para ver a deformação
    ret = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 3.0], [0.0, 3.0]])
    ret_novo = tg.aplicar(H, ret)
    a0, a1 = abs(tg.area_com_sinal(ret)), abs(tg.area_com_sinal(ret_novo))

    bloco(f"  retângulo de referência {_lista(ret, 0)}")
    print(f"    ->  {_lista(ret_novo, 0)}")
    print(f"    área {a0:.1f} -> {a1:.1f} (igual)   "
          f"perímetro {tg.perimetro(ret):.4f} -> {tg.perimetro(ret_novo):.4f}")

    resposta(f"P' = {tg.fmt_ponto(P_linha)} — x salta de 2 para 8, y continua 3.")
    print("  O deslocamento horizontal é PROPORCIONAL À ALTURA do ponto: quem está")
    print("  em y = 0 não sai do lugar, quem está em y = 3 anda 6 unidades. É por")
    print("  isso que o retângulo vira um paralelogramo — a base fica parada e o")
    print("  topo desliza. Como base e altura não mudam, a área é preservada")
    print("  (det = 1), mas os ângulos retos se perdem: não é uma transformação rígida.")

    fig, ax = pl.nova_figura(
        "Exercício 8 — Cisalhamento horizontal (k = 2)",
        "x' = x + 2y : o deslocamento é proporcional à altura, então a base não se move")
    pl.desenhar_poligono(ax, ret, pl.AZUL, "retângulo de referência (área 6)",
                         preenchimento=0.12, marcador="")
    pl.desenhar_poligono(ax, ret_novo, pl.LARANJA, "paralelogramo cisalhado (área 6)",
                         estilo="--", preenchimento=0.12, marcador="")
    for y in (1.0, 2.0):
        ax.annotate("", xy=(2 * y + 0.1, y), xytext=(0.1, y),
                    arrowprops=dict(arrowstyle="-|>", color=pl.VERDE, lw=1.3,
                                    alpha=0.75))
        ax.text(2 * y + 0.35, y, f"y={y:.0f}: +{2 * y:.0f}", fontsize=8.6,
                color=pl.VERDE, va="center")
    pl.desenhar_ponto(ax, P, pl.AZUL, "P original", nome="P")
    pl.desenhar_ponto(ax, P_linha, pl.LARANJA, "P' cisalhado", nome="P", sufixo="'")
    pl.seta(ax, P, P_linha, pl.VERDE, largura=2.2)
    pl.nota(ax, "P  = (2, 3)\nP' = (8, 3)\ny nunca muda | det(H) = 1\n"
                "área preservada, ângulos retos perdidos")
    pl.ajustar(ax, ret, ret_novo, [P_linha], margem=1.3)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex08_cisalhamento.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 8, "nome": "Cisalhamento horizontal",
            "matriz": H.tolist(), "original": P.tolist(),
            "resultado": P_linha.tolist(),
            "resposta": f"P' = {tg.fmt_ponto(P_linha)}"}


# ==========================================================================
# EXERCÍCIO 9 — COMPOSIÇÃO DE TRANSFORMAÇÕES
# ==========================================================================


def ex09_composicao_ponto():
    titulo("EXERCÍCIO 9 — Composição em P(3, 2): translação (1,-1), "
           "rotação +90°, escala 2")

    P = np.array([3.0, 2.0])
    T = tg.translacao(1, -1)
    R = tg.rotacao(90)
    S = tg.escala(2)

    p1 = tg.aplicar(T, P)[0]
    p2 = np.round(tg.aplicar(R, p1)[0], 12) + 0.0
    p3 = np.round(tg.aplicar(S, p2)[0], 12) + 0.0

    bloco("  Passo a passo:")
    print(f"    1) translação (1, -1) : {tg.fmt_ponto(P)}  ->  {tg.fmt_ponto(p1)}")
    print(f"    2) rotação +90°       : {tg.fmt_ponto(p1)}  ->  {tg.fmt_ponto(p2)}")
    print(f"    3) escala uniforme 2  : {tg.fmt_ponto(p2)}  ->  {tg.fmt_ponto(p3)}")

    M = tg.compor(S, R, T)          # aplica T, depois R, depois S
    direto = np.round(tg.aplicar(M, P)[0], 12) + 0.0

    bloco("  Matriz única equivalente — M = S . R . T")
    print("  (a ordem de escrita é a INVERSA da ordem de aplicação)")
    bloco(tg.fmt_matriz(np.round(M, 12) + 0.0, "M", casas=0))
    print(f"  M . P = {tg.fmt_ponto(direto)}   "
          f"(confere com o passo a passo: {np.allclose(direto, p3)})")

    # a ordem importa
    M_invertida = tg.compor(T, R, S)
    outra = np.round(tg.aplicar(M_invertida, P)[0], 12) + 0.0
    bloco(f"  Trocando a ordem (escala, depois rotação, depois translação): "
          f"{tg.fmt_ponto(outra)}")
    print(f"  Composição de matrizes NÃO é comutativa: "
          f"{tg.fmt_ponto(p3)} != {tg.fmt_ponto(outra)}")

    resposta(f"P' = {tg.fmt_ponto(p3)}.")
    print("  As três transformações viraram UMA matriz 3x3. Esse é o ganho prático")
    print("  das coordenadas homogêneas: numa cena com milhares de vértices, o")
    print("  produto S.R.T é calculado uma vez e cada vértice sofre uma única")
    print("  multiplicação, em vez de três passagens sobre a malha inteira.")

    fig, ax = pl.nova_figura(
        "Exercício 9 — Composição de três transformações em P(3, 2)",
        "cada seta é um passo; a matriz M = S . R . T leva P a P' de uma só vez")
    pl.arco_de_rotacao(ax, p1, 90, pl.ROXO)
    pl.desenhar_ponto(ax, P, pl.AZUL, "P inicial (3, 2)", nome="P")
    pl.desenhar_ponto(ax, p1, pl.VERDE, "1) após translação (1, -1)",
                      nome="P", sufixo="₁")
    pl.desenhar_ponto(ax, p2, pl.ROXO, "2) após rotação +90°", nome="P", sufixo="₂",
                      deslocamento=(-118, 6))
    pl.desenhar_ponto(ax, p3, pl.LARANJA, "3) após escala x2 = P'", nome="P",
                      sufixo="'", deslocamento=(10, -6))
    pl.seta(ax, P, p1, pl.VERDE, largura=2.0)
    pl.seta(ax, p2, p3, pl.LARANJA, largura=2.0)
    pl.raio_de_escala(ax, p2, p3)
    pl.seta(ax, P, p3, "#9aa3b2", largura=1.6, estilo=(0, (5, 4)), curvatura=0.16,
            zorder=2, alpha=0.75)
    pl.nota(ax, "(3, 2) -> (4, 1) -> (-1, 4) -> (-2, 8)\n"
                "M = S.R.T  =  | 0  -2   2 |\n"
                "              | 2   0   2 |\n"
                "              | 0   0   1 |\n"
                "ordem trocada daria (-3, 5): não comuta",
            posicao="inferior direita")
    pl.ajustar(ax, [P], [p1], [p2], [p3], margem=2.0)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex09_composicao_ponto.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 9, "nome": "Composição de transformações",
            "matriz": M.tolist(), "original": P.tolist(),
            "passos": [p1.tolist(), p2.tolist(), p3.tolist()],
            "resultado": p3.tolist(),
            "ordem_invertida": outra.tolist(),
            "resposta": f"P' = {tg.fmt_ponto(p3)}"}


# ==========================================================================
# EXERCÍCIO 10 — COMBINAÇÃO DE TRANSFORMAÇÕES EM UMA FIGURA
# ==========================================================================


def ex10_composicao_figura():
    titulo("EXERCÍCIO 10 — Retângulo A(1,1) B(5,1) C(5,3) D(1,3): "
           "translação (-2,3), escala (1,5 ; 0,5), reflexão em y")

    nomes = ["A", "B", "C", "D"]
    ret = np.array([[1.0, 1.0], [5.0, 1.0], [5.0, 3.0], [1.0, 3.0]])

    T = tg.translacao(-2, 3)
    S = tg.escala(1.5, 0.5)
    F = tg.reflexao_eixo_y()

    e1 = tg.aplicar(T, ret)
    e2 = tg.aplicar(S, e1)
    e3 = tg.aplicar(F, e2)

    bloco("  Passo 1 — translação (-2, 3)")
    print("    " + _lista(e1, 1))
    print("  Passo 2 — escala não uniforme (1,5 ; 0,5)")
    print("    " + _lista(e2, 1))
    print("  Passo 3 — reflexão em relação ao eixo y")
    print("    " + _lista(e3, 1))

    M = tg.compor(F, S, T)
    direto = tg.aplicar(M, ret)

    bloco("  Matriz única — M = Fy . S . T")
    bloco(tg.fmt_matriz(M, "M", casas=2))
    print(f"  M aplicada de uma vez confere com o passo a passo: "
          f"{np.allclose(direto, e3)}")
    bloco(tg.tabela_vertices(nomes, ret, e3, casas=1))

    a0, a3 = tg.area_com_sinal(ret), tg.area_com_sinal(e3)
    bloco(f"  área com sinal ..: {a0:+.4f}  ->  {a3:+.4f}")
    print(f"  det(M) ..........: {tg.fator_de_area(M):+.4f}  "
          f"= (-1) x 1,5 x 0,5   ->   área x {abs(tg.fator_de_area(M)):.2f}, "
          "orientação invertida")
    print(f"  dimensões .......: 4 x 2  ->  "
          f"{abs(e3[1][0] - e3[0][0]):.1f} x {abs(e3[2][1] - e3[1][1]):.1f}")

    resposta(f"A' = {tg.fmt_ponto(e3[0], 1)}, B' = {tg.fmt_ponto(e3[1], 1)}, "
             f"C' = {tg.fmt_ponto(e3[2], 1)}, D' = {tg.fmt_ponto(e3[3], 1)}.")
    print("  Duas leituras que os números entregam de graça:")
    print("   * det(M) = -0,75 prevê a área final sem precisar recalculá-la:")
    print("     8 x 0,75 = 6. E o sinal negativo avisa que a figura foi espelhada.")
    print("   * A translação foi aplicada ANTES da escala, então ela também foi")
    print("     escalada: o (-2, 3) do enunciado aparece na matriz final como")
    print("     (+3; +1,5). Trocar a ordem daria outro retângulo.")

    fig, ax = pl.nova_figura(
        "Exercício 10 — Três transformações encadeadas em um retângulo",
        "M = Fy . S . T  —  cada cor é um estágio da sequência")
    pl.eixo_espelho(ax, "y")
    pl.desenhar_poligono(ax, ret, pl.AZUL, "0) original", nomes=nomes,
                         preenchimento=0.13,
                         deslocamentos=[(-8, -20), (12, -8), (12, 8), (-54, 12)])
    pl.desenhar_poligono(ax, e1, pl.VERDE, "1) + translação (-2, 3)", estilo="--",
                         preenchimento=0.10, marcador="")
    pl.desenhar_poligono(ax, e2, pl.ROXO, "2) + escala (1,5 ; 0,5)", estilo="-.",
                         preenchimento=0.10, marcador="")
    pl.desenhar_poligono(ax, e3, pl.LARANJA, "3) + reflexão em y  =  resultado",
                         estilo="--", nomes=nomes, sufixo="'", preenchimento=0.18,
                         deslocamentos=[(14, -17), (-10, -22), (-10, 12), (12, 12)])
    for a, b in zip(e2, e3):
        pl.ligacao(ax, a, b, alpha=0.35)
    pl.nota(ax, f"área: {abs(a0):.1f}  ->  {abs(a3):.1f}     "
                f"det(M) = {tg.fator_de_area(M):+.2f}\n"
                "dimensões: 4 x 2  ->  6 x 1\n"
                "sinal de det negativo = figura espelhada",
            posicao="inferior esquerda")
    pl.ajustar(ax, ret, e1, e2, e3, margem=1.2)
    pl.legenda(ax, 2)
    caminho = pl.salvar(fig, SAIDA / "ex10_composicao_figura.png")
    print(f"\n  figura -> {caminho.name}")

    return {"exercicio": 10, "nome": "Combinação de transformações em uma figura",
            "matriz": M.tolist(), "original": ret.tolist(),
            "passos": [e1.tolist(), e2.tolist(), e3.tolist()],
            "resultado": e3.tolist(),
            "det": tg.fator_de_area(M),
            "resposta": f"A'={tg.fmt_ponto(e3[0],1)} B'={tg.fmt_ponto(e3[1],1)} "
                        f"C'={tg.fmt_ponto(e3[2],1)} D'={tg.fmt_ponto(e3[3],1)}"}


EXERCICIOS = [
    ex01_translacao_simples,
    ex02_escala_uniforme,
    ex03_escala_nao_uniforme,
    ex04_rotacao_ponto,
    ex05_rotacao_poligono,
    ex06_reflexao_ponto,
    ex07_reflexao_triangulo,
    ex08_cisalhamento,
    ex09_composicao_ponto,
    ex10_composicao_figura,
]
