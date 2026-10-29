"""
AC04 - Evolucao da Cena: Modelos de Iluminacao
Script 04 - Imagem renderizada da cena final

Confere a cena montada pelos scripts 01-03, renderiza o enquadramento
principal da AP1 (Camera_Principal, 1920x1080, EEVEE) com a palavra Ibmec
legivel e os tres objetos autorais visiveis, e salva o .blend:

    AC4/AC04_IgorMariano_render_final.png
    AC4/AC04_IgorMariano.blend

Os scripts da AC04 ficam guardados dentro do .blend (editor de texto) e o
viewport abre na camera principal em modo Rendered.

Requer o arquivo AC04_IgorMariano.blend aberto (gerado pelo script 01).
"""

import os

import bpy

NOME_COPIA = "AC04_IgorMariano.blend"
IMAGEM_FINAL = "AC04_IgorMariano_render_final.png"
ATRIBUICAO = {
    "Objeto_A_Pulpito_Pitch": "MAT_Lambert",
    "Objeto_B_Capelo_Formatura": "MAT_Phong",
    "Objeto_C_Diploma_Ibmec": "MAT_BlinnPhong",
}
SCRIPTS = (
    "01_continuidade_ap1.py",
    "02_iluminacao.py",
    "03_materiais.py",
    "04_render_final.py",
    "executar_ac04.py",
)

if os.path.basename(bpy.data.filepath) != NOME_COPIA:
    raise RuntimeError(f"Abra {NOME_COPIA} (gerado pelo script 01) antes de executar.")

cena = bpy.context.scene
pasta_ac4 = os.path.dirname(bpy.data.filepath)

# ---------------------------------------------------------------
# 1. Conferencias antes do render
# ---------------------------------------------------------------
for nome_obj, nome_mat in ATRIBUICAO.items():
    materiais = [m.name for m in bpy.data.objects[nome_obj].data.materials]
    assert materiais == [nome_mat], f"{nome_obj} deveria usar {nome_mat}, usa {materiais}"
marca = [m.name for m in bpy.data.objects["Marca_Ibmec"].data.materials]
assert marca == ["AP1_Cinza_Claro_Marca"], "a palavra Ibmec deve manter o material da AP1"
luzes = sorted(o.name for o in bpy.data.collections["AC04_Iluminacao"].objects)
assert luzes == ["Luz_Preenchimento_Area", "Luz_Principal_Area"], luzes
assert cena.render.engine == "BLENDER_EEVEE_NEXT"

# ---------------------------------------------------------------
# 2. Render do enquadramento principal
# ---------------------------------------------------------------
cena.camera = bpy.data.objects["Camera_Principal"]
cena.frame_set(1)
cena.render.resolution_x = 1920
cena.render.resolution_y = 1080
cena.render.resolution_percentage = 100
cena.render.image_settings.file_format = "PNG"
cena.render.image_settings.color_mode = "RGB"
cena.render.film_transparent = False
cena.render.filepath = os.path.join(pasta_ac4, IMAGEM_FINAL)
bpy.ops.render.render(write_still=True)
cena.render.filepath = "//" + IMAGEM_FINAL

# ---------------------------------------------------------------
# 3. Scripts e leia-me guardados no .blend
# ---------------------------------------------------------------
pasta_scripts = os.path.join(pasta_ac4, "scripts")
for nome in SCRIPTS:
    caminho = os.path.join(pasta_scripts, nome)
    if not os.path.isfile(caminho):
        continue
    texto = bpy.data.texts.get(nome) or bpy.data.texts.new(nome)
    texto.clear()
    with open(caminho, encoding="utf-8") as arquivo:
        texto.write(arquivo.read())

leia_me = bpy.data.texts.get("LEIA-ME_AC04") or bpy.data.texts.new("LEIA-ME_AC04")
leia_me.clear()
leia_me.write(
    "AC04 - Igor Mariano - Modelos de Iluminacao\n"
    "Copia da cena da AP1 (AP1_IgorRodrigues.blend nao foi alterado).\n"
    "Objeto_A_Pulpito_Pitch -> MAT_Lambert | Objeto_B_Capelo_Formatura -> MAT_Phong | "
    "Objeto_C_Diploma_Ibmec -> MAT_BlinnPhong\n"
    "Luzes na colecao AC04_Iluminacao; as luzes da AP1 ficam desativadas.\n"
    "Render: EEVEE, Camera_Principal (Numpad 0), F12.\n"
)

# ---------------------------------------------------------------
# 4. Viewport na camera principal em modo Rendered
# ---------------------------------------------------------------
for tela in bpy.data.screens:
    for area in tela.areas:
        if area.type == "VIEW_3D":
            espaco = area.spaces.active
            espaco.region_3d.view_perspective = "CAMERA"
            espaco.shading.type = "RENDERED"

# ---------------------------------------------------------------
# 5. Salvar
# ---------------------------------------------------------------
preferencias = bpy.context.preferences.filepaths
versoes_antes = preferencias.save_version
preferencias.save_version = 0
try:
    bpy.ops.wm.save_mainfile(compress=True)
finally:
    preferencias.save_version = versoes_antes

print("AC04_04_OK", os.path.join(pasta_ac4, IMAGEM_FINAL))
