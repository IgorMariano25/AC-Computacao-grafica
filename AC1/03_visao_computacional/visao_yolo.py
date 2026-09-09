# -*- coding: utf-8 -*-
"""
ÁREA 3 - VISÃO COMPUTACIONAL (VISÃO ARTIFICIAL)
===============================================
Fluxo característico da área:   IMAGEM  ->  DESCRIÇÃO SIMBÓLICA (DADOS)

Aplicação executada: detector de objetos YOLO, na implementação Ultralytics
(repositório público: https://github.com/ultralytics/ultralytics), com os pesos
pré-treinados `yolov8n.pt` no conjunto COCO (80 classes). A imagem de teste
`bus.jpg` vem do repositório público https://github.com/ultralytics/assets.

O slide 28 do material da disciplina cita exatamente o YOLO
(https://pjreddie.com/darknet/yolo/) como exemplo da área.

O programa é organizado segundo os seis passos do "típico sistema de visão"
apresentados nos slides 31 a 45 da aula de introdução:
  PASSO 1 - AQUISIÇÃO
  PASSO 2 - PRÉ-PROCESSAMENTO
  PASSO 3 - PROCESSAMENTO DE IMAGEM
  PASSO 4 - ANÁLISE DE IMAGEM
  PASSO 5 - EXTRAÇÃO DE CARACTERÍSTICAS
  PASSO 6 - IA / RECONHECIMENTO DE PADRÕES

Ao final compara-se a abordagem clássica (descritor HOG + SVM, características
projetadas à mão) com a abordagem por aprendizado profundo (características
aprendidas pela rede) sobre a MESMA imagem.
"""

import json
import os
import time
from pathlib import Path

os.environ.setdefault("YOLO_VERBOSE", "false")

import cv2
import numpy as np
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ultralytics import YOLO

AQUI = Path(__file__).resolve().parent
ASSETS = AQUI.parent / "assets"
SAIDA = AQUI / "saida"
SAIDA.mkdir(exist_ok=True)

ENTRADA = ASSETS / "bus.jpg"
PESOS = AQUI / "yolov8n.pt"
TAMANHO_REDE = 640


