"""
AC04 - Evolucao da Cena: Modelos de Iluminacao
Executa os scripts da AC04 em sequencia, na mesma sessao do Blender:

    01_continuidade_ap1.py  copia AP1 -> AC4/AC04_IgorMariano.blend
    02_iluminacao.py        Atividade 1: luz principal, preenchimento, EEVEE
    03_materiais.py         Atividade 2: MAT_Lambert, MAT_Phong, MAT_BlinnPhong
    04_render_final.py      imagem final e .blend salvo

A etapa 3 da atividade (comparar e observar, girar a luz) e feita na
interface do Blender e nao faz parte desta automacao.

Como usar (sem abrir a interface), a partir da raiz do repositorio:
    blender -b AP1/AP1_IgorRodrigues.blend --python AC4/scripts/executar_ac04.py
Ou abra AP1_IgorRodrigues.blend no Blender 4.5 LTS, aba Scripting, abra este
arquivo e execute (Alt+P).
"""

import os
import runpy

import bpy

ETAPAS = (
    "01_continuidade_ap1.py",
    "02_iluminacao.py",
    "03_materiais.py",
    "04_render_final.py",
)


def pasta_dos_scripts():
    """Pasta deste arquivo, inclusive quando executado pelo editor de texto."""
    candidatas = []
    if "__file__" in globals():
        candidatas.append(os.path.dirname(os.path.abspath(__file__)))
    texto = bpy.context.space_data.text if getattr(bpy.context, "space_data", None) and \
        bpy.context.space_data.type == "TEXT_EDITOR" else None
    if texto and texto.filepath:
        candidatas.append(os.path.dirname(bpy.path.abspath(texto.filepath)))
    if bpy.data.filepath:
        pasta_blend = os.path.dirname(bpy.data.filepath)
        candidatas.append(os.path.join(pasta_blend, "scripts"))
        candidatas.append(os.path.join(os.path.dirname(pasta_blend), "AC4", "scripts"))
    for pasta in candidatas:
        if all(os.path.isfile(os.path.join(pasta, etapa)) for etapa in ETAPAS):
            return pasta
    raise RuntimeError("Pasta AC4/scripts nao encontrada.")


pasta = pasta_dos_scripts()
for etapa in ETAPAS:
    print("== AC04 ==", etapa)
    runpy.run_path(os.path.join(pasta, etapa), run_name="__main__")
print("AC04_CONCLUIDA", bpy.data.filepath)
