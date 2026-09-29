# -*- coding: utf-8 -*-
"""
AP1 - Conceito e Modelagem da peca "Ibmec em 15 segundos"
Peca (cenario alternativo, tema EDUCACAO): "A Sala que Abre o Mundo" - Ibmec

Cena-conceito construida integralmente por script no Blender 4.5 LTS.
Mesma estrutura tecnica do script principal (AP1_IgorMariano.py), com um
cenario voltado para a EDUCACAO: um anfiteatro/sala de aula do Ibmec, em que a
palavra "ibmec" ocupa o painel frontal, acima do palco, como assinatura da aula.

O que este script monta:
  - colecao principal AP1_Ibmec_Educacao com 4 subcolecoes organizadas;
  - a palavra "ibmec" com as cores oficiais (azul #002555 / amarelo #F5AC00),
    cada letra como objeto independente e o ponto do "i" separado - aqui ele e
    a "lampada da ideia", que na AP2 acende e se encaixa sobre a letra;
  - os TRES objetos autorais, todos modelados do zero:
        OBJ_Livro_Aberto        (grade curvada + solidify/bevel)
        OBJ_Globo_Armilar       (revolucao + curvas de Bezier ciclicas)
        OBJ_Capelo_Formatura    (composicao de malhas + inset/extrude + curva)
  - o cenario da sala (piso, paredes, painel-lousa com reentrancia, palco,
    arquibancada e bancadas em Array, pulpito, luminarias em Array e cadeiras
    em duplicatas vinculadas);
  - camera principal com alvo (Track To), 3 cameras de storyboard e
    marcadores de timeline;
  - timeline de 15 s a 24 fps = 360 frames.

Como usar:
  1. Abra o Blender 4.5 LTS (arquivo novo ou o .blend do logo).
  2. Aba Scripting > Open > selecione este arquivo.
  3. Run Script (Alt+P).
  4. No Windows, veja as mensagens em Window > Toggle System Console.

O script e idempotente: rodar de novo apaga e reconstroi a colecao,
sem duplicar objetos (nada de ".001").
"""

import math
import bpy
import bmesh
from mathutils import Matrix, Vector

# ===================================================================
# 0. CONFIGURACAO
# ===================================================================

COLECAO_RAIZ = "AP1_Ibmec_Educacao"

# --- duracao planejada da peca -------------------------------------
FPS = 24
DURACAO_SEGUNDOS = 15
FRAME_INICIAL = 1
FRAME_FINAL = FRAME_INICIAL + FPS * DURACAO_SEGUNDOS - 1   # 360 frames

# --- palavra -------------------------------------------------------
TEXTO_LOGO = "ibmec"          # marca em caixa baixa, como na identidade visual
LARGURA_PALAVRA = 7.6         # largura final em metros (escala intencional)
ALTURA_BASE_PALAVRA = 3.05    # altura da palavra no painel frontal
PROFUNDIDADE_PALAVRA = 9.62   # y do painel: a palavra fica em relevo sobre ele
TAMANHO_FONTE = 3.0
PROFUNDIDADE_LETRA = 0.22     # extrusao do texto
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
CAMINHO_SVG_LOGO = ""

# --- cores lidas do arquivo AP1-Logo-Ibmec-3D.blend ----------------
HEX_AZUL_IBMEC = "002555"
HEX_AMARELO_IBMEC = "F5AC00"

SALVAR_BLEND = False
CAMINHO_BLEND = r"E:\AC-Computação-Gráfica\AP1\AP1_IgorMariano_Educacao.blend"

# --- geometria da sala ---------------------------------------------
LARGURA_SALA = 24.0           # eixo x
FUNDO_SALA = 10.0             # y do painel frontal (atras do palco)
PLATEIA_SALA = -12.0          # y do fundo da plateia
ALTURA_PALCO = 0.90           # topo do palco
ALTURA_PE_DIREITO = 6.40


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
    do torno. Usada na esfera do globo, no pedestal e na copa do capelo.
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


