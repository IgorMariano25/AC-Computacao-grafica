# -*- coding: utf-8 -*-
"""
AP1 - Geracao das capturas exigidas nos entregaveis.

Roda depois de AP1_IgorMariano.py, no mesmo arquivo .blend, e gera:

  01_enquadramento_principal.png   entregavel 2 (enquadramento principal)
  02_objeto_farol.png              entregavel 3
  03_objeto_jangada.png            entregavel 3
  04_objeto_planetario.png         entregavel 3
  05_palavra_ibmec.png             entregavel 3
  06_storyboard_1_amanhecer.png    entregavel 4
  07_storyboard_2_construcao.png   entregavel 4
  08_storyboard_3_assinatura.png   entregavel 4

Usa o motor Workbench (o mesmo do Solid Mode do viewport), com as cores de
material dos objetos. Cada imagem sai em menos de um segundo - nenhuma
renderizacao demorada, como combinado para o escopo da AP1.

Como usar:
  1. Abra o .blend ja montado pelo AP1_IgorMariano.py.
  2. Aba Scripting > Open > AP1_capturas.py > Run Script.
  3. As imagens vao para a pasta indicada em PASTA_SAIDA.
"""

import math
import os
import bpy
from mathutils import Vector

# Deixe "" para salvar em <pasta do .blend>/saida. Se o arquivo ainda nao
# foi salvo, o script usa o caminho abaixo.
PASTA_SAIDA = ""
PASTA_PADRAO = "E:\\AC-Computação-Gráfica\\AP1\\saida"

LARGURA = 1920
ALTURA = 1080
LENTE_DETALHE = 50.0       # lente das capturas de objeto
FOLGA = 1.30               # margem em volta do objeto enquadrado


# ===================================================================
# utilidades
# ===================================================================

def pasta_de_saida():
    if PASTA_SAIDA:
        destino = PASTA_SAIDA
    elif bpy.data.filepath:
        destino = os.path.join(os.path.dirname(bpy.data.filepath), "saida")
    else:
        destino = PASTA_PADRAO
    os.makedirs(destino, exist_ok=True)
    return destino


def apontar_para(obj, alvo):
    direcao = Vector(alvo) - obj.location
    obj.rotation_euler = direcao.to_track_quat("-Z", "Y").to_euler()


def configurar_workbench(cena):
    """Deixa o render igual ao Solid Mode com cores de material."""
    cena.render.engine = "BLENDER_WORKBENCH"
    cena.render.resolution_x = LARGURA
    cena.render.resolution_y = ALTURA
    cena.render.resolution_percentage = 100
    cena.render.image_settings.file_format = "PNG"
    cena.render.film_transparent = False

    sombreamento = cena.display.shading
    sombreamento.light = "STUDIO"
    sombreamento.color_type = "MATERIAL"
    sombreamento.show_shadows = True
    sombreamento.show_cavity = True
    sombreamento.cavity_type = "BOTH"
    sombreamento.show_object_outline = False
    cena.display.render_aa = "8"


def caixa_de(objetos, grafo):
    """Bounding box em coordenadas de mundo, ja com os modificadores aplicados."""
    cantos = []
    for obj in objetos:
        avaliado = obj.evaluated_get(grafo)
        for canto in avaliado.bound_box:
            cantos.append(avaliado.matrix_world @ Vector(canto))
    minimo = Vector((min(c.x for c in cantos), min(c.y for c in cantos),
                     min(c.z for c in cantos)))
    maximo = Vector((max(c.x for c in cantos), max(c.y for c in cantos),
                     max(c.z for c in cantos)))
    return minimo, maximo


def familia(obj):
    """O objeto e todos os seus filhos (usado para enquadrar o conjunto)."""
    grupo = [obj]
    for filho in obj.children_recursive:
        grupo.append(filho)
    return grupo


