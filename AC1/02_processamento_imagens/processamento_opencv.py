# -*- coding: utf-8 -*-
"""
ÁREA 2 - PROCESSAMENTO DE IMAGENS
=================================
Fluxo característico da área:   IMAGEM  ->  IMAGEM

Aplicação executada: OpenCV (repositório público: https://github.com/opencv/opencv),
biblioteca padrão da indústria para processamento de imagens, aplicada sobre a
imagem de teste `fruits.jpg` do próprio repositório do OpenCV
(opencv/samples/data/fruits.jpg).

Cada bloco reproduz um tópico do material da disciplina (arquivo files/PI.pdf):
  (A) AQUISIÇÃO      - resolução espacial (amostragem) e gradação tonal (quantização)
  (B) REALCE         - histograma, equalização de histograma
  (C) RESTAURAÇÃO    - ruído sal-e-pimenta + filtro de mediana (métrica PSNR)
  (D) REALCE/BORDAS  - convolução com máscaras de Sobel e Laplaciano
  (E) SEGMENTAÇÃO    - limiarização de Otsu + operações morfológicas
  (F) EXTRAÇÃO       - contornos e atributos das regiões segmentadas

Ponto central da área: TODAS as etapas recebem uma matriz de pixels e devolvem
outra matriz de pixels. Não há modelo geométrico e não há interpretação semântica.
"""

import json
from pathlib import Path

import cv2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"
SAIDA = AQUI / "saida"
SAIDA.mkdir(exist_ok=True)

ENTRADA = ASSETS / "fruits.jpg"


# --------------------------------------------------------------------------
# Utilidades: o caminho do projeto tem acentos, e cv2.imread/imwrite do OpenCV
# no Windows não aceita caminhos fora de ASCII. Lemos/gravamos via buffer.
# --------------------------------------------------------------------------
def ler_imagem(caminho: Path):
    dados = np.fromfile(str(caminho), dtype=np.uint8)
    img = cv2.imdecode(dados, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"não foi possível decodificar {caminho}")
    return img


def salvar_imagem(caminho: Path, img):
    ok, buf = cv2.imencode(caminho.suffix, img)
    if not ok:
        raise IOError(f"falha ao codificar {caminho}")
    buf.tofile(str(caminho))


def painel(caminho: Path, itens, titulo_geral, colunas=3, cmap_padrao="gray"):
    """
    Monta uma figura rotulada com vários resultados intermediários.
    Cada item é (imagem, título) ou (imagem, título, cmap).
    """
    linhas = int(np.ceil(len(itens) / colunas))
    alt, larg = itens[0][0].shape[:2]
    largura_celula = 4.6
    altura_celula = largura_celula * (alt / larg) + 0.55      # espaço para o título
    fig, eixos = plt.subplots(linhas, colunas,
                              figsize=(largura_celula * colunas, altura_celula * linhas),
                              constrained_layout=True)
    eixos = np.atleast_1d(eixos).ravel()
    for ax, item in zip(eixos, itens):
        img, titulo = item[0], item[1]
        cmap = item[2] if len(item) > 2 else cmap_padrao
        if img.ndim == 3:
            ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        elif cmap == cmap_padrao:
            ax.imshow(img, cmap=cmap, vmin=0, vmax=255)
        else:
            ax.imshow(img, cmap=cmap)
        ax.set_title(titulo, fontsize=11)
        ax.axis("off")
    for ax in eixos[len(itens):]:
        ax.axis("off")
    fig.suptitle(titulo_geral, fontsize=15, fontweight="bold")
    fig.savefig(caminho, dpi=110)
    plt.close(fig)


def psnr(a, b):
    """Relação sinal-ruído de pico: mede o quanto b se afastou de a."""
    eqm = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return float("inf") if eqm == 0 else 10 * np.log10(255.0 ** 2 / eqm)


