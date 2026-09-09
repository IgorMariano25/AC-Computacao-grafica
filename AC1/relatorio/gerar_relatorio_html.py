# -*- coding: utf-8 -*-
"""
Monta o relatório HTML autocontido a partir de `relatorio_modelo.html`.

Cada marcador {{IMG:caminho/relativo.png}} do modelo é substituído por uma
URI `data:` com a figura já reduzida e recomprimida em WebP, de modo que o
arquivo final possa ser aberto ou compartilhado sozinho, sem a pasta de saídas.
"""

import base64
import io
import re
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
BASE = AQUI.parent
MODELO = AQUI / "relatorio_modelo.html"
DESTINO = AQUI / "relatorio.html"

LARGURA_MAXIMA = 1500
QUALIDADE = 82


def embutir(caminho_relativo: str) -> str:
    origem = BASE / caminho_relativo
    if not origem.exists():
        raise FileNotFoundError(f"figura ausente: {origem} — execute executar_tudo.py antes")
    img = Image.open(origem).convert("RGB")
    if img.width > LARGURA_MAXIMA:
        altura = round(img.height * LARGURA_MAXIMA / img.width)
        img = img.resize((LARGURA_MAXIMA, altura), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="WEBP", quality=QUALIDADE, method=5)
    dados = base64.b64encode(buf.getvalue()).decode("ascii")
    print(f"  {caminho_relativo:<58s} {origem.stat().st_size/1024:7.0f} KB "
          f"-> {len(dados)/1024:7.0f} KB (base64)")
    return "data:image/webp;base64," + dados


def main():
    print("Embutindo figuras no relatório HTML:")
    html = MODELO.read_text(encoding="utf-8")
    html = re.sub(r"\{\{IMG:([^}]+)\}\}", lambda m: embutir(m.group(1).strip()), html)
    DESTINO.write_text(html, encoding="utf-8")
    print(f"\n{DESTINO}  ({DESTINO.stat().st_size/1024/1024:.2f} MB)")


if __name__ == "__main__":
    main()