def renderizar(cena, camera, caminho):
    anterior = cena.camera
    cena.camera = camera
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)
    cena.camera = anterior
    print("[AP1] gerado:", caminho)


def camera_de_detalhe(cena, objetos, direcao):
    """Cria uma camera temporaria que enquadra o conjunto informado."""
    grafo = bpy.context.evaluated_depsgraph_get()
    minimo, maximo = caixa_de(objetos, grafo)
    centro = (minimo + maximo) * 0.5
    raio = (maximo - minimo).length * 0.5

    dados = bpy.data.cameras.new("CAM_TMP_Detalhe")
    dados.lens = LENTE_DETALHE
    dados.clip_end = 900.0
    camera = bpy.data.objects.new("CAM_TMP_Detalhe", dados)
    cena.collection.objects.link(camera)

    meia_abertura = math.atan((cena.render.resolution_y / cena.render.resolution_x)
                              * 18.0 / dados.lens)
    distancia = (raio / math.tan(meia_abertura)) * FOLGA
    camera.location = centro + Vector(direcao).normalized() * distancia
    apontar_para(camera, centro)
    bpy.context.view_layer.update()
    return camera


def descartar(camera):
    dados = camera.data
    bpy.data.objects.remove(camera, do_unlink=True)
    if dados.users == 0:
        bpy.data.cameras.remove(dados)


# ===================================================================
# execucao
# ===================================================================

def main():
    cena = bpy.context.scene
    destino = pasta_de_saida()

    motor_anterior = cena.render.engine
    saida_anterior = cena.render.filepath
    camera_anterior = cena.camera
    frame_anterior = cena.frame_current

    configurar_workbench(cena)
    cena.frame_set(300)

    def pegar(nome):
        obj = bpy.data.objects.get(nome)
        if obj is None:
            print("[AP1] AVISO: objeto '%s' nao encontrado - rode antes o "
                  "AP1_IgorMariano.py." % nome)
        return obj

    # ---- 1. enquadramento principal --------------------------------
    principal = pegar("CAM_Principal")
    if principal:
        renderizar(cena, principal,
                   os.path.join(destino, "01_enquadramento_principal.png"))

    # ---- 2 a 5. objetos autorais e a palavra -----------------------
    detalhes = [
        ("OBJ_Farol_Mucuripe", "02_objeto_farol.png", (-0.85, -1.00, 0.34)),
        ("OBJ_Jangada_Mucuripe", "03_objeto_jangada.png", (-0.55, -1.00, 0.30)),
        ("OBJ_Planetario_Dragao_do_Mar", "04_objeto_planetario.png",
         (0.70, -1.00, 0.38)),
        ("LOGO_Palavra_Ibmec", "05_palavra_ibmec.png", (-0.22, -1.00, 0.16)),
    ]
    for nome, arquivo, direcao in detalhes:
        alvo = pegar(nome)
        if alvo is None:
            continue
        camera = camera_de_detalhe(cena, familia(alvo), direcao)
        renderizar(cena, camera, os.path.join(destino, arquivo))
        descartar(camera)

    # ---- 6 a 8. quadros do storyboard ------------------------------
    quadros = [
        ("CAM_SB1_Amanhecer", "06_storyboard_1_amanhecer.png", 1),
        ("CAM_SB2_Construcao", "07_storyboard_2_construcao.png", 121),
        ("CAM_SB3_Assinatura", "08_storyboard_3_assinatura.png", 241),
    ]
    for nome, arquivo, frame in quadros:
        camera = pegar(nome)
        if camera is None:
            continue
        cena.frame_set(frame)
        renderizar(cena, camera, os.path.join(destino, arquivo))

    # ---- restaura o estado do arquivo ------------------------------
    cena.render.engine = motor_anterior
    cena.render.filepath = saida_anterior
    cena.camera = camera_anterior
    cena.frame_set(frame_anterior)

    print("")
    print("[AP1] Capturas concluidas em:", destino)


main()
