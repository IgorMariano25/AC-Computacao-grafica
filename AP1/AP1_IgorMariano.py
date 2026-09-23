# -*- coding: utf-8 -*-
"""
AP1 - Conceito e Modelagem da peca "Ibmec em 15 segundos"
Peca: "Do Mucuripe ao Futuro" - Ibmec Fortaleza

Cena-conceito construida integralmente por script no Blender 4.5 LTS.

O que este script monta:
  - colecao principal AP1_Ibmec_Conceito com 4 subcolecoes organizadas;
  - a palavra "ibmec" com as cores oficiais (azul #002555 / amarelo #F5AC00),
    cada letra como objeto independente e o ponto do "i" separado - ele e o
    "sol do Mucuripe" que fecha o logo na AP2;
  - os TRES objetos autorais, todos modelados do zero:
        OBJ_Farol_Mucuripe            (superficie de revolucao + bevel)
        OBJ_Jangada_Mucuripe          (composicao de malhas + solidify/simple deform)
        OBJ_Planetario_Dragao_do_Mar  (revolucao + inset/extrude + curva de Bezier)
  - o cenario de Fortaleza (mar, faixa de areia com dunas, deck-mirante,
    escadaria com Array, coqueiros, rochedo);
  - camera principal com alvo (Track To), 3 cameras de storyboard e
    marcadores de timeline;
  - timeline de 15 s a 24 fps = 360 frames.

Como usar:
  1. Abra o Blender 4.5 LTS (arquivo novo ou o .blend do logo).
  2. Aba Scripting > Open > selecione este arquivo.
  3. Run Script (Alt+P).
  4. No Windows, veja as mensagens em Window > Toggle System Console.

O script e idempotente: rodar de novo apaga e reconstroi a colecao AP1,
sem duplicar objetos (nada de ".001").
"""

import math
import bpy
import bmesh
from mathutils import Matrix, Vector

# ===================================================================
# 0. CONFIGURACAO
# ===================================================================

COLECAO_RAIZ = "AP1_Ibmec_Conceito"

# --- duracao planejada da peca -------------------------------------
FPS = 24
DURACAO_SEGUNDOS = 15
FRAME_INICIAL = 1
FRAME_FINAL = FRAME_INICIAL + FPS * DURACAO_SEGUNDOS - 1   # 360 frames

# --- palavra -------------------------------------------------------
TEXTO_LOGO = "ibmec"          # marca em caixa baixa, como na identidade visual
LARGURA_PALAVRA = 8.2         # largura final em metros (escala intencional)
ALTURA_BASE_PALAVRA = 1.22    # altura do piso do deck-mirante
TAMANHO_FONTE = 3.0
PROFUNDIDADE_LETRA = 0.24     # extrusao do texto
CHANFRO_LETRA = 0.03          # bevel das letras
ESPACO_LETRAS = 0.16

# Fonte da marca. Deixe "" para o script procurar uma fonte adequada no
# sistema, ou aponte para o .ttf oficial da identidade visual do Ibmec.
CAMINHO_FONTE = ""
FONTES_CANDIDATAS = [
    "C:/Windows/Fonts/Montserrat-Bold.ttf",
    "C:/Windows/Fonts/Poppins-Bold.ttf",
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/verdanab.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]

# Opcional: caminho do SVG oficial com as letras separadas. Se preenchido,
# o script importa as curvas reais da marca no lugar do texto.
# Ex.: r"C:\Users\igor-\Downloads\Ibmec-letras-separadas.svg"
CAMINHO_SVG_LOGO = ""

# --- cores lidas do arquivo AP1-Logo-Ibmec-3D.blend ----------------
HEX_AZUL_IBMEC = "002555"
HEX_AMARELO_IBMEC = "F5AC00"

SALVAR_BLEND = False
CAMINHO_BLEND = r"E:\AC-Computação-Gráfica\AP1\AP1_IgorMariano.blend"

# --- geografia da cena ---------------------------------------------
LINHA_DA_COSTA = 12.0         # acima desse y a cena e mar


# ===================================================================
# 1. UTILIDADES
# ===================================================================