def main():
    relatorio = {}
    print("=" * 74)
    print("ÁREA 2 - PROCESSAMENTO DE IMAGENS  |  OpenCV", cv2.__version__)
    print("=" * 74)

    original = ler_imagem(ENTRADA)
    altura, largura = original.shape[:2]
    print(f"\n[ENTRADA] {ENTRADA.name}: {largura}x{altura} pixels, "
          f"{original.shape[2]} canais, {original.nbytes/1024:.0f} KB em memória")
    relatorio["entrada"] = {"arquivo": ENTRADA.name, "largura": largura,
                            "altura": altura, "canais": int(original.shape[2])}

    # ======================================================================
    # (A) AQUISIÇÃO: resolução espacial e gradação tonal
    # ======================================================================
    print("\n(A) AQUISIÇÃO — amostragem (resolução) e quantização (gradação tonal)")
    itens = [(original, f"Original — {largura}x{altura}, 256 níveis/canal")]
    for divisor in (8, 32):
        pequena = cv2.resize(original, (largura // divisor, altura // divisor),
                             interpolation=cv2.INTER_AREA)
        grande = cv2.resize(pequena, (largura, altura), interpolation=cv2.INTER_NEAREST)
        itens.append((grande, f"Amostragem — {largura//divisor}x{altura//divisor}"))
        print(f"    amostragem 1/{divisor:<2d} -> {largura//divisor:3d}x{altura//divisor:3d} "
              f"({(largura//divisor)*(altura//divisor):,} pixels)")

    for niveis in (16, 4, 2):
        passo = 256 // niveis
        quant = ((original // passo) * passo + passo // 2).astype(np.uint8)
        itens.append((quant, f"Quantização — {niveis} níveis/canal"))
        print(f"    quantização {niveis:2d} níveis -> "
              f"{np.log2(niveis):.0f} bits/canal (de 8)")
    painel(SAIDA / "A_aquisicao.png", itens,
           "(A) Aquisição: efeito da resolução espacial e da quantização", colunas=3)

    # ======================================================================
    # (B) REALCE: tons de cinza, histograma e equalização
    # ======================================================================
    print("\n(B) REALCE — conversão para tons de cinza e equalização de histograma")
    cinza = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)   # Y = 0.299R+0.587G+0.114B
    escuro = np.clip(cinza * 0.45 + 20, 0, 255).astype(np.uint8)   # baixo contraste
    equalizada = cv2.equalizeHist(escuro)
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(escuro)

    for nome, img in [("cinza", cinza), ("baixo contraste", escuro),
                      ("equalizada", equalizada), ("CLAHE", clahe)]:
        print(f"    {nome:<16s} média={img.mean():6.1f}  desvio={img.std():5.1f}  "
              f"faixa=[{img.min():3d},{img.max():3d}]")
    relatorio["realce"] = {
        "desvio_baixo_contraste": round(float(escuro.std()), 2),
        "desvio_equalizado": round(float(equalizada.std()), 2),
    }

    fig, eixos = plt.subplots(2, 3, figsize=(15, 8.5))
    for coluna, (img, titulo) in enumerate([
            (escuro, "Imagem de baixo contraste"),
            (equalizada, "Equalização de histograma"),
            (clahe, "CLAHE (equalização local)")]):
        eixos[0, coluna].imshow(img, cmap="gray", vmin=0, vmax=255)
        eixos[0, coluna].set_title(titulo, fontsize=12)
        eixos[0, coluna].axis("off")
        eixos[1, coluna].hist(img.ravel(), bins=256, range=(0, 256),
                              color="#3a7bd5", alpha=0.85)
        eixos[1, coluna].set_xlim(0, 255)
        eixos[1, coluna].set_title(f"histograma — desvio padrão = {img.std():.1f}",
                                   fontsize=10)
    fig.suptitle("(B) Realce: o histograma como descritor global da imagem",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(SAIDA / "B_realce_histograma.png", dpi=110)
    plt.close(fig)

    # ======================================================================
    # (C) RESTAURAÇÃO: ruído + filtragem
    # ======================================================================
    print("\n(C) RESTAURAÇÃO — ruído sal-e-pimenta e filtros de suavização")
    rng = np.random.default_rng(42)
    ruidosa = cinza.copy()
    mascara = rng.random(cinza.shape)
    ruidosa[mascara < 0.04] = 0        # pimenta
    ruidosa[mascara > 0.96] = 255      # sal

    mediana = cv2.medianBlur(ruidosa, 3)
    gaussiano = cv2.GaussianBlur(ruidosa, (5, 5), 1.2)
    media = cv2.blur(ruidosa, (5, 5))

    metricas = {"ruidosa": psnr(cinza, ruidosa), "média 5x5": psnr(cinza, media),
                "gaussiano 5x5": psnr(cinza, gaussiano), "mediana 3x3": psnr(cinza, mediana)}
    for nome, valor in metricas.items():
        print(f"    PSNR {nome:<15s} = {valor:5.2f} dB")
    print("    -> a mediana vence porque é um filtro NÃO-LINEAR, imune a valores extremos")
    relatorio["restauracao_psnr_db"] = {k: round(v, 2) for k, v in metricas.items()}

    painel(SAIDA / "C_restauracao.png", [
        (cinza, "Original (tons de cinza)"),
        (ruidosa, f"Ruído sal-e-pimenta 8% — PSNR {metricas['ruidosa']:.1f} dB"),
        (media, f"Filtro da média 5x5 — PSNR {metricas['média 5x5']:.1f} dB"),
        (gaussiano, f"Gaussiano 5x5 — PSNR {metricas['gaussiano 5x5']:.1f} dB"),
        (mediana, f"Mediana 3x3 — PSNR {metricas['mediana 3x3']:.1f} dB"),
        (cv2.absdiff(cinza, mediana), "Resíduo |original - mediana|"),
    ], "(C) Restauração: filtragem espacial para remoção de ruído", colunas=3)

    # ======================================================================
    # (D) REALCE DE BORDAS: convolução explícita
    # ======================================================================
    print("\n(D) CONVOLUÇÃO — máscaras de Sobel e Laplaciano aplicadas na vizinhança 3x3")
    suave = cv2.GaussianBlur(cinza, (5, 5), 1.4)
    sobel_x = cv2.Sobel(suave, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(suave, cv2.CV_64F, 0, 1, ksize=3)
    magnitude = cv2.convertScaleAbs(np.hypot(sobel_x, sobel_y))
    laplaciano = cv2.convertScaleAbs(cv2.Laplacian(suave, cv2.CV_64F, ksize=3))
    canny = cv2.Canny(suave, 60, 160)

    print("    máscara Sobel_x = [[-1 0 1]   máscara Sobel_y = [[-1 -2 -1]")
    print("                       [-2 0 2]                      [ 0  0  0]")
    print("                       [-1 0 1]]                     [ 1  2  1]]")
    print(f"    pixels de borda detectados pelo Canny: {int((canny > 0).sum()):,} "
          f"({(canny > 0).mean()*100:.2f}% da imagem)")
    relatorio["bordas"] = {"pixels_canny": int((canny > 0).sum()),
                           "percentual_canny": round(float((canny > 0).mean() * 100), 2)}

    painel(SAIDA / "D_convolucao_bordas.png", [
        (cinza, "Original (tons de cinza)"),
        (cv2.convertScaleAbs(sobel_x), "Sobel X — gradiente horizontal"),
        (cv2.convertScaleAbs(sobel_y), "Sobel Y — gradiente vertical"),
        (magnitude, "Magnitude do gradiente"),
        (laplaciano, "Laplaciano (2ª derivada)"),
        (canny, "Canny (60, 160) — arestas finas"),
    ], "(D) Realce: convolução com máscaras derivativas", colunas=3)

    # ======================================================================
    # (E)(F) SEGMENTAÇÃO E EXTRAÇÃO DE ATRIBUTOS
    # ======================================================================
    # Trocamos de imagem: a segmentação por limiar só faz sentido quando o
    # histograma é bimodal (objeto claro sobre fundo escuro), como ensina o
    # material da disciplina. Usamos smarties.png, também do repositório OpenCV.
    print("\n(E) SEGMENTAÇÃO — limiarização de Otsu e morfologia matemática")
    seg_original = ler_imagem(ASSETS / "smarties.png")
    seg_cinza = cv2.cvtColor(seg_original, cv2.COLOR_BGR2GRAY)
    seg_suave = cv2.GaussianBlur(seg_cinza, (5, 5), 1.2)
    print(f"    imagem de entrada: smarties.png "
          f"({seg_original.shape[1]}x{seg_original.shape[0]}) — histograma bimodal")

    # objetos ESCUROS sobre fundo CLARO -> THRESH_BINARY_INV
    limiar, binaria = cv2.threshold(seg_suave, 0, 255,
                                    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    print(f"    limiar escolhido automaticamente por Otsu: T = {limiar:.0f}")
    print(f"    pixels classificados como objeto: {(binaria > 0).mean()*100:.1f}%")

    elemento = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    aberta = cv2.morphologyEx(binaria, cv2.MORPH_OPEN, elemento, iterations=2)
    fechada = cv2.morphologyEx(aberta, cv2.MORPH_CLOSE, elemento, iterations=2)

    n_por_limiar = len([c for c in cv2.findContours(
        fechada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if cv2.contourArea(c) > 300])
    print(f"    contornos após a morfologia: {n_por_limiar} "
          f"(objetos encostados ainda saem grudados)")

    # --- separação de objetos encostados: transformada de distância + watershed
    dist = cv2.distanceTransform(fechada, cv2.DIST_L2, 5)
    _, primeiro_plano = cv2.threshold(dist, 0.60 * dist.max(), 255, 0)
    primeiro_plano = np.uint8(primeiro_plano)
    fundo = cv2.dilate(fechada, elemento, iterations=3)
    desconhecido = cv2.subtract(fundo, primeiro_plano)

    n_marcadores, marcadores = cv2.connectedComponents(primeiro_plano)
    marcadores = marcadores + 1
    marcadores[desconhecido == 255] = 0
    marcadores = cv2.watershed(seg_original.copy(), marcadores)
    print(f"    watershed sobre a transformada de distância: "
          f"{n_marcadores - 1} objetos separados")

    print("\n(F) EXTRAÇÃO DE ATRIBUTOS — contornos das regiões segmentadas")
    anotada = seg_original.copy()
    regioes = []
    rotulos = [r for r in np.unique(marcadores) if r > 1]
    caixas = []
    for rotulo in rotulos:
        mascara_r = np.uint8(marcadores == rotulo) * 255
        cs, _ = cv2.findContours(mascara_r, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not cs:
            continue
        c = max(cs, key=cv2.contourArea)
        if cv2.contourArea(c) < 300:
            continue
        caixas.append(c)
    caixas.sort(key=lambda c: (cv2.boundingRect(c)[1] // 60, cv2.boundingRect(c)[0]))

    for i, c in enumerate(caixas, 1):
        area = cv2.contourArea(c)
        perimetro = cv2.arcLength(c, True)
        circularidade = 4 * np.pi * area / (perimetro ** 2) if perimetro else 0.0
        x, y, w, h = cv2.boundingRect(c)
        cv2.drawContours(anotada, [c], -1, (0, 255, 255), 2)
        cv2.putText(anotada, str(i), (x + w // 2 - 10, y + h // 2 + 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
        regioes.append({"id": i, "area_px": int(area), "perimetro_px": round(perimetro, 1),
                        "circularidade": round(circularidade, 3),
                        "caixa": [int(x), int(y), int(w), int(h)]})
        print(f"    região {i:2d}: área={int(area):6,d} px  perímetro={perimetro:6.1f} px  "
              f"circularidade={circularidade:.3f}")
    areas = np.array([r["area_px"] for r in regioes], dtype=float)
    print(f"    -> {len(regioes)} regiões; área média = {areas.mean():,.0f} px "
          f"(desvio {areas.std():,.0f}); circularidade média = "
          f"{np.mean([r['circularidade'] for r in regioes]):.3f}")
    print("    OBS.: são ATRIBUTOS GEOMÉTRICOS. O sistema não sabe o QUE é cada objeto —")
    print("          nomear o objeto já é tarefa de Visão Computacional (área 3).")
    relatorio["segmentacao"] = {"imagem": "smarties.png", "limiar_otsu": float(limiar),
                                "contornos_apenas_limiar": n_por_limiar,
                                "n_regioes_watershed": len(regioes), "regioes": regioes}

    dist_vis = cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    painel(SAIDA / "E_segmentacao.png", [
        (seg_original, "Entrada: smarties.png (repositório OpenCV)"),
        (binaria, f"Limiarização de Otsu (T={limiar:.0f})"),
        (fechada, f"Morfologia — {n_por_limiar} contornos (objetos grudados)"),
        (dist_vis, "Transformada de distância", "magma"),
        (np.clip(marcadores, 0, None), f"Watershed — {len(regioes)} rótulos", "nipy_spectral"),
        (anotada, f"Atributos extraídos de {len(regioes)} regiões"),
    ], "(E)+(F) Segmentação por limiar, morfologia e extração de atributos", colunas=3)

    # imagens individuais em resolução plena
    for nome, img in [("cinza", cinza), ("equalizada", equalizada), ("ruidosa", ruidosa),
                      ("mediana", mediana), ("canny", canny), ("otsu", fechada),
                      ("contornos", anotada)]:
        salvar_imagem(SAIDA / f"pi_{nome}.png", img)

    print("\n" + "-" * 74)
    print("BALANÇO DA ÁREA (entrada -> saída)")
    print("-" * 74)
    print(f"  ENTRADA : imagem MATRICIAL {largura}x{altura}x3")
    print(f"  SAÍDA   : imagem MATRICIAL {largura}x{altura} (mesma natureza de dado)")
    print("  A informação é sempre reorganizada dentro da própria grade de pixels.")
    print("  O sistema não sabe que são frutas — só conhece intensidades e vizinhanças.")

    (SAIDA / "relatorio.json").write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nArquivos gerados em: {SAIDA}")


if __name__ == "__main__":
    main()
