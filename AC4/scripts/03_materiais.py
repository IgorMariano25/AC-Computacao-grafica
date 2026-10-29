"""
AC04 - Evolucao da Cena: Modelos de Iluminacao
Script 03 - Atividade 2: criar e aplicar os tres materiais

Cria MAT_Lambert, MAT_Phong e MAT_BlinnPhong como aproximacoes no
Principled BSDF, com os valores das praticas da aula 11 (2.1 Lambert,
2.2 Phong, 2.3 Blinn-Phong), e aplica um modelo diferente a cada objeto
autoral da AP1:

    Objeto_A_Pulpito_Pitch     -> MAT_Lambert     (azul medio)
    Objeto_B_Capelo_Formatura  -> MAT_Phong       (vermelho)
    Objeto_C_Diploma_Ibmec     -> MAT_BlinnPhong  (verde)

| Material       | Roughness | Specular IOR Level | Comportamento esperado          |
|----------------|-----------|--------------------|---------------------------------|
| MAT_Lambert    | 1.0       | 0.0                | so difusa, I = kd (N.L)         |
| MAT_Phong      | 0.2       | 0.5                | difusa + especular concentrado  |
| MAT_BlinnPhong | 0.1       | 0.8                | difusa + especular mais intenso |

No Blender 4.5 o antigo campo "Specular" do Principled BSDF se chama
"Specular IOR Level" (0.5 = neutro, 0 = sem especular).

O MAT_Lambert tambem traz um no Diffuse BSDF (Lambert puro, Roughness 0),
desconectado, como alternativa direta indicada no enunciado; para usa-lo,
ligue-o ao Surface do Material Output ou troque LAMBERT_COM_DIFFUSE_BSDF.

Nota: o Principled BSDF e um shader fisico; as configuracoes "Phong" e
"Blinn-Phong" sao aproximacoes visuais, nao as equacoes classicas.

Como no passo "Shade Smooth" das praticas, as tres malhas recebem
sombreamento suave por angulo (30 graus): superficies curvas ficam lisas,
arestas vivas continuam vivas. A geometria da AP1 nao muda. A palavra
Ibmec mantem seu material da AP1 (AP1_Cinza_Claro_Marca).

Requer o arquivo AC04_IgorMariano.blend aberto (gerado pelo script 01).
"""

import math
import os

import bpy

NOME_COPIA = "AC04_IgorMariano.blend"
LAMBERT_COM_DIFFUSE_BSDF = False
ANGULO_SUAVIZACAO = math.radians(30)

MATERIAIS = {
    "MAT_Lambert": {
        "objeto": "Objeto_A_Pulpito_Pitch",
        "modelo": "Lambert - reflexao difusa",
        "cor_hex": "3366CC",  # azul medio
        "rugosidade": 1.0,
        "especular": 0.0,
    },
    "MAT_Phong": {
        "objeto": "Objeto_B_Capelo_Formatura",
        "modelo": "Phong - difusa + especular (vetor de reflexao R)",
        "cor_hex": "C0392B",  # vermelho
        "rugosidade": 0.2,
        "especular": 0.5,
    },
    "MAT_BlinnPhong": {
        "objeto": "Objeto_C_Diploma_Ibmec",
        "modelo": "Blinn-Phong - difusa + especular (vetor medio H)",
        "cor_hex": "2E9E4F",  # verde
        "rugosidade": 0.1,
        "especular": 0.8,
    },
}

if os.path.basename(bpy.data.filepath) != NOME_COPIA:
    raise RuntimeError(f"Abra {NOME_COPIA} (gerado pelo script 01) antes de executar.")


def hex_para_linear(cor_hex):
    """Converte '#RRGGBB' (sRGB) para RGBA linear, o espaco do Base Color."""
    rgba = []
    for i in (0, 2, 4):
        c = int(cor_hex[i:i + 2], 16) / 255
        rgba.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*rgba, 1.0)


def criar_material(nome, cfg):
    """Monta Principled BSDF -> Material Output (e Diffuse BSDF no Lambert)."""
    mat = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    mat.use_nodes = True
    nos = mat.node_tree.nodes
    ligacoes = mat.node_tree.links
    nos.clear()

    cor = hex_para_linear(cfg["cor_hex"])
    saida = nos.new("ShaderNodeOutputMaterial")
    saida.location = (400, 0)
    bsdf = nos.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    bsdf.inputs["Base Color"].default_value = cor
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = cfg["rugosidade"]
    bsdf.inputs["Specular IOR Level"].default_value = cfg["especular"]
    ligacoes.new(bsdf.outputs["BSDF"], saida.inputs["Surface"])

    if nome == "MAT_Lambert":
        difuso = nos.new("ShaderNodeBsdfDiffuse")
        difuso.location = (0, 300)
        difuso.label = "Alternativa: Diffuse BSDF (Lambert puro)"
        difuso.inputs["Color"].default_value = cor
        difuso.inputs["Roughness"].default_value = 0.0
        if LAMBERT_COM_DIFFUSE_BSDF:
            ligacoes.new(difuso.outputs["BSDF"], saida.inputs["Surface"])

    # Cores e brilho equivalentes para o modo Solid do viewport.
    mat.diffuse_color = cor
    mat.roughness = cfg["rugosidade"]
    mat.specular_intensity = cfg["especular"]
    mat.metallic = 0.0
    mat["AC04_modelo"] = cfg["modelo"]
    return mat


# ---------------------------------------------------------------
# 1. Criacao dos materiais e aplicacao nos objetos autorais
# ---------------------------------------------------------------
for nome, cfg in MATERIAIS.items():
    mat = criar_material(nome, cfg)
    obj = bpy.data.objects[cfg["objeto"]]
    malha = obj.data

    malha.materials.clear()
    malha.materials.append(mat)
    for face in malha.polygons:
        face.material_index = 0
    obj.color = mat.diffuse_color

    # ---------------------------------------------------------------
    # 2. Shade Smooth por angulo (sem alterar a geometria)
    # ---------------------------------------------------------------
    malha.shade_smooth()
    malha.set_sharp_from_angle(angle=ANGULO_SUAVIZACAO)

    obj["AC04_material"] = nome
    obj["AC04_modelo"] = cfg["modelo"]
    print(f"AC04_03 {obj.name} -> {nome} (R={cfg['rugosidade']}, IOR Level={cfg['especular']})")

print("AC04_03_OK")
