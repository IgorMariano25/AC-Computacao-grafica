# -*- coding: utf-8 -*-
"""
NÚCLEO DO ESTUDO DIRIGIDO 02 — TRANSFORMAÇÕES GEOMÉTRICAS 2D
=============================================================
Toda transformação deste trabalho é uma matriz 3x3 em COORDENADAS HOMOGÊNEAS,
aplicada a vetores-coluna [x, y, 1]^T:

        | x' |   | a  b  tx |   | x |
        | y' | = | c  d  ty | . | y |
        | 1  |   | 0  0  1  |   | 1 |

O motivo de usar 3x3 para um problema 2D é o mesmo apontado no material da
aula 04 (`docs/aula04/tg2d3d.pdf`): a translação NÃO é linear e não cabe em uma
matriz 2x2. Em coordenadas homogêneas ela vira a última coluna, e aí as quatro
famílias de transformação (translação, escala, rotação, reflexão/cisalhamento)
passam a ser o MESMO tipo de objeto — o que permite compor qualquer sequência
por simples multiplicação de matrizes.

Convenções adotadas:
  * vetores-coluna e pré-multiplicação (P' = M . P), como no material da aula;
  * ângulo positivo = sentido anti-horário (convenção matemática padrão);
  * o eixo y aponta para cima (ao contrário da matriz de pixels, em que y
    cresce para baixo).
"""

from functools import reduce

import numpy as np

# --------------------------------------------------------------------------
# 1. MATRIZES CANÔNICAS
# --------------------------------------------------------------------------


def translacao(tx, ty):
    """Desloca todo ponto por (tx, ty). Não é linear: precisa da 3ª coluna."""
    return np.array([[1.0, 0.0, float(tx)],
                     [0.0, 1.0, float(ty)],
                     [0.0, 0.0, 1.0]])


def escala(sx, sy=None):
    """Escala em relação à ORIGEM. sy omitido => escala uniforme."""
    sy = sx if sy is None else sy
    return np.array([[float(sx), 0.0, 0.0],
                     [0.0, float(sy), 0.0],
                     [0.0, 0.0, 1.0]])


def rotacao(graus):
    """Rotação em torno da ORIGEM. Ângulo positivo = anti-horário."""
    t = np.radians(float(graus))
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0.0],
                     [s, c, 0.0],
                     [0.0, 0.0, 1.0]])


def reflexao_eixo_x():
    """Espelha em relação ao eixo x: (x, y) -> (x, -y)."""
    return np.array([[1.0, 0.0, 0.0],
                     [0.0, -1.0, 0.0],
                     [0.0, 0.0, 1.0]])


def reflexao_eixo_y():
    """Espelha em relação ao eixo y: (x, y) -> (-x, y)."""
    return np.array([[-1.0, 0.0, 0.0],
                     [0.0, 1.0, 0.0],
                     [0.0, 0.0, 1.0]])


def cisalhamento_horizontal(k):
    """x' = x + k.y ; y' = y — o deslocamento é proporcional à ALTURA."""
    return np.array([[1.0, float(k), 0.0],
                     [0.0, 1.0, 0.0],
                     [0.0, 0.0, 1.0]])


def cisalhamento_vertical(k):
    """x' = x ; y' = y + k.x"""
    return np.array([[1.0, 0.0, 0.0],
                     [float(k), 1.0, 0.0],
                     [0.0, 0.0, 1.0]])


IDENTIDADE = np.eye(3)


# --------------------------------------------------------------------------
# 2. COMPOSIÇÃO E APLICAÇÃO
# --------------------------------------------------------------------------


def compor(*matrizes):
    """
    Produto matricial na ordem em que os argumentos são escritos.

    Atenção à ordem de leitura: em pré-multiplicação, `compor(A, B, C)` produz
    A.B.C, e o ponto é atingido primeiro por C, depois por B, depois por A.
    Ou seja: a ÚLTIMA matriz da lista é a PRIMEIRA a ser aplicada.
    """
    return reduce(np.matmul, matrizes)


def aplicar(M, pontos):
    """
    Aplica a matriz 3x3 `M` a um ponto (x, y) ou a um array N x 2 de pontos.
    Devolve sempre um array N x 2 em coordenadas cartesianas.
    """
    P = np.atleast_2d(np.asarray(pontos, dtype=float))
    homogeneas = np.vstack([P.T, np.ones(len(P))])       # 3 x N
    resultado = M @ homogeneas                            # 3 x N
    return (resultado[:2] / resultado[2]).T               # N x 2


# --------------------------------------------------------------------------
# 3. MEDIDAS GEOMÉTRICAS (para comprovar o efeito de cada transformação)
# --------------------------------------------------------------------------


def area_com_sinal(poligono):
    """
    Área pela fórmula do laço (shoelace), COM sinal:
      positivo -> vértices em sentido anti-horário
      negativo -> vértices em sentido horário
    O sinal é o que denuncia a inversão de orientação de uma reflexão.
    """
    P = np.asarray(poligono, dtype=float)
    x, y = P[:, 0], P[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def perimetro(poligono):
    P = np.asarray(poligono, dtype=float)
    return float(np.sum(np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)))


def lados(poligono):
    P = np.asarray(poligono, dtype=float)
    return np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)


def angulos_internos(poligono):
    """Ângulos internos em graus, na ordem dos vértices."""
    P = np.asarray(poligono, dtype=float)
    n = len(P)
    saida = []
    for i in range(n):
        u = P[(i - 1) % n] - P[i]
        v = P[(i + 1) % n] - P[i]
        cos = np.dot(u, v) / (np.linalg.norm(u) * np.linalg.norm(v))
        saida.append(np.degrees(np.arccos(np.clip(cos, -1.0, 1.0))))
    return np.array(saida)


def fator_de_area(M):
    """
    |det| da submatriz linear 2x2 = fator pelo qual QUALQUER área é
    multiplicada. O sinal indica se a orientação foi preservada (+) ou
    invertida (-). A translação não aparece aqui: ela não altera áreas.
    """
    return float(np.linalg.det(M[:2, :2]))


# --------------------------------------------------------------------------
# 4. FORMATAÇÃO
# --------------------------------------------------------------------------


def fmt_ponto(p, casas=4):
    return "(" + ", ".join(f"{v:.{casas}f}".rstrip("0").rstrip(".") or "0"
                           for v in np.asarray(p, dtype=float).ravel()) + ")"


def fmt_matriz(M, rotulo="M", casas=4):
    """Matriz em blocos de texto, alinhada, para o log de execução."""
    linhas_txt = []
    celulas = [[f"{v:.{casas}f}" for v in linha] for linha in np.asarray(M)]
    largura = max(len(c) for linha in celulas for c in linha)
    for i, linha in enumerate(celulas):
        corpo = "  ".join(c.rjust(largura) for c in linha)
        prefixo = f"{rotulo} = " if i == len(celulas) // 2 else " " * (len(rotulo) + 3)
        linhas_txt.append(f"{prefixo}| {corpo} |")
    return "\n".join(linhas_txt)


def tabela_vertices(nomes, antes, depois, casas=4):
    """Tabela 'vértice | antes | depois' para o log."""
    linhas = [f"    {'vértice':<9} {'original':<22} {'transformado':<22}",
              f"    {'-' * 9} {'-' * 22} {'-' * 22}"]
    for nome, a, d in zip(nomes, np.asarray(antes), np.asarray(depois)):
        linhas.append(f"    {nome:<9} {fmt_ponto(a, casas):<22} {fmt_ponto(d, casas):<22}")
    return "\n".join(linhas)