def hex_para_linear(hexa):
    """Converte uma cor sRGB hexadecimal para o espaco linear do Blender."""
    hexa = hexa.lstrip("#")
    canais = [int(hexa[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
              for c in canais]
    return (linear[0], linear[1], linear[2], 1.0)


def sincronizar_cor_de_viewport(mat):
    """Copia a cor do Principled para a cor de viewport, se ela for o cinza padrao.

    Materiais herdados do arquivo do logo costumam ter a cor de viewport
    intocada; sem isso o Solid Mode e o render Workbench mostrariam cinza
    no lugar do azul e do amarelo da marca.
    """
    e_cinza_padrao = all(abs(mat.diffuse_color[i] - 0.8) < 1e-3 for i in range(3))
    if not e_cinza_padrao or not mat.use_nodes:
        return
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled is None:
        return
    cor = principled.inputs["Base Color"].default_value
    mat.diffuse_color = (cor[0], cor[1], cor[2], 1.0)


def obter_material(nome, hexa, rugosidade=0.55, metalico=0.0, apelidos=()):
    """Reaproveita um material existente no arquivo ou cria um novo.

    'apelidos' faz o script herdar os materiais oficiais que ja estejam no
    .blend (por exemplo "Azul Ibmec" e "Amarelo Ibmec"), preservando as
    cores originais da marca.
    """
    for candidato in (nome,) + tuple(apelidos):
        if candidato in bpy.data.materials:
            existente = bpy.data.materials[candidato]
            sincronizar_cor_de_viewport(existente)
            return existente

    mat = bpy.data.materials.new(nome)
    mat.use_nodes = True
    cor = hex_para_linear(hexa)
    principled = mat.node_tree.nodes.get("Principled BSDF")
    if principled:
        principled.inputs["Base Color"].default_value = cor
        principled.inputs["Roughness"].default_value = rugosidade
        if "Metallic" in principled.inputs:
            principled.inputs["Metallic"].default_value = metalico
    # cor de viewport: e o que aparece no Solid Mode e no render Workbench
    mat.diffuse_color = cor
    mat.roughness = rugosidade
    mat.metallic = metalico
    return mat


def nova_colecao(nome, pai):
    colecao = bpy.data.collections.new(nome)
    pai.children.link(colecao)
    return colecao


def novo_objeto_malha(nome, colecao, materiais=()):
    malha = bpy.data.meshes.new("ME_" + nome)
    obj = bpy.data.objects.new(nome, malha)
    for mat in materiais:
        malha.materials.append(mat)
    colecao.objects.link(obj)
    return obj


def gravar_bmesh(bm, obj, suavizar=False):
    """Recalcula normais, grava o bmesh na malha do objeto e libera a memoria."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data)
    bm.free()
    if suavizar:
        for poligono in obj.data.polygons:
            poligono.use_smooth = True
    obj.data.update()


def criar_cone(bm, raio1, raio2, profundidade, segmentos=24, matriz=None, tampas=True):
    """Wrapper de bmesh.ops.create_cone tolerante a variacao de nomes da API."""
    argumentos = dict(cap_ends=tampas, cap_tris=False, segments=segmentos,
                      depth=profundidade, matrix=matriz or Matrix.Identity(4))
    try:
        return bmesh.ops.create_cone(bm, radius1=raio1, radius2=raio2, **argumentos)
    except TypeError:
        return bmesh.ops.create_cone(bm, diameter1=raio1 * 2.0,
                                     diameter2=raio2 * 2.0, **argumentos)


def superficie_de_revolucao(bm, perfil, segmentos=32):
    """Gira um perfil 2D [(raio, altura), ...] em torno do eixo Z.

    Tecnica de modelagem: superficie de revolucao (spin), o mesmo principio
    do torno. Usada no farol, na cupula do planetario e nos troncos.
    """
    antes = set(bm.verts)
    vertices = [bm.verts.new((r, 0.0, z)) for r, z in perfil]
    arestas = [bm.edges.new((vertices[i], vertices[i + 1]))
               for i in range(len(vertices) - 1)]

    bmesh.ops.spin(bm, geom=arestas, cent=(0.0, 0.0, 0.0), axis=(0.0, 0.0, 1.0),
                   dvec=(0.0, 0.0, 0.0), angle=math.radians(360.0),
                   steps=segmentos, use_duplicate=False)

    novos = [v for v in bm.verts if v not in antes]
    bmesh.ops.remove_doubles(bm, verts=novos, dist=1e-4)
    bm.faces.ensure_lookup_table()
    return novos


def extrudar_face(bm, face, vetor):
    """Extrusao de uma face seguida de translacao. Devolve a face do topo."""
    resultado = bmesh.ops.extrude_face_region(bm, geom=[face])
    novos_verts = [e for e in resultado["geom"] if isinstance(e, bmesh.types.BMVert)]
    novas_faces = [e for e in resultado["geom"] if isinstance(e, bmesh.types.BMFace)]
    bmesh.ops.translate(bm, verts=novos_verts, vec=vetor)
    bmesh.ops.delete(bm, geom=[face], context="FACES")
    return novas_faces[0] if novas_faces else None


def face_mais_alta(bm):
    bm.faces.ensure_lookup_table()
    return max(bm.faces, key=lambda f: f.calc_center_median().z)


def marcar_material(faces, indice):
    for face in faces:
        face.material_index = indice


def grupos_de_faces(bm):
    """Separa a malha em ilhas conectadas (usado para isolar o ponto do 'i')."""
    visitadas = set()
    grupos = []
    for semente in bm.faces:
        if semente in visitadas:
            continue
        pilha = [semente]
        visitadas.add(semente)
        grupo = []
        while pilha:
            atual = pilha.pop()
            grupo.append(atual)
            for aresta in atual.edges:
                for vizinha in aresta.link_faces:
                    if vizinha not in visitadas:
                        visitadas.add(vizinha)
                        pilha.append(vizinha)
        grupos.append(grupo)
    return grupos


def apontar_para(obj, alvo):
    """Orienta um objeto (camera) para um ponto do espaco."""
    direcao = Vector(alvo) - obj.location
    obj.rotation_euler = direcao.to_track_quat("-Z", "Y").to_euler()


# ===================================================================
# 2. LIMPEZA / RECONSTRUCAO
# ===================================================================

def limpar_cena():
    """Remove a colecao AP1 anterior (objetos + subcolecoes) e o cubo padrao."""
    raiz = bpy.data.collections.get(COLECAO_RAIZ)
    if raiz:
        def apagar(colecao):
            for filha in list(colecao.children):
                apagar(filha)
            for obj in list(colecao.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(colecao)
        apagar(raiz)

    cubo = bpy.data.objects.get("Cube")
    if cubo is not None and cubo.type == "MESH":
        bpy.data.objects.remove(cubo, do_unlink=True)

    # purga dados orfaos para o arquivo nao crescer a cada execucao
    for banco in (bpy.data.meshes, bpy.data.curves, bpy.data.cameras,
                  bpy.data.lights):
        for dado in list(banco):
            if dado.users == 0:
                banco.remove(dado)


# ===================================================================
# 3. PALAVRA IBMEC
# ===================================================================

def carregar_fonte():
    import os
    caminhos = ([CAMINHO_FONTE] if CAMINHO_FONTE else []) + FONTES_CANDIDATAS
    for caminho in caminhos:
        if caminho and os.path.isfile(caminho):
            try:
                return bpy.data.fonts.load(caminho, check_existing=True)
            except RuntimeError:
                continue
    print("[AP1] Fonte especifica nao encontrada; usando a fonte padrao do Blender.")
    return None


def texto_para_malha(texto, nome, colecao, fonte):
    """Cria um objeto de texto 3D e o converte em malha (sem usar operadores).

    Tecnicas: curva de texto -> extrusao + bevel -> tesselacao em malha.
    """
    curva = bpy.data.curves.new("CU_" + nome, type="FONT")
    curva.body = texto
    if fonte is not None:
        curva.font = fonte
    curva.size = TAMANHO_FONTE
    curva.extrude = PROFUNDIDADE_LETRA
    curva.bevel_depth = CHANFRO_LETRA
    curva.bevel_resolution = 2
    curva.resolution_u = 4
    curva.align_x = "LEFT"
    curva.align_y = "BOTTOM_BASELINE"

    temporario = bpy.data.objects.new("TMP_" + nome, curva)
    colecao.objects.link(temporario)
    bpy.context.view_layer.update()

    grafo = bpy.context.evaluated_depsgraph_get()
    malha = bpy.data.meshes.new_from_object(temporario.evaluated_get(grafo))
    malha.name = "ME_" + nome

    bpy.data.objects.remove(temporario, do_unlink=True)
    if curva.users == 0:
        bpy.data.curves.remove(curva)

    malha.materials.clear()
    obj = bpy.data.objects.new(nome, malha)
    colecao.objects.link(obj)
    return obj


def normalizar_letra(obj):
    """Encosta a letra em x = 0 e devolve a sua largura."""
    coords = [v.co for v in obj.data.vertices]
    if not coords:
        return 0.0
    minimo_x = min(c.x for c in coords)
    maximo_x = max(c.x for c in coords)
    for vertice in obj.data.vertices:
        vertice.co.x -= minimo_x
    obj.data.update()
    return maximo_x - minimo_x


def separar_ponto(obj, nome_novo, colecao, material):
    """Destaca a ilha mais alta da letra 'i' como objeto proprio (o pingo).

    O pingo vira o "sol do Mucuripe": na AP2 ele entra na cena como o sol
    nascendo sobre o mar e se encaixa sobre a letra.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    grupos = grupos_de_faces(bm)
    if len(grupos) < 2:
        bm.free()
        return None

    def altura_media(grupo):
        return sum(f.calc_center_median().y for f in grupo) / len(grupo)

    grupos.sort(key=altura_media)
    topo = grupos[-1]

    bm_ponto = bmesh.new()
    mapa = {}
    for face in topo:
        novos = []
        for vertice in face.verts:
            if vertice not in mapa:
                mapa[vertice] = bm_ponto.verts.new(vertice.co.copy())
            novos.append(mapa[vertice])
        try:
            bm_ponto.faces.new(novos)
        except ValueError:
            pass

    centro = Vector((0.0, 0.0, 0.0))
    for vertice in bm_ponto.verts:
        centro += vertice.co
    centro /= max(1, len(bm_ponto.verts))
    bmesh.ops.translate(bm_ponto, verts=list(bm_ponto.verts), vec=-centro)

    ponto = novo_objeto_malha(nome_novo, colecao, (material,))
    gravar_bmesh(bm_ponto, ponto)

    bmesh.ops.delete(bm, geom=topo, context="FACES")
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()
    return ponto, centro


def importar_svg_do_logo(colecao):
    """Importa as curvas oficiais da marca, se o SVG foi informado."""
    import os
    if not CAMINHO_SVG_LOGO or not os.path.isfile(CAMINHO_SVG_LOGO):
        return []

    antes = set(bpy.data.objects)
    try:
        bpy.ops.import_curve.svg(filepath=CAMINHO_SVG_LOGO)
    except Exception:
        try:
            bpy.ops.wm.svg_import(filepath=CAMINHO_SVG_LOGO)
        except Exception as erro:
            print("[AP1] Nao foi possivel importar o SVG:", erro)
            return []

    novos = [o for o in bpy.data.objects if o not in antes and o.type == "CURVE"]
    for obj in novos:
        for atual in list(obj.users_collection):
            atual.objects.unlink(obj)
        colecao.objects.link(obj)
        obj.data.extrude = PROFUNDIDADE_LETRA / 100.0
        obj.data.bevel_depth = CHANFRO_LETRA / 100.0
        obj.data.dimensions = "2D"
    # a colecao vazia criada pelo importador do SVG e descartada
    for colecao_svg in list(bpy.data.collections):
        if colecao_svg.name.lower().endswith(".svg") and not colecao_svg.objects:
            bpy.data.collections.remove(colecao_svg)
    print("[AP1] SVG importado:", len(novos), "curvas.")
    return novos


def construir_palavra(colecao, mat_azul, mat_amarelo):
    """Monta a palavra letra a letra sob um pivo unico.

    Hierarquia: LOGO_Palavra_Ibmec (empty) -> LOGO_Letra_* + LOGO_Ponto_i.
    O pivo concentra as transformacoes da palavra inteira (rotacao de 90 graus
    em X para as letras ficarem em pe de frente para a camera, translacao ate
    o topo do deck e escala ate a largura alvo), enquanto cada letra mantem a
    sua propria translacao local - pronto para a animacao de entrada da AP2.
    """
    pivo = bpy.data.objects.new("LOGO_Palavra_Ibmec", None)
    pivo.empty_display_type = "PLAIN_AXES"
    pivo.empty_display_size = 0.9
    colecao.objects.link(pivo)

    curvas_svg = importar_svg_do_logo(colecao)
    if curvas_svg:
        letras = _palavra_por_svg(curvas_svg, colecao, mat_azul, mat_amarelo)
    else:
        letras = _palavra_por_texto(colecao, mat_azul, mat_amarelo)

    # --- transformacoes do pivo -------------------------------------
    largura = centralizar_conjunto(letras)
    escala = LARGURA_PALAVRA / max(largura, 1e-6)

    pivo.location = (0.0, 0.0, ALTURA_BASE_PALAVRA)
    pivo.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    pivo.scale = (escala, escala, escala)

    for obj in letras:
        obj.parent = pivo          # parent_inverse = identidade:
                                   # a posicao da letra e lida no espaco do pivo

    print("[AP1] Palavra: largura bruta %.2f -> escala %.3f -> %.2f m."
          % (largura, escala, LARGURA_PALAVRA))
    return pivo, letras


def centralizar_conjunto(objetos):
    """Centraliza as letras em X e apoia a linha de base em Y = 0.

    Devolve a largura bruta do conjunto, usada para calcular a escala do pivo.
    """
    bpy.context.view_layer.update()
    cantos = []
    for obj in objetos:
        for canto in obj.bound_box:
            cantos.append(obj.matrix_world @ Vector(canto))
    if not cantos:
        return 1.0

    minimo_x = min(c.x for c in cantos)
    maximo_x = max(c.x for c in cantos)
    minimo_y = min(c.y for c in cantos)
    centro_x = (minimo_x + maximo_x) / 2.0

    for obj in objetos:
        obj.location.x -= centro_x
        obj.location.y -= minimo_y
    return maximo_x - minimo_x


def _palavra_por_texto(colecao, mat_azul, mat_amarelo):
    fonte = carregar_fonte()
    letras = []
    cursor = 0.0
    ponto_info = None

    for indice, caractere in enumerate(TEXTO_LOGO):
        nome = "LOGO_Letra_%02d_%s" % (indice + 1, caractere)
        letra = texto_para_malha(caractere, nome, colecao, fonte)
        letra.data.materials.append(mat_azul)
        largura = normalizar_letra(letra)

        if caractere == "i":
            resultado = separar_ponto(letra, "LOGO_Ponto_i", colecao, mat_amarelo)
            if resultado:
                ponto_info = (resultado[0], resultado[1], cursor)

        letra.location = (cursor, 0.0, 0.0)
        cursor += largura + ESPACO_LETRAS * TAMANHO_FONTE
        letras.append(letra)

    if ponto_info:
        ponto, centro, base_x = ponto_info
        ponto.location = (base_x + centro.x, centro.y, centro.z)
        letras.append(ponto)

    print("[AP1] Palavra construida a partir de texto 3D (%d objetos)." % len(letras))
    return letras


def _palavra_por_svg(curvas, colecao, mat_azul, mat_amarelo):
    """Renomeia, ordena e colore as curvas vindas do SVG oficial."""
    bpy.context.view_layer.update()
    ordenadas = sorted(curvas, key=lambda o: o.matrix_world.translation.x)

    alturas = [o.matrix_world.translation.z for o in ordenadas]
    indice_ponto = alturas.index(max(alturas))

    letras = []
    contador = 0
    for indice, obj in enumerate(ordenadas):
        if indice == indice_ponto:
            obj.name = "LOGO_Ponto_i"
            obj.data.materials.clear()
            obj.data.materials.append(mat_amarelo)
        else:
            contador += 1
            sufixo = TEXTO_LOGO[contador - 1] if contador <= len(TEXTO_LOGO) else "x"
            obj.name = "LOGO_Letra_%02d_%s" % (contador, sufixo)
            obj.data.materials.clear()
            obj.data.materials.append(mat_azul)
        letras.append(obj)
    return letras


# ===================================================================
# 4. OBJETOS AUTORAIS (os tres exigidos pelo enunciado)
# ===================================================================

def construir_farol(colecao, mat_concreto, mat_azul, mat_luz):
    """Objeto autoral 1 - Farol do Mucuripe.

    Tecnicas: superficie de revolucao (spin) de um perfil desenhado a mao,
    inset + extrusao para o vao da porta, atribuicao de materiais por faixa
    de altura e modificador Bevel para quebrar as arestas vivas.
    """
    farol = novo_objeto_malha("OBJ_Farol_Mucuripe", colecao,
                              (mat_concreto, mat_azul, mat_luz))
    bm = bmesh.new()

    # torre: base alargada, fuste conico e varanda no topo
    perfil_torre = [
        (0.00, 0.00), (1.62, 0.00), (1.62, 0.42), (1.30, 0.58),
        (1.12, 0.72), (0.98, 2.40), (0.86, 4.30), (0.82, 4.78),
        (1.24, 4.92), (1.24, 5.28), (0.98, 5.42), (0.00, 5.42),
    ]
    superficie_de_revolucao(bm, perfil_torre, segmentos=28)

    # cupula da lanterna (segunda revolucao, no mesmo bmesh)
    perfil_cupula = [
        (0.00, 6.46), (0.94, 6.46), (0.88, 6.64), (0.40, 7.06), (0.00, 7.30),
    ]
    superficie_de_revolucao(bm, perfil_cupula, segmentos=28)

    # porta: inset seguido de extrusao para dentro
    bm.faces.ensure_lookup_table()
    porta = None
    melhor = -1e9
    for face in bm.faces:
        centro = face.calc_center_median()
        if 0.85 < centro.z < 1.70 and centro.x ** 2 + centro.y ** 2 > 0.6:
            pontuacao = -centro.y
            if pontuacao > melhor:
                melhor = pontuacao
                porta = face
    if porta is not None:
        bmesh.ops.inset_region(bm, faces=[porta], thickness=0.16, depth=0.0,
                               use_even_offset=True, use_boundary=True)
        bm.normal_update()
        extrudar_face(bm, porta, porta.normal * -0.20)

    # materiais por faixa de altura: varanda azul Ibmec, cupula amarela
    for face in bm.faces:
        altura = face.calc_center_median().z
        if 4.86 <= altura <= 5.46:
            face.material_index = 1
        elif altura >= 6.44:
            face.material_index = 2

    gravar_bmesh(bm, farol)

    chanfro = farol.modifiers.new("MOD_Bevel_Farol", "BEVEL")
    chanfro.width = 0.018
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # vidro da lanterna: filho do farol, sera a fonte de luz da AP2
    vidro = novo_objeto_malha("Farol_Lanterna_Vidro", colecao, (mat_luz,))
    bm_vidro = bmesh.new()
    criar_cone(bm_vidro, 0.76, 0.76, 1.04, segmentos=20,
               matriz=Matrix.Translation((0.0, 0.0, 5.94)))
    gravar_bmesh(bm_vidro, vidro, suavizar=True)
    vidro.parent = farol

    return farol, vidro


def construir_jangada(colecao, mat_madeira, mat_vela, mat_azul):
    """Objeto autoral 2 - Jangada do Mucuripe.

    Tecnicas: composicao de malhas (cinco troncos gerados em laco), edicao
    proporcional manual dos vertices da proa, cubo com atribuicao de material
    por ilha, modificador Bevel; a vela usa Solidify + Simple Deform (Bend).
    """
    jangada = novo_objeto_malha("OBJ_Jangada_Mucuripe", colecao,
                                (mat_madeira, mat_azul))
    bm = bmesh.new()

    # casco: cinco troncos amarrados lado a lado
    for indice in range(5):
        deslocamento_y = -0.52 + indice * 0.26
        matriz = (Matrix.Translation((0.0, deslocamento_y, 0.16))
                  @ Matrix.Rotation(math.radians(90.0), 4, "Y"))
        criar_cone(bm, 0.135, 0.135, 3.6, segmentos=10, matriz=matriz)

    # proa afinada e levantada / popa levemente fechada
    for vertice in bm.verts:
        x = vertice.co.x
        if x > 1.00:
            t = min(1.0, (x - 1.00) / 0.80)
            vertice.co.y *= (1.0 - 0.72 * t)
            vertice.co.z += 0.44 * t * t
        elif x < -1.20:
            t = min(1.0, (-1.20 - x) / 0.60)
            vertice.co.y *= (1.0 - 0.34 * t)
            vertice.co.z += 0.12 * t * t

    # mastro inclinado
    mastro = (Matrix.Translation((0.18, 0.0, 1.92))
              @ Matrix.Rotation(math.radians(-7.0), 4, "Y"))
    criar_cone(bm, 0.078, 0.052, 3.50, segmentos=10, matriz=mastro)

    # retranca (verga inferior da vela)
    retranca = (Matrix.Translation((0.62, 0.0, 0.56))
                @ Matrix.Rotation(math.radians(9.0), 4, "Z")
                @ Matrix.Rotation(math.radians(90.0), 4, "Y"))
    criar_cone(bm, 0.048, 0.040, 2.55, segmentos=8, matriz=retranca)

    # caixa de pesca em azul Ibmec (marca a paleta tambem nos objetos)
    caixa = bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((-1.05, 0.0, 0.45))
                @ Matrix.Diagonal((0.62, 0.78, 0.34, 1.0))))
    verts_caixa = set(caixa["verts"])
    marcar_material([f for f in bm.faces
                     if all(v in verts_caixa for v in f.verts)], 1)

    gravar_bmesh(bm, jangada)

    chanfro = jangada.modifiers.new("MOD_Bevel_Jangada", "BEVEL")
    chanfro.width = 0.012
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # ---- vela triangular -------------------------------------------
    vela = novo_objeto_malha("Jangada_Vela", colecao, (mat_vela,))
    bm_vela = bmesh.new()
    colunas, linhas = 6, 8
    largura, altura = 2.35, 3.05
    grade = []
    for j in range(linhas + 1):
        v = j / linhas
        largura_linha = largura * (1.0 - 0.94 * v) + 0.06
        linha = []
        for i in range(colunas + 1):
            u = i / colunas
            linha.append(bm_vela.verts.new((-0.10 + largura_linha * u,
                                            0.0, altura * v)))
        grade.append(linha)
    for j in range(linhas):
        for i in range(colunas):
            bm_vela.faces.new((grade[j][i], grade[j][i + 1],
                               grade[j + 1][i + 1], grade[j + 1][i]))
    gravar_bmesh(bm_vela, vela)

    espessura = vela.modifiers.new("MOD_Solidify_Vela", "SOLIDIFY")
    espessura.thickness = 0.025
    espessura.offset = 0.0

    barriga = vela.modifiers.new("MOD_Bend_Vela", "SIMPLE_DEFORM")
    barriga.deform_method = "BEND"
    barriga.deform_axis = "Z"
    barriga.angle = math.radians(36.0)

    vela.parent = jangada
    vela.location = (0.20, 0.0, 0.62)

    return jangada, vela