def ler_imagem(caminho: Path):
    img = cv2.imdecode(np.fromfile(str(caminho), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(caminho)
    return img


def salvar_imagem(caminho: Path, img):
    ok, buf = cv2.imencode(caminho.suffix, img)
    if not ok:
        raise IOError(caminho)
    buf.tofile(str(caminho))


def letterbox(img, tamanho=640, cor=(114, 114, 114)):
    """Redimensiona preservando a proporção e completa com borda (pré-processamento
    padrão do YOLO). Devolve a imagem e os parâmetros da transformação."""
    alt, larg = img.shape[:2]
    escala = min(tamanho / alt, tamanho / larg)
    nova = (int(round(larg * escala)), int(round(alt * escala)))
    redim = cv2.resize(img, nova, interpolation=cv2.INTER_LINEAR)
    dw, dh = tamanho - nova[0], tamanho - nova[1]
    topo, base = dh // 2, dh - dh // 2
    esq, dir_ = dw // 2, dw - dw // 2
    saida = cv2.copyMakeBorder(redim, topo, base, esq, dir_,
                               cv2.BORDER_CONSTANT, value=cor)
    return saida, escala, (esq, topo)


def main():
    relatorio = {}
    print("=" * 74)
    print("ÁREA 3 - VISÃO COMPUTACIONAL  |  Ultralytics YOLOv8n (COCO, 80 classes)")
    print("=" * 74)

    # ======================================================================
    # PASSO 1 - AQUISIÇÃO
    # ======================================================================
    original = ler_imagem(ENTRADA)
    alt, larg = original.shape[:2]
    print(f"\nPASSO 1 — AQUISIÇÃO")
    print(f"    imagem .....................: {ENTRADA.name}")
    print(f"    dimensões ..................: {larg}x{alt}x3 = {larg*alt*3:,} bytes brutos")
    relatorio["entrada"] = {"arquivo": ENTRADA.name, "largura": larg, "altura": alt}

    # ======================================================================
    # PASSO 2 - PRÉ-PROCESSAMENTO
    # ======================================================================
    print(f"\nPASSO 2 — PRÉ-PROCESSAMENTO (adequar a imagem à entrada da rede)")
    entrada_rede, escala, (dx, dy) = letterbox(original, TAMANHO_REDE)
    tensor = torch.from_numpy(
        cv2.cvtColor(entrada_rede, cv2.COLOR_BGR2RGB)
        .transpose(2, 0, 1)[None]).float() / 255.0
    print(f"    letterbox ..................: {larg}x{alt} -> {TAMANHO_REDE}x{TAMANHO_REDE} "
          f"(escala {escala:.3f}, borda dx={dx} dy={dy})")
    print(f"    BGR -> RGB, HWC -> NCHW ....: tensor {tuple(tensor.shape)}")
    print(f"    normalização ...............: uint8 [0,255] -> float32 [0,1] "
          f"(mín {tensor.min():.2f}, máx {tensor.max():.2f})")
    salvar_imagem(SAIDA / "passo2_entrada_rede.png", entrada_rede)
    relatorio["preprocessamento"] = {"tensor": list(tensor.shape),
                                     "escala": round(float(escala), 4),
                                     "borda": [dx, dy]}

    # ======================================================================
    # PASSOS 3 e 5 - PROCESSAMENTO E EXTRAÇÃO DE CARACTERÍSTICAS
    # ======================================================================
    modelo = YOLO(str(PESOS))
    rede = modelo.model
    n_parametros = sum(p.numel() for p in rede.parameters())
    print(f"\nPASSOS 3 e 5 — PROCESSAMENTO / EXTRAÇÃO DE CARACTERÍSTICAS")
    print(f"    arquitetura ................: YOLOv8n, {len(rede.model)} blocos")
    print(f"    parâmetros treinados .......: {n_parametros:,}")
    print(f"    classes reconhecíveis ......: {len(modelo.names)} (conjunto COCO)")

    # ganchos para capturar os mapas de características de camadas iniciais
    ativacoes = {}

    def gancho(nome):
        def fn(_mod, _ent, saida):
            ativacoes[nome] = saida.detach()
        return fn

    camadas_observadas = [0, 2, 4, 6]
    ganchos = [rede.model[i].register_forward_hook(gancho(f"bloco_{i}"))
               for i in camadas_observadas]

    t0 = time.perf_counter()
    with torch.no_grad():
        rede(tensor)
    t_rede = (time.perf_counter() - t0) * 1000
    for h in ganchos:
        h.remove()

    print(f"    passagem direta (CPU) ......: {t_rede:.0f} ms")
    print("    mapas de características produzidos automaticamente pela rede:")
    for nome in sorted(ativacoes):
        f = ativacoes[nome]
        print(f"      {nome:<10s} {tuple(f.shape)}   "
              f"({f.shape[1]} filtros de {f.shape[2]}x{f.shape[3]})")
    relatorio["rede"] = {"parametros": int(n_parametros),
                         "n_classes": len(modelo.names),
                         "tempo_forward_ms": round(t_rede, 1),
                         "mapas": {k: list(v.shape) for k, v in ativacoes.items()}}

    # visualiza os primeiros filtros de cada bloco observado
    fig, eixos = plt.subplots(len(camadas_observadas), 6,
                              figsize=(15, 2.6 * len(camadas_observadas)),
                              constrained_layout=True)
    for linha, i in enumerate(camadas_observadas):
        f = ativacoes[f"bloco_{i}"][0]
        # escolhe os 6 canais de maior energia (mais informativos visualmente)
        energia = f.flatten(1).abs().mean(1)
        canais = torch.argsort(energia, descending=True)[:6]
        for coluna, canal in enumerate(canais):
            mapa = f[canal].cpu().numpy()
            eixos[linha, coluna].imshow(mapa, cmap="inferno")
            eixos[linha, coluna].axis("off")
            if coluna == 0:
                eixos[linha, coluna].set_ylabel(f"bloco {i}")
        eixos[linha, 0].set_title(
            f"bloco {i} — {f.shape[0]} filtros de {f.shape[1]}x{f.shape[2]}",
            loc="left", fontsize=11)
    fig.suptitle("PASSO 5 — Extração de características: mapas aprendidos pela rede\n"
                 "(bordas e texturas nas camadas rasas; padrões semânticos nas profundas)",
                 fontsize=14, fontweight="bold")
    fig.savefig(SAIDA / "passo5_mapas_caracteristicas.png", dpi=105)
    plt.close(fig)

    # ======================================================================
    # PASSOS 4 e 6 - ANÁLISE E RECONHECIMENTO
    # ======================================================================
    print(f"\nPASSOS 4 e 6 — ANÁLISE DE IMAGEM / RECONHECIMENTO DE PADRÕES")
    t0 = time.perf_counter()
    resultado = modelo.predict(original, imgsz=TAMANHO_REDE, conf=0.25,
                               iou=0.45, verbose=False)[0]
    t_total = (time.perf_counter() - t0) * 1000
    print(f"    inferência completa (com NMS): {t_total:.0f} ms")
    print(f"    supressão de não-máximos ....: IoU 0.45, confiança mínima 0.25")

    deteccoes = []
    for caixa in resultado.boxes:
        x1, y1, x2, y2 = [float(v) for v in caixa.xyxy[0].tolist()]
        deteccoes.append({
            "classe": modelo.names[int(caixa.cls)],
            "id_classe": int(caixa.cls),
            "confianca": round(float(caixa.conf), 4),
            "caixa_xyxy": [round(v, 1) for v in (x1, y1, x2, y2)],
            "largura_px": round(x2 - x1, 1),
            "altura_px": round(y2 - y1, 1),
            "area_px": round((x2 - x1) * (y2 - y1), 1),
        })
    deteccoes.sort(key=lambda d: -d["confianca"])

    print(f"\n    SAÍDA DA ÁREA — descrição simbólica da cena ({len(deteccoes)} objetos):")
    print(f"    {'#':<3}{'classe':<12}{'confiança':>10}   {'caixa (x1,y1,x2,y2)':<30}{'área px':>10}")
    print("    " + "-" * 67)
    for i, d in enumerate(deteccoes, 1):
        cx = ",".join(f"{v:.0f}" for v in d["caixa_xyxy"])
        print(f"    {i:<3}{d['classe']:<12}{d['confianca']:>10.3f}   {cx:<30}{d['area_px']:>10,.0f}")

    contagem = {}
    for d in deteccoes:
        contagem[d["classe"]] = contagem.get(d["classe"], 0) + 1
    print(f"\n    Interpretação da cena: " +
          ", ".join(f"{n}x {c}" for c, n in sorted(contagem.items())))
    relatorio["deteccoes"] = deteccoes
    relatorio["contagem_por_classe"] = contagem
    relatorio["tempo_inferencia_ms"] = round(t_total, 1)

    anotada = resultado.plot(line_width=2, font_size=12)
    salvar_imagem(SAIDA / "passo6_deteccoes_yolo.png", anotada)

    # ======================================================================
    # CONTRASTE: características projetadas à mão (HOG + SVM, 2005)
    # ======================================================================
    print(f"\nCONTRASTE — abordagem clássica: HOG + SVM (Dalal & Triggs, 2005)")
    print(f"    descritor de características ESCRITO À MÃO, não aprendido")
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    t0 = time.perf_counter()
    caixas_hog, pesos_hog = hog.detectMultiScale(original, winStride=(8, 8),
                                                 padding=(16, 16), scale=1.05)
    t_hog = (time.perf_counter() - t0) * 1000
    print(f"    tempo ......................: {t_hog:.0f} ms")
    print(f"    pessoas detectadas .........: {len(caixas_hog)} "
          f"(o HOG só sabe procurar UMA classe: pedestres)")
    pessoas_yolo = contagem.get("person", 0)
    print(f"    YOLO, na mesma imagem ......: {pessoas_yolo} pessoas + "
          f"{len(deteccoes)-pessoas_yolo} objetos de outras classes")

    anotada_hog = original.copy()
    for (x, y, w, h), p in zip(caixas_hog, pesos_hog.ravel() if len(caixas_hog) else []):
        cv2.rectangle(anotada_hog, (x, y), (x + w, y + h), (255, 200, 0), 3)
        cv2.putText(anotada_hog, f"person {float(p):.2f}", (x, max(y - 8, 14)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
    salvar_imagem(SAIDA / "contraste_hog.png", anotada_hog)
    relatorio["hog_classico"] = {"n_pessoas": int(len(caixas_hog)),
                                 "tempo_ms": round(t_hog, 1)}

    # painel comparativo final
    fig, eixos = plt.subplots(1, 3, figsize=(16, 6.2), constrained_layout=True)
    for ax, (img, titulo) in zip(eixos, [
            (original, f"PASSO 1 — Aquisição\n{larg}x{alt} pixels"),
            (anotada_hog, f"Clássico: HOG + SVM\n{len(caixas_hog)} pessoa(s), 1 classe"),
            (anotada, f"YOLOv8n: {len(deteccoes)} objetos\n" +
                      ", ".join(f"{n}x {c}" for c, n in sorted(contagem.items())))]):
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.set_title(titulo, fontsize=12)
        ax.axis("off")
    fig.suptitle("ÁREA 3 — Visão Computacional: da imagem para a descrição da cena",
                 fontsize=15, fontweight="bold")
    fig.savefig(SAIDA / "comparativo_visao.png", dpi=110)
    plt.close(fig)

    print("\n" + "-" * 74)
    print("BALANÇO DA ÁREA (entrada -> saída)")
    print("-" * 74)
    print(f"  ENTRADA : imagem MATRICIAL {larg}x{alt}x3 = {larg*alt*3:,} bytes")
    saida_json = json.dumps(deteccoes)
    print(f"  SAÍDA   : DESCRIÇÃO SIMBÓLICA — {len(deteccoes)} registros, "
          f"{len(saida_json)} bytes de JSON")
    print(f"  Redução de {larg*alt*3/len(saida_json):,.0f}x no volume de dados: a área")
    print("  troca pixels por SIGNIFICADO. A imagem anotada é só para o humano ver;")
    print("  o produto real da Visão Computacional é a lista de objetos acima.")

    (SAIDA / "relatorio.json").write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nArquivos gerados em: {SAIDA}")


if __name__ == "__main__":
    main()
