"""
AC04 - Evolucao da Cena: Modelos de Iluminacao
Script 01 - Continuidade da AP1

Recebe aberta a cena da AP1 (AP1/AP1_IgorRodrigues.blend) e a salva como
COPIA em AC4/AC04_IgorMariano.blend. O arquivo original da AP1 nunca e
sobrescrito: a partir deste script o arquivo aberto passa a ser a copia, e os
scripts 02, 03 e 04 se recusam a rodar em qualquer outro arquivo.

Na copia:
- confere se a estrutura da AP1 esta intacta (colecao AP1_Ibmec_Conceito,
  Marca_Ibmec, Camera_Principal e os tres objetos autorais);
- cria a colecao AC04_Iluminacao, dentro de AP1_Ibmec_Conceito, que recebe
  as luzes do script 02.

A composicao, a camera principal e a palavra Ibmec nao sao alteradas.

Como usar (sem abrir a interface), a partir da raiz do repositorio:
    blender -b AP1/AP1_IgorRodrigues.blend --python AC4/scripts/01_continuidade_ap1.py
Ou abra AP1_IgorRodrigues.blend no Blender 4.5 LTS, aba Scripting, abra este
arquivo e execute (Alt+P).
Para rodar as quatro etapas de uma vez, use executar_ac04.py.
"""

import os

import bpy

NOME_COPIA = "AC04_IgorMariano.blend"
COLECAO_RAIZ = "AP1_Ibmec_Conceito"
COLECAO_LUZES = "AC04_Iluminacao"
OBJETOS_AUTORAIS = (
    "Objeto_A_Pulpito_Pitch",
    "Objeto_B_Capelo_Formatura",
    "Objeto_C_Diploma_Ibmec",
)

# ---------------------------------------------------------------
# 1. Conferencia da cena de origem
# ---------------------------------------------------------------
arquivo_atual = bpy.data.filepath
if not arquivo_atual:
    raise RuntimeError("Abra AP1/AP1_IgorRodrigues.blend antes de executar este script.")

for nome in (COLECAO_RAIZ, "Marca", "Objetos_Autorais", "Cenario", "Camera_Luzes"):
    if nome not in bpy.data.collections:
        raise RuntimeError(f"Colecao '{nome}' da AP1 nao encontrada: este nao e o arquivo da AP1.")
for nome in OBJETOS_AUTORAIS + ("Marca_Ibmec", "Camera_Principal"):
    if nome not in bpy.data.objects:
        raise RuntimeError(f"Objeto '{nome}' da AP1 nao encontrado.")

# ---------------------------------------------------------------
# 2. Destino da copia
#    AP1/AP1_IgorRodrigues.blend -> AC4/AC04_IgorMariano.blend
# ---------------------------------------------------------------
if os.path.basename(arquivo_atual) == NOME_COPIA:
    destino = arquivo_atual  # reexecucao sobre a propria copia
else:
    raiz_repositorio = os.path.dirname(os.path.dirname(arquivo_atual))
    destino = os.path.join(raiz_repositorio, "AC4", NOME_COPIA)
os.makedirs(os.path.dirname(destino), exist_ok=True)

# ---------------------------------------------------------------
# 3. Organizacao no Outliner
#    AP1_Ibmec_Conceito
#    |- Marca / Objetos_Autorais / Cenario / Camera_Luzes   (AP1)
#    |- AC04_Iluminacao                                      (novo)
# ---------------------------------------------------------------
raiz = bpy.data.collections[COLECAO_RAIZ]
if COLECAO_LUZES not in bpy.data.collections:
    raiz.children.link(bpy.data.collections.new(COLECAO_LUZES))

bpy.context.scene["AC04_Origem"] = (
    "Copia de AP1/AP1_IgorRodrigues.blend; composicao, camera e marca preservadas."
)

# ---------------------------------------------------------------
# 4. Salvar como copia AC04
# ---------------------------------------------------------------
preferencias = bpy.context.preferences.filepaths
versoes_antes = preferencias.save_version
preferencias.save_version = 0  # sem AC04_IgorMariano.blend1 ao lado da copia
try:
    bpy.ops.wm.save_as_mainfile(filepath=destino, compress=True)
finally:
    preferencias.save_version = versoes_antes

print("AC04_01_OK", bpy.data.filepath)