def construir_planetario(colecao, mat_concreto, mat_azul):
    """Objeto autoral 3 - Planetario do Centro Dragao do Mar.

    Tecnicas: superficie de revolucao para o tambor e a cupula, inset +
    extrusao para o portico de entrada, materiais por ilha e uma curva de
    Bezier com extrude/bevel para a passarela suspensa.
    """
    planetario = novo_objeto_malha("OBJ_Planetario_Dragao_do_Mar", colecao,
                                   (mat_concreto, mat_azul))
    bm = bmesh.new()

    raio = 2.45
    perfil = [(0.00, 0.00), (2.62, 0.00), (2.62, 0.62), (2.52, 0.78)]
    for passo in range(13):
        angulo = math.radians(90.0) * passo / 12.0
        perfil.append((raio * math.cos(angulo), 0.80 + raio * math.sin(angulo)))
    superficie_de_revolucao(bm, perfil, segmentos=36)

    # portico de entrada: inset + extrusao para dentro do tambor
    bm.faces.ensure_lookup_table()
    entrada = None
    melhor = -1e9
    for face in bm.faces:
        centro = face.calc_center_median()
        if 0.10 < centro.z < 0.60 and centro.x ** 2 + centro.y ** 2 > 3.0:
            pontuacao = -centro.y
            if pontuacao > melhor:
                melhor = pontuacao
                entrada = face
    if entrada is not None:
        bmesh.ops.inset_region(bm, faces=[entrada], thickness=0.12, depth=0.0,
                               use_even_offset=True, use_boundary=True)
        bm.normal_update()
        extrudar_face(bm, entrada, entrada.normal * -0.26)

    # tambor em azul Ibmec, cupula em concreto claro
    for face in bm.faces:
        if face.calc_center_median().z <= 0.80:
            face.material_index = 1

    gravar_bmesh(bm, planetario, suavizar=True)

    # ---- passarela suspensa (curva de Bezier) ----------------------
    curva = bpy.data.curves.new("CU_Planetario_Rampa", type="CURVE")
    curva.dimensions = "3D"
    curva.resolution_u = 8
    curva.extrude = 0.26          # largura do tabuleiro
    curva.bevel_depth = 0.07      # arredonda a borda do tabuleiro
    curva.bevel_resolution = 2
    curva.materials.append(mat_concreto)

    spline = curva.splines.new("BEZIER")
    pontos = [(-4.80, 2.40, 0.30), (-2.70, 3.80, 1.00), (0.40, 3.60, 1.70),
              (3.20, 2.00, 2.05), (3.90, -1.00, 1.25)]
    spline.bezier_points.add(len(pontos) - 1)
    for ponto, coordenada in zip(spline.bezier_points, pontos):
        ponto.co = coordenada
        ponto.handle_left_type = "AUTO"
        ponto.handle_right_type = "AUTO"
        ponto.tilt = math.radians(90.0)   # deixa o tabuleiro na horizontal

    rampa = bpy.data.objects.new("Planetario_Rampa", curva)
    colecao.objects.link(rampa)
    rampa.parent = planetario

    return planetario, rampa