def curva_circular(nome, raio, espessura, colecao, material, resolucao=12):
    """Cria um anel a partir de uma curva de Bezier ciclica com bevel.

    Tecnica: curva + bevel_depth (o mesmo principio do tubo). Usada nos tres
    aneis do globo armilar; o fator 0.5523 e a aproximacao classica de um
    circulo por quatro segmentos de Bezier cubicos.
    """
    curva = bpy.data.curves.new("CU_" + nome, type="CURVE")
    curva.dimensions = "3D"
    curva.resolution_u = resolucao
    curva.bevel_depth = espessura
    curva.bevel_resolution = 3
    curva.materials.append(material)

    spline = curva.splines.new("BEZIER")
    spline.bezier_points.add(3)
    alca = raio * 0.5523
    posicoes = [(raio, 0.0, 0.0), (0.0, raio, 0.0),
                (-raio, 0.0, 0.0), (0.0, -raio, 0.0)]
    tangentes = [(0.0, alca, 0.0), (-alca, 0.0, 0.0),
                 (0.0, -alca, 0.0), (alca, 0.0, 0.0)]
    for ponto, pos, tan in zip(spline.bezier_points, posicoes, tangentes):
        # FREE: as alcas abaixo valem como escritas, sem realinhamento automatico
        ponto.handle_left_type = "FREE"
        ponto.handle_right_type = "FREE"
        ponto.co = pos
        ponto.handle_left = (pos[0] - tan[0], pos[1] - tan[1], pos[2] - tan[2])
        ponto.handle_right = (pos[0] + tan[0], pos[1] + tan[1], pos[2] + tan[2])
    spline.use_cyclic_u = True

    obj = bpy.data.objects.new(nome, curva)
    colecao.objects.link(obj)
    return obj


# ===================================================================
# 2. LIMPEZA / RECONSTRUCAO
# ===================================================================

def limpar_cena():
    """Remove a colecao anterior (objetos + subcolecoes) e o cubo padrao."""
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
    print("[AP1-EDU] Fonte especifica nao encontrada; usando a fonte padrao.")
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

    Neste cenario o pingo e a "lampada da ideia": na AP2 ele acende sobre a
    sala e desce ate se encaixar na letra, fechando a assinatura da marca.
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
            print("[AP1-EDU] Nao foi possivel importar o SVG:", erro)
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
    print("[AP1-EDU] SVG importado:", len(novos), "curvas.")
    return novos


