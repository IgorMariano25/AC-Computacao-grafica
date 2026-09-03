# -*- coding: utf-8 -*-
"""
Executa, em sequência, os quatro programas da entrega e o quadro comparativo,
gravando a saída de console de cada um em `relatorio/log_execucao.txt`.

Uso:
    python executar_tudo.py
"""

import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LOG = AQUI / "relatorio" / "log_execucao.txt"
LOG.parent.mkdir(exist_ok=True)

PROGRAMAS = [
    ("Área 1 — Síntese de Imagens",
     AQUI / "01_sintese_imagens" / "sintese_opengl.py"),
    ("Área 2 — Processamento de Imagens",
     AQUI / "02_processamento_imagens" / "processamento_opencv.py"),
    ("Área 3 — Visão Computacional",
     AQUI / "03_visao_computacional" / "visao_yolo.py"),
    ("Área 4 — Visualização Computacional",
     AQUI / "04_visualizacao_computacional" / "visualizacao_vtk.py"),
    ("Quadro comparativo",
     AQUI / "00_comparativo" / "gerar_comparativo.py"),
]


def main():
    partes, falhas = [], []
    for titulo, script in PROGRAMAS:
        print(f"\n>>> {titulo}  ({script.name})", flush=True)
        inicio = time.perf_counter()
        proc = subprocess.run([sys.executable, str(script)], cwd=script.parent,
                              capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        duracao = time.perf_counter() - inicio
        print(proc.stdout, end="")
        if proc.returncode != 0:
            falhas.append(titulo)
            print(f"!!! FALHOU (código {proc.returncode})", flush=True)
            print(proc.stderr[-2500:], flush=True)
        else:
            print(f"    concluído em {duracao:.1f} s", flush=True)

        partes.append(
            f"{'=' * 78}\n{titulo}\narquivo: {script.relative_to(AQUI)}\n"
            f"duração: {duracao:.1f} s | código de saída: {proc.returncode}\n"
            f"{'=' * 78}\n{proc.stdout}\n"
            + (f"[stderr]\n{proc.stderr}\n" if proc.returncode != 0 else ""))

    LOG.write_text("\n".join(partes), encoding="utf-8")
    print(f"\nLog completo em: {LOG}")
    if falhas:
        print("Programas que falharam: " + ", ".join(falhas))
        return 1
    print("Todos os programas foram executados com sucesso.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