# ===================================================================
# 5. CENARIO DE FORTALEZA
# ===================================================================

def criar_grade(bm, x0, x1, y0, y1, nx, ny, funcao_altura):
    """Gera uma malha regular e aplica uma funcao de altura vertice a vertice."""
    linhas = []
    for j in range(ny + 1):
        v = j / ny
        y = y0 + (y1 - y0) * v
        linha = []
        for i in range(nx + 1):
            u = i / nx
            x = x0 + (x1 - x0) * u
            linha.append(bm.verts.new((x, y, funcao_altura(x, y))))
        linhas.append(linha)
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((linhas[j][i], linhas[j][i + 1],
                          linhas[j + 1][i + 1], linhas[j + 1][i]))
    return linhas


def altura_da_areia(x, y):
    """Relevo da praia: duas dunas, ondulacao suave e descida para o mar."""
    z = 0.30
    z += 0.60 * math.exp(-(((x + 26.0) ** 2) / 240.0 + ((y - 2.0) ** 2) / 420.0))
    z += 0.85 * math.exp(-(((x - 32.0) ** 2) / 300.0 + ((y + 16.0) ** 2) / 520.0))
    z += 0.09 * math.sin(x * 0.22) * math.cos(y * 0.18)

    # linha da costa irregular: a praia molhada mergulha abaixo do nivel do mar
    costa = LINHA_DA_COSTA + 1.6 * math.sin(x * 0.11) + 0.8 * math.sin(x * 0.27)
    if y > costa - 6.0:
        t = min(1.0, (y - (costa - 6.0)) / 7.0)
        z = z * (1.0 - t) - 0.55 * t

    # bordas afundam para nao aparecer o limite do plano
    borda = min(1.0, (150.0 - abs(x)) / 30.0)
    z = z * borda - 0.60 * (1.0 - borda)
    return z


