"""
AC04 - Evolucao da Cena: Modelos de Iluminacao
Script 02 - Atividade 1: preparar a iluminacao da cena

Configura uma iluminacao fixa, usada sem alteracao em todas as imagens:

- Luz_Principal_Area: luz Area pequena (disco de 1 m) a frente do palco,
  do lado do capelo e do diploma. Por ser pequena, gera brilho especular
  concentrado e sombras perceptiveis. Por estar fora do centro, cada objeto
  autoral a recebe em um angulo diferente: o pulpito de lado (pela direita
  da imagem), o capelo e o diploma quase de frente (pela esquerda).
  Ela fica abaixo do forro, a 3,2 m: com a luz mais baixa, o vetor medio
  entre a luz e a camera (H, o do Blinn-Phong) se aproxima das normais da
  copa do capelo e do canudo do diploma, e o brilho aparece para a camera.
  A abertura (spread) de 120 graus concentra a luz no palco.
- Luz_Preenchimento_Area: luz Area grande e fraca do lado oposto, so para
  que as sombras nao fiquem pretas.
- Ambiente (World) escuro e uniforme, para que o brilho visivel nos
  materiais venha das luzes da cena e nao de um ceu cinza.

A luz Sun foi descartada porque o auditorio da AP1 e fechado: o forro
(Forro_modular, z = 4,2 m) bloquearia a luz direcional. As tres luzes
neutras da AP1 continuam no arquivo (colecao Camera_Luzes), mas ficam
desativadas no viewport e no render para nao interferir na comparacao.

O motor passa de Workbench (AP1, apenas visualizacao) para EEVEE, que
calcula as componentes difusa e especular, e o gerenciamento de cor para
AgX, que comprime os brilhos sem estourar as areas claras.

Requer o arquivo AC04_IgorMariano.blend aberto (gerado pelo script 01).
"""

import math
import os

import bpy
from mathutils import Vector

NOME_COPIA = "AC04_IgorMariano.blend"
COLECAO_LUZES = "AC04_Iluminacao"
LUZES_AP1 = ("Luz_AP1_Suave", "Luz_AP1_Preenchimento", "Luz_AP1_Plateia")

# Valores fixos: posicao, potencia, tamanho e cor nao mudam entre as imagens.
LUZ_PRINCIPAL = {
    "nome": "Luz_Principal_Area",
    "local": (-2.5, 6.5, 3.2),    # m; forro a 4,2 m
    "alvo": (-1.5, 2.2, 1.3),     # entre o pulpito e a mesa, altura dos objetos
    "potencia": 300.0,            # W
    "tamanho": 1.0,               # m (disco)
    "abertura": 120.0,            # graus (spread)
    "cor": (1.0, 1.0, 1.0),       # branca
}
LUZ_PREENCHIMENTO = {
    "nome": "Luz_Preenchimento_Area",
    "local": (5.5, 9.0, 3.8),
    "alvo": (0.0, 2.0, 1.0),
    "potencia": 50.0,
    "tamanho": 4.0,
    "abertura": 180.0,
    "cor": (1.0, 1.0, 1.0),
}
AMBIENTE_COR = (0.05, 0.05, 0.05)
AMBIENTE_FORCA = 1.0

if os.path.basename(bpy.data.filepath) != NOME_COPIA:
    raise RuntimeError(f"Abra {NOME_COPIA} (gerado pelo script 01) antes de executar.")

cena = bpy.context.scene

# ---------------------------------------------------------------
# 1. Luzes da AP1: mantidas no arquivo, desativadas
# ---------------------------------------------------------------
for nome in LUZES_AP1:
    luz = bpy.data.objects.get(nome)
    if luz:
        luz.hide_render = True
        luz.hide_viewport = True

# ---------------------------------------------------------------
# 2. Luzes da AC04 na colecao AC04_Iluminacao
#    Reexecutar o script recria as luzes em vez de duplica-las.
# ---------------------------------------------------------------
colecao = bpy.data.collections[COLECAO_LUZES]
for obj in list(colecao.objects):
    dados = obj.data
    bpy.data.objects.remove(obj, do_unlink=True)
    if dados and dados.users == 0:
        bpy.data.lights.remove(dados)


def criar_luz_area(cfg):
    """Cria uma luz Area em disco apontada para cfg['alvo']."""
    dados = bpy.data.lights.new(cfg["nome"], "AREA")
    dados.shape = "DISK"
    dados.size = cfg["tamanho"]
    dados.energy = cfg["potencia"]
    dados.spread = math.radians(cfg["abertura"])
    dados.color = cfg["cor"]
    dados.use_shadow = True
    obj = bpy.data.objects.new(cfg["nome"], dados)
    colecao.objects.link(obj)
    obj.location = cfg["local"]
    direcao = Vector(cfg["alvo"]) - obj.location
    obj.rotation_euler = direcao.to_track_quat("-Z", "Y").to_euler()
    return obj


principal = criar_luz_area(LUZ_PRINCIPAL)
preenchimento = criar_luz_area(LUZ_PREENCHIMENTO)

# ---------------------------------------------------------------
# 3. Ambiente (World) escuro e uniforme
# ---------------------------------------------------------------
mundo = bpy.data.worlds.get("AC04_Ambiente") or bpy.data.worlds.new("AC04_Ambiente")
mundo.use_nodes = True
fundo = mundo.node_tree.nodes["Background"]
fundo.inputs["Color"].default_value = (*AMBIENTE_COR, 1.0)
fundo.inputs["Strength"].default_value = AMBIENTE_FORCA
mundo.color = AMBIENTE_COR
if cena.world and cena.world != mundo:
    cena.world.use_fake_user = True  # preserva o World da AP1 no arquivo
cena.world = mundo

# ---------------------------------------------------------------
# 4. Motor de render e gerenciamento de cor
# ---------------------------------------------------------------
cena.render.engine = "BLENDER_EEVEE_NEXT"
cena.eevee.taa_render_samples = 128
cena.eevee.taa_samples = 32
cena.eevee.use_shadows = True
cena.eevee.use_raytracing = True
cena.view_settings.view_transform = "AgX"
cena.view_settings.look = "None"
cena.view_settings.exposure = 0.0
cena.view_settings.gamma = 1.0

for chave, cfg in (("AC04_Luz_Principal", LUZ_PRINCIPAL), ("AC04_Luz_Preenchimento", LUZ_PREENCHIMENTO)):
    cena[chave] = (
        f"Area disco {cfg['tamanho']} m, {cfg['potencia']:.0f} W, spread {cfg['abertura']:.0f} graus, "
        f"branca, em {cfg['local']} apontada para {cfg['alvo']}"
    )

print("AC04_02_OK", principal.name, preenchimento.name)
