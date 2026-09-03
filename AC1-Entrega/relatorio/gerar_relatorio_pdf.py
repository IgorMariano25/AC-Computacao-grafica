# -*- coding: utf-8 -*-
"""
Converte `relatorio.html` em `relatorio.pdf` usando o modo headless do
Chrome ou do Edge — o mesmo motor que renderiza a versão publicada, de forma
que o PDF sai idêntico ao que se vê no navegador.

O HTML é copiado para uma pasta temporária de caminho ASCII antes da impressão:
o caminho do projeto contém acentos, e o navegador headless nem sempre resolve
`file:///` com caracteres fora de ASCII no Windows.

Uso:
    python gerar_relatorio_pdf.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
HTML = AQUI / "relatorio.html"
PDF = AQUI / "relatorio.pdf"

NAVEGADORES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
]


def achar_navegador() -> Path:
    for caminho in NAVEGADORES:
        if caminho.exists():
            return caminho
    for nome in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        encontrado = shutil.which(nome)
        if encontrado:
            return Path(encontrado)
    raise FileNotFoundError(
        "nenhum navegador baseado em Chromium encontrado — instale o Chrome ou o Edge")


def main():
    if not HTML.exists():
        raise FileNotFoundError(f"{HTML} não existe — execute gerar_relatorio_html.py antes")

    navegador = achar_navegador()
    print(f"navegador ....: {navegador}")
    print(f"entrada ......: {HTML.name}  ({HTML.stat().st_size/1024/1024:.2f} MB)")

    with tempfile.TemporaryDirectory(prefix="relatorio_pdf_") as tmp:
        trabalho = Path(tmp)
        origem = trabalho / "relatorio.html"
        destino = trabalho / "relatorio.pdf"
        shutil.copy2(HTML, origem)

        comando = [
            str(navegador),
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=20000",     # tempo para baixar as fontes
            f"--user-data-dir={trabalho / 'perfil'}",
            f"--print-to-pdf={destino}",
            origem.as_uri(),
        ]
        proc = subprocess.run(comando, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=180)
        if not destino.exists():
            print(proc.stdout)
            print(proc.stderr)
            raise RuntimeError(f"o navegador não gerou o PDF (código {proc.returncode})")
        shutil.copy2(destino, PDF)

    print(f"saída ........: {PDF}  ({PDF.stat().st_size/1024/1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