def construir_cenario(colecao, materiais):
    mat_mar = materiais["mar"]
    mat_areia = materiais["areia"]
    mat_piso = materiais["piso"]
    mat_pedra = materiais["pedra"]
    mat_tronco = materiais["madeira"]
    mat_folha = materiais["vegetacao"]

    # ---- mar ------------------------------------------------------
    mar = novo_objeto_malha("CEN_Mar_Atlantico", colecao, (mat_mar,))
    bm = bmesh.new()
    criar_grade(bm, -200.0, 200.0, -70.0, 280.0, 80, 80, lambda x, y: 0.0)
    gravar_bmesh(bm, mar, suavizar=True)

    textura = bpy.data.textures.get("TEX_Ondulacao_Mar")
    if textura is None:
        textura = bpy.data.textures.new("TEX_Ondulacao_Mar", type="CLOUDS")
    textura.noise_scale = 8.0

    deslocamento = mar.modifiers.new("MOD_Displace_Mar", "DISPLACE")
    deslocamento.texture = textura
    deslocamento.texture_coords = "GLOBAL"
    deslocamento.strength = 0.30
    deslocamento.mid_level = 0.5

    ondas = mar.modifiers.new("MOD_Wave_Mar", "WAVE")   # ja animado para a AP2
    ondas.height = 0.07
    ondas.width = 6.0
    ondas.narrowness = 1.8
    ondas.speed = 0.10
    ondas.start_position_y = 120.0

    # ---- faixa de areia -------------------------------------------
    areia = novo_objeto_malha("CEN_Praia_Beira_Mar", colecao, (mat_areia,))
    bm = bmesh.new()
    criar_grade(bm, -150.0, 150.0, -80.0, LINHA_DA_COSTA + 9.0, 90, 60,
                altura_da_areia)
    gravar_bmesh(bm, areia, suavizar=True)

    # ---- deck-mirante que sustenta a palavra ----------------------
    deck = novo_objeto_malha("CEN_Deck_Mirante", colecao, (mat_piso,))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, 0.30, 0.45))
                @ Matrix.Diagonal((11.6, 4.8, 1.40, 1.0))))
    topo = face_mais_alta(bm)
    bmesh.ops.inset_region(bm, faces=[topo], thickness=0.40, depth=0.0,
                           use_even_offset=True, use_boundary=True)
    extrudar_face(bm, topo, Vector((0.0, 0.0, 0.07)))
    gravar_bmesh(bm, deck)

    chanfro = deck.modifiers.new("MOD_Bevel_Deck", "BEVEL")
    chanfro.width = 0.05
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # ---- escadaria (modificador Array) ----------------------------
    escada = novo_objeto_malha("CEN_Escadaria_Deck", colecao, (mat_piso,))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, -2.42, 0.88))
                @ Matrix.Diagonal((4.40, 0.52, 0.24, 1.0))))
    gravar_bmesh(bm, escada)

    degraus = escada.modifiers.new("MOD_Array_Degraus", "ARRAY")
    degraus.count = 4
    degraus.use_relative_offset = False
    degraus.use_constant_offset = True
    degraus.constant_offset_displace = (0.0, -0.50, -0.22)

    # ---- rochedo do farol -----------------------------------------
    rochedo = novo_objeto_malha("CEN_Rochedo_Farol", colecao, (mat_pedra,))
    bm = bmesh.new()
    criar_cone(bm, 3.30, 2.10, 1.50, segmentos=9,
               matriz=Matrix.Translation((0.0, 0.0, 0.30)))
    for vertice in bm.verts:
        vertice.co.z += 0.16 * math.sin(vertice.co.x * 1.7 + vertice.co.y)
    gravar_bmesh(bm, rochedo)
    rochedo.location = (-11.00, 11.00, 0.0)
    rochedo.rotation_euler = (0.0, 0.0, math.radians(18.0))

    # ---- coqueiros (duplicatas vinculadas) ------------------------
    coqueiro = construir_coqueiro(colecao, mat_tronco, mat_folha)
    posicoes = [
        ((-5.00, 4.00, 0.33), math.radians(25.0), 1.00),
        ((5.50, 6.00, 0.38), math.radians(-40.0), 0.88),
        ((11.00, 3.00, 0.45), math.radians(115.0), 1.12),
    ]
    coqueiros = []
    for indice, (local, giro, escala) in enumerate(posicoes, start=1):
        if indice == 1:
            atual = coqueiro
        else:
            atual = coqueiro.copy()      # duplicata vinculada: mesma malha
            colecao.objects.link(atual)
        atual.name = "CEN_Coqueiro_%02d" % indice
        atual.location = local
        atual.rotation_euler = (math.radians(2.0 * indice), math.radians(-4.0), giro)
        atual.scale = (escala, escala, escala)
        coqueiros.append(atual)

    return {"mar": mar, "areia": areia, "deck": deck, "escada": escada,
            "rochedo": rochedo, "coqueiros": coqueiros}