def construir_palavra(colecao, mat_azul, mat_amarelo):
    """Monta a palavra letra a letra sob um pivo unico, em relevo no painel.

    Hierarquia: LOGO_Palavra_Ibmec (empty) -> LOGO_Letra_* + LOGO_Ponto_i.
    O pivo concentra as transformacoes da palavra inteira (rotacao de 90 graus
    em X para as letras ficarem de frente para a plateia, translacao ate o
    painel frontal e escala ate a largura alvo), enquanto cada letra mantem a
    sua propria translacao local - pronta para a animacao de entrada da AP2.
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

    pivo.location = (0.0, PROFUNDIDADE_PALAVRA, ALTURA_BASE_PALAVRA)
    pivo.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    pivo.scale = (escala, escala, escala)

    for obj in letras:
        obj.parent = pivo          # parent_inverse = identidade:
                                   # a posicao da letra e lida no espaco do pivo

    print("[AP1-EDU] Palavra: largura bruta %.2f -> escala %.3f -> %.2f m."
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

    print("[AP1-EDU] Palavra construida a partir de texto 3D (%d objetos)."
          % len(letras))
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

def construir_livro(colecao, mat_papel, mat_capa, mat_amarelo):
    """Objeto autoral 1 - Livro aberto: o conhecimento que se abre na aula.

    Tecnicas: duas grades geradas por funcao (as paginas encurvadas a partir
    da lombada), modificador Solidify para dar espessura ao bloco de paginas,
    Bevel nas bordas, capa como malha propria com Solidify e um marcador de
    pagina em amarelo Ibmec modelado a parte.
    """
    livro = novo_objeto_malha("OBJ_Livro_Aberto", colecao, (mat_papel,))
    bm = bmesh.new()

    largura_pagina, profundidade_pagina = 1.30, 1.70
    colunas, linhas = 10, 8

    def pagina(sinal):
        grade = []
        for j in range(linhas + 1):
            v = j / linhas
            y = -profundidade_pagina / 2.0 + profundidade_pagina * v
            linha = []
            for i in range(colunas + 1):
                u = i / colunas
                x = sinal * (0.05 + largura_pagina * u)
                # a pagina sobe conforme se afasta da lombada (curvatura do papel)
                z = 0.30 * (u ** 1.7) + 0.035 * math.sin(v * math.pi)
                linha.append(bm.verts.new((x, y, z)))
            grade.append(linha)
        for j in range(linhas):
            for i in range(colunas):
                if sinal > 0:
                    bm.faces.new((grade[j][i], grade[j][i + 1],
                                  grade[j + 1][i + 1], grade[j + 1][i]))
                else:
                    bm.faces.new((grade[j][i + 1], grade[j][i],
                                  grade[j + 1][i], grade[j + 1][i + 1]))

    pagina(+1.0)
    pagina(-1.0)
    gravar_bmesh(bm, livro)

    bloco = livro.modifiers.new("MOD_Solidify_Paginas", "SOLIDIFY")
    bloco.thickness = 0.085
    bloco.offset = -1.0

    chanfro = livro.modifiers.new("MOD_Bevel_Livro", "BEVEL")
    chanfro.width = 0.008
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # ---- capa (malha propria, em azul Ibmec) -----------------------
    capa = novo_objeto_malha("Livro_Capa", colecao, (mat_capa,))
    bm_capa = bmesh.new()
    colunas_capa = 14
    grade = []
    for j in range(2):
        y = -profundidade_pagina / 2.0 - 0.06 + (profundidade_pagina + 0.12) * j
        linha = []
        for i in range(colunas_capa + 1):
            u = i / colunas_capa
            x = (u - 0.5) * 2.0 * (largura_pagina + 0.12)
            z = 0.30 * (abs(u - 0.5) * 2.0) ** 1.7 - 0.02
            linha.append(bm_capa.verts.new((x, y, z)))
        grade.append(linha)
    for i in range(colunas_capa):
        bm_capa.faces.new((grade[0][i], grade[0][i + 1],
                           grade[1][i + 1], grade[1][i]))
    gravar_bmesh(bm_capa, capa)

    espessura = capa.modifiers.new("MOD_Solidify_Capa", "SOLIDIFY")
    espessura.thickness = 0.06
    espessura.offset = -1.0

    capa.parent = livro

    # ---- marcador de pagina (fita amarela da marca) ----------------
    marcador = novo_objeto_malha("Livro_Marcador", colecao, (mat_amarelo,))
    bm_marca = bmesh.new()
    bmesh.ops.create_cube(
        bm_marca, size=1.0,
        matrix=(Matrix.Translation((0.55, -0.72, 0.16))
                @ Matrix.Rotation(math.radians(-9.0), 4, "Z")
                @ Matrix.Diagonal((0.16, 1.05, 0.012, 1.0))))
    gravar_bmesh(bm_marca, marcador)
    marcador.parent = livro

    return livro, capa, marcador


def construir_globo(colecao, mat_metal, mat_azul, mat_amarelo):
    """Objeto autoral 2 - Globo armilar: o mundo que a aula alcanca.

    Tecnicas: superficie de revolucao para o pedestal torneado e para a
    esfera, atribuicao de material por faixa de altura e tres curvas de
    Bezier ciclicas com bevel (equador, meridiano e ecliptica) posicionadas
    por rotacoes locais.
    """
    globo = novo_objeto_malha("OBJ_Globo_Armilar", colecao,
                              (mat_metal, mat_azul))
    bm = bmesh.new()

    # pedestal torneado (revolucao de um perfil desenhado a mao)
    perfil_pe = [
        (0.00, 0.00), (0.52, 0.00), (0.52, 0.09), (0.34, 0.17),
        (0.13, 0.28), (0.10, 0.92), (0.17, 1.04), (0.00, 1.10),
    ]
    superficie_de_revolucao(bm, perfil_pe, segmentos=24)

    # esfera do globo: meia circunferencia girada em torno de Z
    raio, centro_z = 0.74, 1.90
    perfil_esfera = []
    passos = 14
    for k in range(passos + 1):
        angulo = math.radians(-90.0 + 180.0 * k / passos)
        perfil_esfera.append((raio * math.cos(angulo),
                              centro_z + raio * math.sin(angulo)))
    superficie_de_revolucao(bm, perfil_esfera, segmentos=32)

    # a esfera recebe o azul Ibmec; o pedestal fica metalico
    for face in bm.faces:
        if face.calc_center_median().z > 1.16:
            face.material_index = 1

    gravar_bmesh(bm, globo, suavizar=True)

    # ---- aneis (curvas de Bezier ciclicas com bevel) ---------------
    aneis = []
    definicoes = [
        ("Globo_Anel_Equador", 0.92, 0.035, (0.0, 0.0, 0.0), mat_amarelo),
        ("Globo_Anel_Meridiano", 0.95, 0.030,
         (math.radians(90.0), 0.0, 0.0), mat_metal),
        ("Globo_Anel_Ecliptica", 0.98, 0.026,
         (math.radians(90.0), 0.0, math.radians(58.0)), mat_metal),
    ]
    for nome, raio_anel, espessura, giro, material in definicoes:
        anel = curva_circular(nome, raio_anel, espessura, colecao, material)
        anel.location = (0.0, 0.0, centro_z)
        anel.rotation_euler = giro
        anel.parent = globo
        anel.matrix_parent_inverse = Matrix.Identity(4)
        aneis.append(anel)

    return globo, aneis


def construir_capelo(colecao, mat_tecido, mat_azul, mat_amarelo):
    """Objeto autoral 3 - Capelo de formatura: a entrega da educacao.

    Tecnicas: copa por superficie de revolucao, inset + extrusao no topo para
    o encaixe do botao, composicao com a tabua quadrada (cubo transformado),
    material por faixa de altura, modificador Bevel e uma curva de Bezier com
    bevel para o cordao, que balanca na AP2.
    """
    capelo = novo_objeto_malha("OBJ_Capelo_Formatura", colecao,
                               (mat_tecido, mat_azul))
    bm = bmesh.new()

    # copa (revolucao de um perfil levemente abaulado)
    perfil_copa = [
        (0.00, 0.00), (0.50, 0.02), (0.53, 0.18), (0.50, 0.34),
        (0.44, 0.44), (0.00, 0.47),
    ]
    superficie_de_revolucao(bm, perfil_copa, segmentos=28)

    # inset + extrusao no topo da copa: encaixe do botao do cordao
    topo = face_mais_alta(bm)
    bmesh.ops.inset_region(bm, faces=[topo], thickness=0.14, depth=0.0,
                           use_even_offset=True, use_boundary=True)
    bm.normal_update()
    extrudar_face(bm, topo, Vector((0.0, 0.0, -0.05)))

    # tabua quadrada (o "mortarboard"), levemente inclinada
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, 0.0, 0.53))
                @ Matrix.Rotation(math.radians(-7.0), 4, "Y")
                @ Matrix.Diagonal((1.70, 1.70, 0.055, 1.0))))

    # a tabua fica em azul Ibmec, a copa em tecido escuro
    for face in bm.faces:
        if face.calc_center_median().z >= 0.48:
            face.material_index = 1

    gravar_bmesh(bm, capelo)

    chanfro = capelo.modifiers.new("MOD_Bevel_Capelo", "BEVEL")
    chanfro.width = 0.012
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # ---- botao do cordao -------------------------------------------
    botao = novo_objeto_malha("Capelo_Botao", colecao, (mat_amarelo,))
    bm_botao = bmesh.new()
    criar_cone(bm_botao, 0.11, 0.09, 0.07, segmentos=16,
               matriz=Matrix.Translation((0.0, 0.0, 0.60)))
    gravar_bmesh(bm_botao, botao, suavizar=True)
    botao.parent = capelo

    # ---- cordao (curva de Bezier com bevel) ------------------------
    curva = bpy.data.curves.new("CU_Capelo_Cordao", type="CURVE")
    curva.dimensions = "3D"
    curva.resolution_u = 8
    curva.bevel_depth = 0.022
    curva.bevel_resolution = 2
    curva.materials.append(mat_amarelo)

    spline = curva.splines.new("BEZIER")
    pontos = [(0.00, 0.00, 0.62), (0.36, 0.10, 0.60), (0.78, 0.18, 0.52),
              (0.96, 0.22, 0.20), (0.99, 0.24, -0.26)]
    spline.bezier_points.add(len(pontos) - 1)
    for ponto, coordenada in zip(spline.bezier_points, pontos):
        ponto.co = coordenada
        ponto.handle_left_type = "AUTO"
        ponto.handle_right_type = "AUTO"

    cordao = bpy.data.objects.new("Capelo_Cordao", curva)
    colecao.objects.link(cordao)
    cordao.parent = capelo

    return capelo, cordao


# ===================================================================
# 5. CENARIO: A SALA DE AULA DO IBMEC
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


def construir_cenario(colecao, materiais):
    mat_piso = materiais["piso"]
    mat_parede = materiais["parede"]
    mat_painel = materiais["painel"]
    mat_madeira = materiais["madeira"]
    mat_metal = materiais["metal"]
    mat_azul = materiais["azul"]
    mat_luz = materiais["luz"]

    metade = LARGURA_SALA / 2.0

    # ---- piso ------------------------------------------------------
    piso = novo_objeto_malha("CEN_Piso_Sala", colecao, (mat_piso,))
    bm = bmesh.new()
    criar_grade(bm, -metade, metade, PLATEIA_SALA - 2.0, FUNDO_SALA,
                24, 24, lambda x, y: 0.0)
    gravar_bmesh(bm, piso)

    # ---- paredes laterais ------------------------------------------
    paredes = novo_objeto_malha("CEN_Paredes_Sala", colecao, (mat_parede,))
    bm = bmesh.new()
    for lado in (-1.0, 1.0):
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=(Matrix.Translation((lado * (metade + 0.20),
                                        (FUNDO_SALA + PLATEIA_SALA) / 2.0,
                                        ALTURA_PE_DIREITO / 2.0))
                    @ Matrix.Diagonal((0.40, FUNDO_SALA - PLATEIA_SALA + 4.0,
                                       ALTURA_PE_DIREITO, 1.0))))
    gravar_bmesh(bm, paredes)

    # ---- painel frontal que recebe a palavra -----------------------
    # inset + extrusao criam a reentrancia escura onde a marca fica em relevo
    painel = novo_objeto_malha("CEN_Painel_Frontal", colecao,
                               (mat_parede, mat_painel))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, FUNDO_SALA + 0.50,
                                    ALTURA_PE_DIREITO / 2.0))
                @ Matrix.Diagonal((LARGURA_SALA + 0.8, 1.00,
                                   ALTURA_PE_DIREITO, 1.0))))

    bm.faces.ensure_lookup_table()
    frente = min(bm.faces, key=lambda f: f.calc_center_median().y)
    bmesh.ops.inset_region(bm, faces=[frente], thickness=1.50, depth=0.0,
                           use_even_offset=True, use_boundary=True)
    bm.normal_update()
    fundo_painel = extrudar_face(bm, frente, Vector((0.0, 0.26, 0.0)))
    if fundo_painel is not None:
        fundo_painel.material_index = 1
    gravar_bmesh(bm, painel)

    chanfro = painel.modifiers.new("MOD_Bevel_Painel", "BEVEL")
    chanfro.width = 0.04
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # ---- palco (tablado do professor) ------------------------------
    palco = novo_objeto_malha("CEN_Palco", colecao, (mat_madeira,))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, 7.00, ALTURA_PALCO / 2.0))
                @ Matrix.Diagonal((15.0, 6.60, ALTURA_PALCO, 1.0))))
    topo = face_mais_alta(bm)
    bmesh.ops.inset_region(bm, faces=[topo], thickness=0.35, depth=0.0,
                           use_even_offset=True, use_boundary=True)
    extrudar_face(bm, topo, Vector((0.0, 0.0, 0.05)))
    gravar_bmesh(bm, palco)

    chanfro = palco.modifiers.new("MOD_Bevel_Palco", "BEVEL")
    chanfro.width = 0.05
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # ---- degraus de acesso ao palco (Array) ------------------------
    degraus = novo_objeto_malha("CEN_Degraus_Palco", colecao, (mat_madeira,))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, 3.50, 0.68))
                @ Matrix.Diagonal((4.60, 0.55, 0.22, 1.0))))
    gravar_bmesh(bm, degraus)

    array_degraus = degraus.modifiers.new("MOD_Array_Degraus", "ARRAY")
    array_degraus.count = 3
    array_degraus.use_relative_offset = False
    array_degraus.use_constant_offset = True
    array_degraus.constant_offset_displace = (0.0, -0.55, -0.22)

    # ---- arquibancada da plateia (Array) ---------------------------
    arquibancada = novo_objeto_malha("CEN_Arquibancada", colecao, (mat_piso,))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, -0.60, 0.22))
                @ Matrix.Diagonal((LARGURA_SALA - 1.0, 3.20, 0.44, 1.0))))
    gravar_bmesh(bm, arquibancada)

    array_niveis = arquibancada.modifiers.new("MOD_Array_Niveis", "ARRAY")
    array_niveis.count = 4
    array_niveis.use_relative_offset = False
    array_niveis.use_constant_offset = True
    array_niveis.constant_offset_displace = (0.0, -3.20, 0.44)

    # ---- bancadas dos alunos (Array, uma por nivel) ----------------
    bancada = novo_objeto_malha("CEN_Bancadas_Alunos", colecao,
                                (mat_madeira, mat_metal))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, -1.35, 1.14))
                @ Matrix.Diagonal((LARGURA_SALA - 3.0, 0.90, 0.10, 1.0))))
    pernas = bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, -1.35, 0.78))
                @ Matrix.Diagonal((LARGURA_SALA - 3.6, 0.16, 0.62, 1.0))))
    verts_pernas = set(pernas["verts"])
    marcar_material([f for f in bm.faces
                     if all(v in verts_pernas for v in f.verts)], 1)
    gravar_bmesh(bm, bancada)

    array_bancadas = bancada.modifiers.new("MOD_Array_Bancadas", "ARRAY")
    array_bancadas.count = 4
    array_bancadas.use_relative_offset = False
    array_bancadas.use_constant_offset = True
    array_bancadas.constant_offset_displace = (0.0, -3.20, 0.44)

    # ---- pulpito que sustenta o livro ------------------------------
    pulpito = novo_objeto_malha("CEN_Pulpito", colecao, (mat_madeira, mat_azul))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((-3.10, 6.40, ALTURA_PALCO + 0.55))
                @ Matrix.Diagonal((1.50, 0.95, 1.10, 1.0))))
    topo = face_mais_alta(bm)
    bmesh.ops.inset_region(bm, faces=[topo], thickness=0.10, depth=0.0,
                           use_even_offset=True, use_boundary=True)
    extrudar_face(bm, topo, Vector((0.0, 0.0, 0.06)))
    # faixa azul Ibmec aplicada na frente do pulpito
    faixa = bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((-3.10, 5.90, ALTURA_PALCO + 0.72))
                @ Matrix.Diagonal((1.20, 0.06, 0.30, 1.0))))
    verts_faixa = set(faixa["verts"])
    marcar_material([f for f in bm.faces
                     if all(v in verts_faixa for v in f.verts)], 1)
    gravar_bmesh(bm, pulpito)

    chanfro = pulpito.modifiers.new("MOD_Bevel_Pulpito", "BEVEL")
    chanfro.width = 0.02
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)

    # ---- mesa de apoio do globo ------------------------------------
    mesa = novo_objeto_malha("CEN_Mesa_Apoio", colecao, (mat_madeira,))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((4.20, 6.60, ALTURA_PALCO + 0.46))
                @ Matrix.Diagonal((1.70, 1.10, 0.09, 1.0))))
    for dx, dy in ((-0.70, -0.42), (0.70, -0.42), (-0.70, 0.42), (0.70, 0.42)):
        bmesh.ops.create_cube(
            bm, size=1.0,
            matrix=(Matrix.Translation((4.20 + dx, 6.60 + dy,
                                        ALTURA_PALCO + 0.21))
                    @ Matrix.Diagonal((0.09, 0.09, 0.42, 1.0))))
    gravar_bmesh(bm, mesa)

    # ---- luminarias do teto (dois Arrays encadeados) ---------------
    luminaria = novo_objeto_malha("CEN_Luminarias", colecao, (mat_luz,))
    bm = bmesh.new()
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((-7.00, 6.00, ALTURA_PE_DIREITO - 0.45))
                @ Matrix.Diagonal((2.60, 0.34, 0.10, 1.0))))
    gravar_bmesh(bm, luminaria)

    array_x = luminaria.modifiers.new("MOD_Array_Luminarias_X", "ARRAY")
    array_x.count = 3
    array_x.use_relative_offset = False
    array_x.use_constant_offset = True
    array_x.constant_offset_displace = (7.00, 0.0, 0.0)

    array_y = luminaria.modifiers.new("MOD_Array_Luminarias_Y", "ARRAY")
    array_y.count = 5
    array_y.use_relative_offset = False
    array_y.use_constant_offset = True
    array_y.constant_offset_displace = (0.0, -4.20, 0.0)

    # ---- cadeiras (duplicatas vinculadas: uma malha, varios objetos) --
    cadeira = construir_cadeira(colecao, mat_azul, mat_metal)
    cadeiras = []
    for nivel in range(4):
        y = -1.95 - nivel * 3.20
        z = 0.44 + nivel * 0.44
        for indice, x in enumerate((-6.60, -2.20, 2.20, 6.60)):
            if nivel == 0 and indice == 0:
                atual = cadeira
            else:
                atual = cadeira.copy()      # duplicata vinculada: mesma malha
                colecao.objects.link(atual)
            atual.name = "CEN_Cadeira_%02d_%02d" % (nivel + 1, indice + 1)
            atual.location = (x, y, z)
            atual.rotation_euler = (0.0, 0.0, math.radians(180.0 + 3.0 * indice))
            cadeiras.append(atual)

    return {"piso": piso, "paredes": paredes, "painel": painel, "palco": palco,
            "degraus": degraus, "arquibancada": arquibancada,
            "bancadas": bancada, "pulpito": pulpito, "mesa": mesa,
            "luminarias": luminaria, "cadeiras": cadeiras}


def construir_cadeira(colecao, mat_estofado, mat_metal):
    """Cadeira da plateia: assento e encosto em cubos transformados, pe
    tubular e base em disco (revolucao/cone), com Bevel nas arestas."""
    obj = novo_objeto_malha("CEN_Cadeira_01_01", colecao,
                            (mat_estofado, mat_metal))
    bm = bmesh.new()

    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, 0.0, 0.46))
                @ Matrix.Diagonal((0.52, 0.50, 0.08, 1.0))))
    bmesh.ops.create_cube(
        bm, size=1.0,
        matrix=(Matrix.Translation((0.0, 0.24, 0.72))
                @ Matrix.Rotation(math.radians(-8.0), 4, "X")
                @ Matrix.Diagonal((0.52, 0.07, 0.46, 1.0))))

    pe = criar_cone(bm, 0.05, 0.05, 0.42, segmentos=10,
                    matriz=Matrix.Translation((0.0, 0.0, 0.21)))
    base = criar_cone(bm, 0.22, 0.22, 0.04, segmentos=12,
                      matriz=Matrix.Translation((0.0, 0.0, 0.02)))
    verts_metal = set(pe["verts"]) | set(base["verts"])
    marcar_material([f for f in bm.faces
                     if all(v in verts_metal for v in f.verts)], 1)

    gravar_bmesh(bm, obj)

    chanfro = obj.modifiers.new("MOD_Bevel_Cadeira", "BEVEL")
    chanfro.width = 0.015
    chanfro.segments = 2
    chanfro.limit_method = "ANGLE"
    chanfro.angle_limit = math.radians(50.0)
    return obj


# ===================================================================
# 6. CAMERA, STORYBOARD E TIMELINE
# ===================================================================

def nova_camera(nome, colecao, local, alvo, lente=35.0):
    dados = bpy.data.cameras.new("CAM_DATA_" + nome)
    dados.lens = lente
    dados.clip_end = 300.0
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
    alvo.location = (0.0, 8.40, 3.10)

    principal = nova_camera("CAM_Principal", colecao, (0.0, -7.20, 3.90),
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
        ("CAM_SB1_Sala_Antes_da_Aula", (-6.80, -9.40, 1.60),
         (-1.00, 6.20, 1.90), 40.0),
        ("CAM_SB2_Conhecimento_se_Abre", (-4.20, 3.20, 2.60),
         (-2.60, 7.10, 2.10), 50.0),
        ("CAM_SB3_Assinatura_Ibmec", (0.00, -4.60, 3.30),
         (0.00, 9.20, 3.10), 42.0),
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
        ("SB1_Sala_Antes_da_Aula", 1),
        ("SB2_Conhecimento_se_Abre", 121),
        ("SB3_Assinatura_Ibmec", 241),
        ("Fim_15s", FRAME_FINAL),
    ]
    for nome, frame in momentos:
        cena.timeline_markers.new(nome, frame=frame)

    cena.frame_set(300)
    return momentos


def criar_luz(colecao):
    """Luz principal da sala (a iluminacao definitiva fica para a AP2)."""
    dados = bpy.data.lights.new("LUZ_DATA_Area", type="AREA")
    dados.energy = 900.0
    dados.size = 9.0
    luz = bpy.data.objects.new("LUZ_Teto_Sala", dados)
    colecao.objects.link(luz)
    luz.location = (0.0, 3.00, ALTURA_PE_DIREITO - 0.60)
    luz.rotation_euler = (math.radians(12.0), 0.0, 0.0)
    return luz


# ===================================================================
# 7. MONTAGEM DA CENA
# ===================================================================

def main():
    if bpy.app.version < (4, 5, 0):
        print("[AP1-EDU] AVISO: este projeto foi escrito para o Blender 4.5 LTS "
              "(versao atual: %d.%d.%d)." % bpy.app.version)

    limpar_cena()

    cena = bpy.context.scene
    raiz = nova_colecao(COLECAO_RAIZ, cena.collection)
    col_palavra = nova_colecao("01_Palavra_Ibmec", raiz)
    col_objetos = nova_colecao("02_Objetos_Autorais", raiz)
    col_cenario = nova_colecao("03_Cenario_Sala_de_Aula", raiz)
    col_camera = nova_colecao("04_Camera_e_Auxiliares", raiz)

    # ---- materiais -------------------------------------------------
    mat_azul = obter_material("MAT_Ibmec_Azul", HEX_AZUL_IBMEC, 0.38,
                              apelidos=("Azul Ibmec",))
    mat_amarelo = obter_material("MAT_Ibmec_Amarelo", HEX_AMARELO_IBMEC, 0.35,
                                 apelidos=("Amarelo Ibmec",))
    materiais = {
        "azul": mat_azul,
        "amarelo": mat_amarelo,
        "piso": obter_material("MAT_Piso_Sala", "B9B2A6", 0.72),
        "parede": obter_material("MAT_Parede_Sala", "EDEAE3", 0.78),
        "painel": obter_material("MAT_Painel_Frontal", "1C2430", 0.52),
        "madeira": obter_material("MAT_Madeira_Mobiliario", "A97C4F", 0.70),
        "metal": obter_material("MAT_Metal_Escovado", "9AA0A6", 0.34, 0.85),
        "papel": obter_material("MAT_Papel_Livro", "F4F1E8", 0.84),
        "tecido": obter_material("MAT_Tecido_Capelo", "23272E", 0.86),
        "luz": obter_material("MAT_Luminaria", "FFF3CF", 0.28),
    }

    # ---- palavra ---------------------------------------------------
    pivo, letras = construir_palavra(col_palavra, mat_azul, mat_amarelo)

    # ---- objetos autorais ------------------------------------------
    livro, _capa, _marcador = construir_livro(col_objetos, materiais["papel"],
                                              mat_azul, mat_amarelo)
    livro.location = (-3.10, 6.36, ALTURA_PALCO + 1.16)
    livro.rotation_euler = (math.radians(-14.0), 0.0, math.radians(4.0))
    livro.scale = (1.05, 1.05, 1.05)

    globo, _aneis = construir_globo(col_objetos, materiais["metal"],
                                    mat_azul, mat_amarelo)
    globo.location = (4.20, 6.60, ALTURA_PALCO + 0.50)
    globo.rotation_euler = (0.0, 0.0, math.radians(-22.0))
    globo.scale = (0.92, 0.92, 0.92)

    capelo, _cordao = construir_capelo(col_objetos, materiais["tecido"],
                                       mat_azul, mat_amarelo)
    capelo.location = (0.40, 5.20, ALTURA_PALCO + 0.06)
    capelo.rotation_euler = (0.0, 0.0, math.radians(18.0))
    capelo.scale = (1.15, 1.15, 1.15)

    # ---- cenario e camera ------------------------------------------
    construir_cenario(col_cenario, materiais)
    criar_luz(col_camera)
    principal, alvo, cameras_sb = configurar_cameras(col_camera, pivo)
    momentos = configurar_timeline()

    # ---- relatorio no console --------------------------------------
    print("")
    print("=" * 62)
    print("AP1 - 'A Sala que Abre o Mundo' | Ibmec (cenario: EDUCACAO)")
    print("=" * 62)
    print("Colecao principal ....: %s" % COLECAO_RAIZ)
    print("Palavra ..............: %d objetos (letras + ponto do i)" % len(letras))
    print("Objetos autorais .....: %s | %s | %s"
          % (livro.name, globo.name, capelo.name))
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
        print("[AP1-EDU] Arquivo salvo em %s" % CAMINHO_BLEND)


main()
