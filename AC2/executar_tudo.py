# -*- coding: utf-8 -*-
"""
EXECUTOR DO ESTUDO DIRIGIDO 02
===============================
Roda os dez exercícios e as figuras de síntese, gravando:

  * saida/*.png              uma figura por exercício + as de síntese
  * saida/resultados.json    todas as coordenadas e matrizes apuradas
  * saida/log_execucao.txt   a saída de console completa desta execução

Uso:
    python executar_tudo.py
"""

import io
import json
import sys
import time
from pathlib import Path

import numpy as np

import transformacoes as tg
import exercicios
import figuras_extra

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI / "saida"


class Espelho(io.TextIOBase):
    """Duplica o stdout: uma cópia para o terminal, outra para o log."""

    def __init__(self, destino):
        self.destino = destino
        self.buffer_texto = io.StringIO()

    def write(self, texto):
        self.destino.write(texto)
        self.buffer_texto.write(texto)
        return len(texto)

    def flush(self):
        self.destino.flush()

    @property
    def texto(self):
        return self.buffer_texto.getvalue()


def verificar_invariantes():
    """
    Confere as identidades algébricas que o trabalho afirma no texto.
    Se qualquer uma falhar, a execução para — os números do README só valem
    se estas igualdades valerem.
    """
    exercicios.titulo("VERIFICAÇÃO ALGÉBRICA — identidades usadas no relatório")
    checagens = []

    def checar(descricao, condicao):
        checagens.append((descricao, bool(condicao)))
        print(f"  [{'ok' if condicao else 'FALHOU'}] {descricao}")

    P = np.array([[3.0, 2.0], [1.0, -4.0], [0.0, 0.0], [-2.5, 7.25]])

    T, R, S = tg.translacao(1, -1), tg.rotacao(90), tg.escala(2)
    passo = tg.aplicar(S, tg.aplicar(R, tg.aplicar(T, P)))
    checar("compor(S,R,T) == aplicar T, depois R, depois S",
           np.allclose(tg.aplicar(tg.compor(S, R, T), P), passo))

    checar("a composição NÃO comuta: S.R.T != T.R.S",
           not np.allclose(tg.compor(S, R, T), tg.compor(T, R, S)))

    checar("T(4,-2) . T(-4,2) == identidade  (translação é invertível)",
           np.allclose(tg.compor(tg.translacao(4, -2), tg.translacao(-4, 2)),
                       np.eye(3)))

    checar("R(45°) . R(45°) == R(90°)  (rotações somam ângulos)",
           np.allclose(tg.compor(tg.rotacao(45), tg.rotacao(45)), tg.rotacao(90)))

    checar("R(θ) é ortogonal: R . Rᵀ == identidade",
           np.allclose(tg.rotacao(-45)[:2, :2] @ tg.rotacao(-45)[:2, :2].T,
                       np.eye(2)))

    checar("Fy . Fy == identidade  (reflexão é a própria inversa)",
           np.allclose(tg.compor(tg.reflexao_eixo_y(), tg.reflexao_eixo_y()),
                       np.eye(3)))

    checar("Fx . Fy == R(180°)  (duas reflexões ortogonais = meia volta)",
           np.allclose(tg.compor(tg.reflexao_eixo_x(), tg.reflexao_eixo_y()),
                       tg.rotacao(180)))

    checar("det(R) = +1 e det(Fx) = -1",
           np.isclose(tg.fator_de_area(tg.rotacao(-45)), 1.0)
           and np.isclose(tg.fator_de_area(tg.reflexao_eixo_x()), -1.0))

    quad = np.array([[1.0, 1.0], [1.0, 4.0], [4.0, 4.0], [4.0, 1.0]])
    M = tg.compor(tg.reflexao_eixo_y(), tg.escala(1.5, 0.5), tg.translacao(-2, 3))
    checar("|det(M)| prevê o fator de área de uma composição",
           np.isclose(abs(tg.area_com_sinal(tg.aplicar(M, quad))),
                      abs(tg.area_com_sinal(quad) * tg.fator_de_area(M))))

    checar("cisalhamento preserva área: det(H) = 1",
           np.isclose(tg.fator_de_area(tg.cisalhamento_horizontal(2)), 1.0))

    T_c = tg.translacao(2.5, 2.5)
    girar_no_lugar = tg.compor(T_c, tg.rotacao(-45), np.linalg.inv(T_c))
    checar("T . R . T⁻¹ gira em torno do baricentro (o centro fica parado)",
           np.allclose(tg.aplicar(girar_no_lugar, [2.5, 2.5])[0], [2.5, 2.5]))

    falhas = [d for d, ok in checagens if not ok]
    print(f"\n  {len(checagens) - len(falhas)}/{len(checagens)} verificações passaram.")
    if falhas:
        raise AssertionError("verificações falharam: " + "; ".join(falhas))
    return len(checagens)


def main():
    SAIDA.mkdir(exist_ok=True)
    espelho = Espelho(sys.stdout)
    original = sys.stdout
    sys.stdout = espelho
    inicio = time.perf_counter()

    try:
        print("ESTUDO DIRIGIDO 02 — TRANSFORMAÇÕES GEOMÉTRICAS 2D")
        print("Transformações em coordenadas homogêneas 3x3, plotagem com Matplotlib.")
        print(f"numpy {np.__version__} | "
              f"matplotlib {__import__('matplotlib').__version__} | "
              f"python {sys.version.split()[0]}")

        resultados = []
        for funcao in exercicios.EXERCICIOS:
            resultados.append(funcao())

        n_verificacoes = verificar_invariantes()

        exercicios.titulo("FIGURAS DE SÍNTESE")
        for funcao in figuras_extra.EXTRAS:
            print(f"  figura -> {funcao().name}")
        print(f"  figura -> {figuras_extra.painel_exercicios().name}")

        duracao = time.perf_counter() - inicio

        exercicios.titulo("RESUMO DAS RESPOSTAS")
        for r in resultados:
            print(f"  {r['exercicio']:>2}. {r['nome']:<42} {r['resposta']}")

        (SAIDA / "resultados.json").write_text(
            json.dumps({"exercicios": resultados,
                        "verificacoes_algebricas": n_verificacoes,
                        "duracao_s": round(duracao, 3)},
                       indent=2, ensure_ascii=False), encoding="utf-8")

        print(f"\n  {len(resultados)} exercícios resolvidos, "
              f"{n_verificacoes} verificações algébricas, "
              f"{len(list(SAIDA.glob('*.png')))} figuras geradas em {duracao:.2f} s.")
        print(f"  Saída em: {SAIDA}")
        return 0
    finally:
        sys.stdout = original
        (SAIDA / "log_execucao.txt").write_text(espelho.texto, encoding="utf-8")
        print(f"\nLog completo em: {SAIDA / 'log_execucao.txt'}")


if __name__ == "__main__":
    sys.exit(main())