def construir_coqueiro(colecao, mat_tronco, mat_folha):
    """Coqueiro modelado por lofting de aneis + folhas em tiras afiladas."""
    obj = novo_objeto_malha("CEN_Coqueiro_01", colecao, (mat_tronco, mat_folha))
    bm = bmesh.new()

    altura, aneis, lados = 5.40, 9, 8
    anterior = None
    for k in range(aneis + 1):
        t = k / aneis
        centro_x = 0.60 * t * t
        raio = 0.26 * (1.0 - 0.52 * t)
        atual = []
        for lado in range(lados):
            angulo = 2.0 * math.pi * lado / lados
            atual.append(bm.verts.new((centro_x + raio * math.cos(angulo),
                                       raio * math.sin(angulo), altura * t)))
        if anterior is not None:
            for lado in range(lados):
                bm.faces.new((anterior[lado], anterior[(lado + 1) % lados],
                              atual[(lado + 1) % lados], atual[lado]))
        anterior = atual

    faces_folha = []
    base = Vector((0.60, 0.0, altura))
    for folha in range(7):
        angulo = 2.0 * math.pi * folha / 7.0 + 0.35
        direcao = Vector((math.cos(angulo), math.sin(angulo), 0.0))
        lateral = Vector((-direcao.y, direcao.x, 0.0))
        borda = None
        for passo in range(6):
            t = passo / 5.0
            centro = base + direcao * (2.70 * t) + Vector((0.0, 0.0,
                                                           0.85 * t - 2.40 * t * t))
            meia_largura = 0.30 * (1.0 - t) + 0.04
            a = bm.verts.new(centro + lateral * meia_largura)
            b = bm.verts.new(centro - lateral * meia_largura)
            if borda is not None:
                faces_folha.append(bm.faces.new((borda[0], borda[1], b, a)))
            borda = (a, b)
    marcar_material(faces_folha, 1)

    gravar_bmesh(bm, obj)
    return obj


