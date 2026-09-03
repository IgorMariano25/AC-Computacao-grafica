# -*- coding: utf-8 -*-
"""
ÁREA 4 - VISUALIZAÇÃO COMPUTACIONAL
===================================
Fluxo característico da área:   DADOS (não-visuais)  ->  IMAGEM PARA ANÁLISE

A área usa as MESMAS técnicas de síntese da Área 1, mas com um objetivo
diferente: o objetivo não é reproduzir a aparência de um objeto, e sim
tornar compreensível um fenômeno ou um conjunto de dados.

O material da disciplina divide a área em duas frentes (slide 50):
  SciVis  - a geometria do modelo é DETERMINADA PELO DOMÍNIO
            (o joelho tem uma forma; ela vem do tomógrafo, não do projetista)
  InfoVis - a geometria do modelo é ATRIBUÍDA PELO PROJETISTA
            (não existe uma "posição natural" de um país num gráfico)

PARTE A - VISUALIZAÇÃO CIENTÍFICA
  Aplicação: VTK / Visualization Toolkit (repositório público
  https://github.com/Kitware/VTK) acessado pelo PyVista
  (https://github.com/pyvista/pyvista). O slide 54 cita literalmente
  "Rendering Volumétrico Direto: ray casting no Visualization Toolkit".
  Dado: tomografia computadorizada de um joelho, do repositório público
  https://github.com/pyvista/vtk-data.

PARTE B - VISUALIZAÇÃO DE INFORMAÇÃO
  Aplicação: reprodução do gráfico do Gapminder (citado no slide 62)
  com Matplotlib (https://github.com/matplotlib/matplotlib), sobre o
  conjunto público https://github.com/plotly/datasets (gapminder2007.csv).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyvista as pv
from pyvista import examples
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image, ImageDraw, ImageFont

pv.OFF_SCREEN = True

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"
SAIDA = AQUI / "saida"
SAIDA.mkdir(exist_ok=True)

JANELA = (900, 900)


def rotular(caminho: Path, texto):
    """
    Grava uma cópia rotulada ao lado da imagem gerada pelo VTK.
    A imagem original é preservada sem rótulo, para reaproveitamento.
    """
    img = Image.open(caminho).convert("RGB")
    desenho = ImageDraw.Draw(img)
    try:
        fonte = ImageFont.truetype("arialbd.ttf", 24)
    except OSError:
        fonte = ImageFont.load_default()
    desenho.rectangle([0, 0, img.width, 44], fill=(18, 20, 26))
    desenho.text((16, 10), texto, fill=(240, 240, 245), font=fonte)
    destino = caminho.with_name(caminho.stem + "_rotulada.png")
    img.save(destino)
    return destino


# ==========================================================================
# PARTE A - VISUALIZAÇÃO CIENTÍFICA (SciVis)
# ==========================================================================
def parte_a():
    print("\n" + "=" * 74)
    print("PARTE A - VISUALIZAÇÃO CIENTÍFICA  |  VTK/PyVista, tomografia de joelho")
    print("=" * 74)

    volume = examples.download_knee_full()
    nx, ny, nz = volume.dimensions
    valores = volume.active_scalars
    print(f"\n[DADO DE ENTRADA] campo escalar 3D amostrado em grade regular")
    print(f"    dimensões da grade .........: {nx} x {ny} x {nz}")
    print(f"    total de voxels ............: {volume.n_points:,}")
    print(f"    espaçamento (mm) ...........: {volume.spacing}")
    print(f"    faixa de intensidade .......: {valores.min()} a {valores.max()}")
    print(f"    memória do campo ...........: {valores.nbytes/1024/1024:.1f} MB")
    print("    -> NÃO é uma imagem e NÃO é uma malha: é uma FUNÇÃO f(x,y,z) medida.")

    relatorio = {"dimensoes": [int(nx), int(ny), int(nz)],
                 "n_voxels": int(volume.n_points),
                 "espacamento": [float(s) for s in volume.spacing],
                 "faixa": [int(valores.min()), int(valores.max())]}

    # ---------- A1: cortes ortogonais (a visualização mais direta) --------
    print("\n[A1] CORTES ORTOGONAIS — mapeia intensidade para cor, sem geometria 3D")
    cortes = volume.slice_orthogonal()
    p = pv.Plotter(off_screen=True, window_size=JANELA)
    p.add_mesh(cortes, cmap="gray", clim=[0, 120],
               scalar_bar_args={"title": "intensidade CT"})
    p.background_color = "#12141a"
    p.camera_position = "iso"
    p.screenshot(SAIDA / "A1_cortes_ortogonais.png")
    p.close()
    rotular(SAIDA / "A1_cortes_ortogonais.png",
            "A1. Cortes ortogonais (mapeamento escalar -> cor)")
    print("    -> saida/A1_cortes_ortogonais.png")

    # ---------- A2: isosuperfície (marching cubes) ------------------------
    print("\n[A2] ISOSUPERFÍCIE — extrai geometria do campo e cai no pipeline da Área 1")
    # o histograma mostra o tecido mole concentrado perto de 62 e o osso acima de 105
    iso_pele, iso_osso = 62, 108
    pele = volume.contour([iso_pele])
    osso = volume.contour([iso_osso])
    print(f"    algoritmo ..................: marching cubes (vtkContourFilter)")
    print(f"    isovalor {iso_pele} (tecido mole) -> {pele.n_cells:,} triângulos")
    print(f"    isovalor {iso_osso} (osso) ........ -> {osso.n_cells:,} triângulos")
    print(f"    -> a partir daqui é rasterização comum: MALHA -> IMAGEM (Área 1)")
    relatorio["isosuperficie"] = {"isovalor_pele": iso_pele, "isovalor_osso": iso_osso,
                                  "triangulos_pele": int(pele.n_cells),
                                  "triangulos_osso": int(osso.n_cells)}

    p = pv.Plotter(off_screen=True, window_size=JANELA)
    p.add_mesh(pele, color="#c98f6b", opacity=0.16, smooth_shading=True)
    p.add_mesh(osso, color="#f2ead6", opacity=1.0, smooth_shading=True)
    p.background_color = "#12141a"
    p.camera_position = "yz"
    p.camera.azimuth = 35
    p.camera.elevation = 18
    p.screenshot(SAIDA / "A2_isosuperficie.png")
    p.close()
    rotular(SAIDA / "A2_isosuperficie.png",
            f"A2. Isosuperficies - {osso.n_cells + pele.n_cells:,} triangulos "
            f"(marching cubes)")
    print("    -> saida/A2_isosuperficie.png")

    # ---------- A3: rendering volumétrico direto (ray casting) ------------
    print("\n[A3] RENDERING VOLUMÉTRICO DIRETO — ray casting, SEM extrair geometria")
    print("    técnica citada no slide 54 do material da disciplina")
    print("    o raio de cada pixel atravessa o volume acumulando cor e opacidade;")
    print("    quem decide o que aparece é a FUNÇÃO DE TRANSFERÊNCIA (valor -> opacidade)")

    # função de transferência: ar transparente, tecido mole translúcido, osso opaco.
    # os 6 valores são amostrados uniformemente na faixa 0..174 do tomógrafo.
    tf_osso = [0.00, 0.00, 0.00, 0.05, 0.60, 0.95]
    tf_completa = [0.00, 0.00, 0.010, 0.06, 0.70, 0.98]
    pontos = np.linspace(int(valores.min()), int(valores.max()), len(tf_osso))
    print("    pontos de controle .........: " +
          "  ".join(f"{int(v)}" for v in pontos))
    print(f"    opacidade (realce do osso) .: {tf_osso}")
    print(f"    opacidade (osso + tecido) ..: {tf_completa}")
    relatorio["dvr"] = {"pontos_controle": [int(v) for v in pontos],
                        "tf_osso": tf_osso, "tf_completa": tf_completa}

    # mapa de cores no estilo médico: tecido avermelhado, osso claro
    cmap_medico = matplotlib.colors.LinearSegmentedColormap.from_list(
        "medico", ["#12080a", "#8c3b28", "#c98f6b", "#e8d9b8", "#ffffff"])

    for nome, opac, cmap, legenda in [
            ("A3_dvr_osso", tf_osso, "bone",
             "A3. DVR - funcao de transferencia realca o OSSO"),
            ("A3_dvr_completo", tf_completa, cmap_medico,
             "A3. DVR - mesma tomografia, transferencia mostra TECIDO + OSSO")]:
        p = pv.Plotter(off_screen=True, window_size=JANELA)
        p.add_volume(volume, cmap=cmap, opacity=opac, shade=True,
                     scalar_bar_args={"title": "intensidade CT"})
        p.background_color = "#12141a"
        p.camera_position = "yz"
        p.camera.azimuth = 35
        p.camera.elevation = 18
        p.screenshot(SAIDA / f"{nome}.png")
        p.close()
        rotular(SAIDA / f"{nome}.png", legenda)
        print(f"    -> saida/{nome}.png")

    # ---------- montagem comparativa SciVis -------------------------------
    nomes = ["A1_cortes_ortogonais", "A2_isosuperficie", "A3_dvr_osso", "A3_dvr_completo"]
    montagem = Image.new("RGB", (JANELA[0] * 2, JANELA[1] * 2), (18, 20, 26))
    for i, nome in enumerate(nomes):
        montagem.paste(Image.open(SAIDA / f"{nome}_rotulada.png").convert("RGB"),
                       ((i % 2) * JANELA[0], (i // 2) * JANELA[1]))
    montagem.resize((1300, 1300), Image.LANCZOS).save(SAIDA / "A_scivis_montagem.png")
    print("\n    -> saida/A_scivis_montagem.png (comparativo das três técnicas)")

    # histograma do campo escalar: a base para escolher a função de transferência
    fig, ax = plt.subplots(figsize=(9, 4.2), constrained_layout=True)
    ax.hist(valores[::13], bins=180, color="#4a7fd4", log=True)
    ax.set_xlabel("intensidade do voxel (unidades do tomógrafo)")
    ax.set_ylabel("nº de voxels (escala log)")
    ax.set_title("Histograma do campo escalar — guia para a função de transferência")
    for x, rotulo in [(20, "ar / fundo"), (75, "tecido mole"), (140, "osso")]:
        ax.axvline(x, color="#d4574a", ls="--", lw=1.2)
        ax.text(x + 3, ax.get_ylim()[1] * 0.25, rotulo, rotation=90,
                color="#d4574a", fontsize=9)
    fig.savefig(SAIDA / "A_histograma_campo.png", dpi=115)
    plt.close(fig)

    print("\n    BALANÇO SciVis: entrada = {:,} voxels ({:.1f} MB) -> saída = imagem {}x{}"
          .format(volume.n_points, valores.nbytes / 1024 / 1024, *JANELA))
    print("    A geometria vem do DOMÍNIO (a anatomia). O projetista escolhe apenas")
    print("    o MAPEAMENTO visual (cor e opacidade), não a forma.")
    return relatorio


# ==========================================================================
# PARTE B - VISUALIZAÇÃO DE INFORMAÇÃO (InfoVis)
# ==========================================================================
def parte_b():
    print("\n" + "=" * 74)
    print("PARTE B - VISUALIZAÇÃO DE INFORMAÇÃO  |  Gapminder 2007 (slide 62)")
    print("=" * 74)

    dados = pd.read_csv(ASSETS / "gapminder2007.csv")
    print(f"\n[DADO DE ENTRADA] tabela sem qualquer geometria associada")
    print(f"    registros ..................: {len(dados)} países")
    print(f"    variáveis ..................: {list(dados.columns)}")
    print(f"    memória ....................: {dados.memory_usage(deep=True).sum()/1024:.1f} KB")
    print("    -> um país NÃO tem posição (x,y) natural: ela precisa ser INVENTADA.")

    print("\n[MAPEAMENTO VISUAL escolhido pelo projetista]")
    canais = [("posição X", "PIB per capita (US$, escala logarítmica)"),
              ("posição Y", "expectativa de vida (anos)"),
              ("área do círculo", "população"),
              ("cor", "continente (variável categórica)")]
    for canal, variavel in canais:
        print(f"    {canal:<18s} <- {variavel}")

    cores = {"Africa": "#e15759", "Americas": "#4e79a7", "Asia": "#f28e2b",
             "Europe": "#59a14f", "Oceania": "#b07aa1"}
    ESCALA_AREA = 5.0e5          # habitantes por ponto² de área do círculo
    fig, ax = plt.subplots(figsize=(12.5, 7.6), constrained_layout=True)
    for continente, grupo in dados.groupby("continent"):
        ax.scatter(grupo["gdpPercap"], grupo["lifeExp"],
                   s=grupo["pop"] / ESCALA_AREA, alpha=0.62,
                   color=cores.get(continente, "#888888"),
                   edgecolor="white", linewidth=0.7, label=continente, zorder=3)

    destaques = ["China", "India", "United States", "Brazil", "Nigeria", "Japan"]
    for _, linha in dados[dados["country"].isin(destaques)].iterrows():
        ax.annotate(linha["country"],
                    (linha["gdpPercap"], linha["lifeExp"]),
                    textcoords="offset points", xytext=(0, 13),
                    ha="center", fontsize=9.5, fontweight="bold", zorder=4)

    ax.set_xscale("log")
    ax.set_xlabel("PIB per capita (US$, escala logarítmica)", fontsize=11)
    ax.set_ylabel("Expectativa de vida ao nascer (anos)", fontsize=11)
    ax.set_title("Visualização de Informação — Gapminder 2007: "
                 "riqueza x longevidade, 142 países\n"
                 "posição, área e cor são convenções escolhidas pelo projetista",
                 fontsize=13, fontweight="bold")
    ax.grid(alpha=0.25, zorder=0)
    legenda_cont = ax.legend(title="Continente (cor)", loc="lower right",
                             fontsize=9.5, framealpha=0.95)
    legenda_cont.set_zorder(6)
    ax.add_artist(legenda_cont)

    marcadores = [Line2D([], [], marker="o", ls="", markerfacecolor="#9a9a9a",
                         markeredgecolor="white", alpha=0.62,
                         markersize=np.sqrt(p / ESCALA_AREA),
                         label=f"{p/1e6:,.0f} mi")
                  for p in (5e7, 2.5e8, 1.2e9)]
    legenda_pop = ax.legend(handles=marcadores, title="População (área do círculo)",
                            loc="upper left", fontsize=9.5, labelspacing=1.7,
                            borderpad=1.0, handletextpad=1.6, framealpha=0.95)
    legenda_pop.set_zorder(6)

    fig.savefig(SAIDA / "B_infovis_gapminder.png", dpi=120)
    plt.close(fig)
    print("\n    -> saida/B_infovis_gapminder.png")

    correlacao = np.corrcoef(np.log10(dados["gdpPercap"]), dados["lifeExp"])[0, 1]
    print(f"\n    Leitura possibilitada pelo gráfico:")
    print(f"      correlação log(PIB) x expectativa de vida = {correlacao:.3f}")
    print(f"      expectativa de vida: {dados['lifeExp'].min():.1f} a "
          f"{dados['lifeExp'].max():.1f} anos")
    for c, g in dados.groupby("continent"):
        print(f"      {c:<9s} n={len(g):3d}  vida média={g['lifeExp'].mean():5.1f} anos  "
              f"PIB mediano=US$ {g['gdpPercap'].median():>9,.0f}")
    print("\n    BALANÇO InfoVis: entrada = {} linhas x {} colunas -> saída = 1 imagem"
          .format(len(dados), len(dados.columns)))
    print("    A geometria é ARBITRÁRIA (convenção). Ler o gráfico exige treino:")
    print("    é preciso saber que o eixo X é logarítmico e que a ÁREA (não o raio)")
    print("    codifica a população.")

    return {"n_paises": int(len(dados)),
            "variaveis": list(dados.columns),
            "correlacao_logPIB_expVida": round(float(correlacao), 4)}


def main():
    print("=" * 74)
    print("ÁREA 4 - VISUALIZAÇÃO COMPUTACIONAL")
    print("=" * 74)
    print(f"VTK {pv.vtk_version_info.major}.{pv.vtk_version_info.minor} | PyVista {pv.__version__}")

    relatorio = {"scivis": parte_a(), "infovis": parte_b()}

    print("\n" + "-" * 74)
    print("BALANÇO DA ÁREA (entrada -> saída)")
    print("-" * 74)
    print("  ENTRADA : DADOS que não são imagem nem modelo geométrico de um objeto")
    print("            (campo escalar medido, tabela de indicadores)")
    print("  SAÍDA   : imagem cujo propósito é a ANÁLISE, não o realismo")
    print("  A área compartilha o motor de renderização com a Área 1, mas o produto")
    print("  é entendimento: a pergunta não é 'ficou bonito?' e sim 'ficou legível?'.")

    (SAIDA / "relatorio.json").write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nArquivos gerados em: {SAIDA}")


if __name__ == "__main__":
    main()