# ===================================================================
# 6. CAMERA, STORYBOARD E TIMELINE
# ===================================================================

def nova_camera(nome, colecao, local, alvo, lente=35.0):
    dados = bpy.data.cameras.new("CAM_DATA_" + nome)
    dados.lens = lente
    dados.clip_end = 600.0
    camera = bpy.data.objects.new(nome, dados)
    colecao.objects.link(camera)
    camera.location = local
    apontar_para(camera, alvo)
    return camera


def configurar_cameras(colecao, pivo_palavra):
    cena = bpy.context.scene

    alvo = bpy.data.objects.new("CAM_Alvo_Principal", None)
    alvo.empty_display_type = "SPHERE"
    alvo.empty_display_size = 0.35
    colecao.objects.link(alvo)
    alvo.location = (0.0, 1.50, 2.60)

    principal = nova_camera("CAM_Principal", colecao, (0.0, -15.00, 5.20),
                            alvo.location, lente=35.0)
    seguir = principal.constraints.new("TRACK_TO")
    seguir.target = alvo
    seguir.track_axis = "TRACK_NEGATIVE_Z"
    seguir.up_axis = "UP_Y"

    # profundidade de campo ja apontada para a palavra (sera usada na AP2)
    principal.data.dof.focus_object = pivo_palavra
    principal.data.dof.aperture_fstop = 4.0
    principal.data.dof.use_dof = False

    cena.camera = principal

    storyboard = [
        ("CAM_SB1_Amanhecer", (-2.40, -7.00, 1.15), (2.00, 40.00, 3.20), 50.0),
        ("CAM_SB2_Construcao", (-10.50, -9.00, 3.60), (-0.60, 1.20, 2.20), 45.0),
        ("CAM_SB3_Assinatura", (0.00, -11.20, 3.05), (0.00, 1.20, 2.35), 42.0),
    ]
    cameras_sb = [nova_camera(nome, colecao, local, olhar, lente)
                  for nome, local, olhar, lente in storyboard]

    return principal, alvo, cameras_sb


def configurar_timeline():
    cena = bpy.context.scene
    cena.render.fps = FPS
    cena.frame_start = FRAME_INICIAL
    cena.frame_end = FRAME_FINAL
    cena.render.resolution_x = 1920
    cena.render.resolution_y = 1080
    cena.render.resolution_percentage = 100

    cena.timeline_markers.clear()
    momentos = [
        ("SB1_Amanhecer_no_Mucuripe", 1),
        ("SB2_Construcao_da_Palavra", 121),
        ("SB3_Assinatura_Ibmec", 241),
        ("Fim_15s", FRAME_FINAL),
    ]
    for nome, frame in momentos:
        cena.timeline_markers.new(nome, frame=frame)

    cena.frame_set(300)
    return momentos


def criar_luz(colecao):
    dados = bpy.data.lights.new("LUZ_DATA_Sol", type="SUN")
    dados.energy = 3.2
    dados.angle = math.radians(2.0)
    luz = bpy.data.objects.new("LUZ_Sol_Fortaleza", dados)
    colecao.objects.link(luz)
    luz.location = (14.0, 26.0, 18.0)
    luz.rotation_euler = (math.radians(52.0), math.radians(6.0), math.radians(206.0))
    return luz


# ===================================================================
# 7. MONTAGEM DA CENA
# ===================================================================

def main():
    if bpy.app.version < (4, 5, 0):
        print("[AP1] AVISO: este projeto foi escrito para o Blender 4.5 LTS "
              "(versao atual: %d.%d.%d)." % bpy.app.version)

    limpar_cena()

    cena = bpy.context.scene
    raiz = nova_colecao(COLECAO_RAIZ, cena.collection)
    col_palavra = nova_colecao("01_Palavra_Ibmec", raiz)
    col_objetos = nova_colecao("02_Objetos_Autorais", raiz)
    col_cenario = nova_colecao("03_Cenario_Fortaleza", raiz)
    col_camera = nova_colecao("04_Camera_e_Auxiliares", raiz)

    # ---- materiais -------------------------------------------------
    mat_azul = obter_material("MAT_Ibmec_Azul", HEX_AZUL_IBMEC, 0.38,
                              apelidos=("Azul Ibmec",))
    mat_amarelo = obter_material("MAT_Ibmec_Amarelo", HEX_AMARELO_IBMEC, 0.35,
                                 apelidos=("Amarelo Ibmec",))
    materiais = {
        "azul": mat_azul,
        "amarelo": mat_amarelo,
        "mar": obter_material("MAT_Mar_Atlantico", "1E6F8C", 0.18),
        "areia": obter_material("MAT_Areia_Fortaleza", "E8D2A6", 0.85),
        "concreto": obter_material("MAT_Concreto_Claro", "E6E6E1", 0.62),
        "piso": obter_material("MAT_Piso_Deck", "C9B48F", 0.72),
        "pedra": obter_material("MAT_Pedra_Litoral", "8A8378", 0.80),
        "madeira": obter_material("MAT_Madeira_Jangada", "9C6B3F", 0.70),
        "vela": obter_material("MAT_Vela_Algodao", "F2EDE0", 0.68),
        "vegetacao": obter_material("MAT_Vegetacao_Coqueiro", "3E7A3A", 0.66),
        "luz": obter_material("MAT_Luz_Farol", "FFD86B", 0.30),
    }

    # ---- palavra ---------------------------------------------------
    pivo, letras = construir_palavra(col_palavra, mat_azul, mat_amarelo)

    # ---- objetos autorais ------------------------------------------
    farol, _vidro = construir_farol(col_objetos, materiais["concreto"],
                                    mat_azul, materiais["luz"])
    farol.location = (-11.00, 11.00, 0.95)
    farol.rotation_euler = (0.0, 0.0, math.radians(-12.0))
    farol.scale = (1.0, 1.0, 1.0)

    jangada, _vela = construir_jangada(col_objetos, materiais["madeira"],
                                       materiais["vela"], mat_azul)
    jangada.location = (-5.00, 20.00, 0.10)
    jangada.rotation_euler = (0.0, math.radians(3.0), math.radians(-127.0))
    jangada.scale = (1.15, 1.15, 1.15)

    planetario, _rampa = construir_planetario(col_objetos,
                                              materiais["concreto"], mat_azul)
    planetario.location = (9.00, 7.50, 0.36)
    planetario.rotation_euler = (0.0, 0.0, math.radians(24.0))
    planetario.scale = (1.05, 1.05, 1.05)

    # ---- cenario e camera ------------------------------------------
    construir_cenario(col_cenario, materiais)
    criar_luz(col_camera)
    principal, alvo, cameras_sb = configurar_cameras(col_camera, pivo)
    momentos = configurar_timeline()

    # ---- relatorio no console --------------------------------------
    print("")
    print("=" * 62)
    print("AP1 - 'Do Mucuripe ao Futuro' | Ibmec Fortaleza")
    print("=" * 62)
    print("Colecao principal ....: %s" % COLECAO_RAIZ)
    print("Palavra ..............: %d objetos (letras + ponto do i)" % len(letras))
    print("Objetos autorais .....: %s | %s | %s"
          % (farol.name, jangada.name, planetario.name))
    print("Camera principal .....: %s (lente %.0f mm, Track To em %s)"
          % (principal.name, principal.data.lens, alvo.name))
    print("Cameras de storyboard : %s" % ", ".join(c.name for c in cameras_sb))
    print("Timeline .............: frames %d a %d | %d fps | %d s"
          % (FRAME_INICIAL, FRAME_FINAL, FPS, DURACAO_SEGUNDOS))
    print("Marcadores ...........: %s"
          % ", ".join("%s@%d" % (n, f) for n, f in momentos))
    print("=" * 62)

    if SALVAR_BLEND:
        bpy.ops.wm.save_as_mainfile(filepath=CAMINHO_BLEND)
        print("[AP1] Arquivo salvo em %s" % CAMINHO_BLEND)


main()
