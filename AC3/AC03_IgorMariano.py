"""
AC03 - Transformacoes Geometricas 2D e 3D no Blender 4.5 LTS
Cena: "Parque Geometrico"

Este script cria a colecao AC03_transformacoes, adiciona os objetos
2D (quadrado, triangulo, circulo) e 3D (cubo, cilindro, esfera),
aplica transformacoes de translacao, rotacao e escala nos eixos
X, Y e Z, e insere keyframes de animacao para um objeto 2D e um
objeto 3D ao longo da timeline (frame 1 ao 120, 24 fps).

Bonus incluidos: hierarquia parent/child (transformacao composta) e
easing + keyframe intermediario na animacao.

Como usar:
1. Abra o Blender 4.5 LTS.
2. Va em Scripting > Open > selecione este arquivo.
3. Execute o script (Run Script / Alt+P).
"""

import bpy
import math

FRAME_INICIAL = 1
FRAME_MEIO = 60
FRAME_FINAL = 120

# ---------------------------------------------------------------
# 1. Configuracao da cena / timeline
# ---------------------------------------------------------------
scene = bpy.context.scene
scene.render.fps = 24
scene.frame_start = FRAME_INICIAL
scene.frame_end = FRAME_FINAL

# ---------------------------------------------------------------
# 2. Criacao da colecao AC03_transformacoes
# ---------------------------------------------------------------
COLECAO_NOME = "AC03_transformacoes"

# Reexecutar o script nao deve duplicar os objetos (obj2d_quadrado.001 etc.)
if COLECAO_NOME in bpy.data.collections:
    colecao = bpy.data.collections[COLECAO_NOME]
    for obj in list(colecao.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
else:
    colecao = bpy.data.collections.new(COLECAO_NOME)
    scene.collection.children.link(colecao)


def mover_para_colecao(obj):
    """Move o objeto para a colecao AC03, removendo-o das demais."""
    for c in obj.users_collection:
        c.objects.unlink(obj)
    colecao.objects.link(obj)


# ---------------------------------------------------------------
# 3. Objetos 2D (plano XY)
#    Translacao em X/Y, rotacao em Z, escala em X/Y.
# ---------------------------------------------------------------

# 3.1 Quadrado (Plane)
bpy.ops.mesh.primitive_plane_add(size=1.5, location=(-4, -2, 0))
quadrado = bpy.context.active_object
quadrado.name = "obj2d_quadrado"
quadrado.rotation_euler = (0, 0, math.radians(30))
quadrado.scale = (1.4, 0.9, 1.0)
mover_para_colecao(quadrado)

# 3.2 Triangulo (Plane editado para 3 vertices)
bpy.ops.mesh.primitive_plane_add(size=1.5, location=(-2, -2, 0))
triangulo = bpy.context.active_object
triangulo.name = "obj2d_triangulo"

# dissolve_verts so remove vertices se o modo de selecao for por vertice
bpy.context.tool_settings.mesh_select_mode = (True, False, False)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='DESELECT')
bpy.ops.object.mode_set(mode='OBJECT')
triangulo.data.vertices[0].select = True
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.dissolve_verts()
bpy.ops.object.mode_set(mode='OBJECT')

triangulo.rotation_euler = (0, 0, math.radians(45))
triangulo.scale = (1.2, 1.2, 1.0)
mover_para_colecao(triangulo)

# 3.3 Circulo (Mesh Circle)
bpy.ops.mesh.primitive_circle_add(radius=0.9, fill_type='NGON', location=(0, -2, 0))
circulo = bpy.context.active_object
circulo.name = "obj2d_circulo"
circulo.rotation_euler = (0, 0, math.radians(15))
circulo.scale = (1.3, 1.3, 1.0)
mover_para_colecao(circulo)

# ---------------------------------------------------------------
# 4. Objetos 3D
#    Translacao em X/Y/Z, rotacao em X/Y/Z, escala em X/Y/Z.
# ---------------------------------------------------------------

# 4.1 Cubo
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4, 2, 1))
cubo = bpy.context.active_object
cubo.name = "obj3d_cubo"
cubo.rotation_euler = (math.radians(25), math.radians(15), math.radians(40))
cubo.scale = (1.2, 0.8, 1.5)
mover_para_colecao(cubo)

# 4.2 Cilindro
bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=1.5, location=(-1.5, 2, 1))
cilindro = bpy.context.active_object
cilindro.name = "obj3d_cilindro"
cilindro.rotation_euler = (math.radians(60), 0, math.radians(10))
cilindro.scale = (1.0, 1.0, 1.3)
mover_para_colecao(cilindro)

# 4.3 Esfera UV
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=(1.5, 2, 1.2))
esfera = bpy.context.active_object
esfera.name = "obj3d_esfera"
esfera.rotation_euler = (0, math.radians(35), math.radians(20))
esfera.scale = (1.0, 1.0, 0.8)
mover_para_colecao(esfera)

# ---------------------------------------------------------------
# 5. BONUS: hierarquia parent/child (transformacao composta)
#    O triangulo passa a ser filho do circulo, entao herda a
#    translacao e a rotacao animadas do circulo, somadas as suas.
# ---------------------------------------------------------------
triangulo.parent = circulo
triangulo.matrix_parent_inverse = circulo.matrix_world.inverted()

# ---------------------------------------------------------------
# 6. Animacao curta (keyframes) - 120 frames a 24 fps = 5 segundos
#    - Objeto 2D (circulo): translada em X e rotaciona em Z.
#    - Objeto 3D (cubo): escala e rotaciona em eixos diferentes.
# ---------------------------------------------------------------

# 6.1 Animacao do circulo (2D): translacao + rotacao
scene.frame_set(FRAME_INICIAL)
circulo.location = (0, -2, 0)
circulo.rotation_euler = (0, 0, math.radians(15))
circulo.keyframe_insert(data_path="location", frame=FRAME_INICIAL)
circulo.keyframe_insert(data_path="rotation_euler", frame=FRAME_INICIAL)

# BONUS: etapa intermediaria (o circulo sobe um pouco em Y no meio do caminho)
circulo.location = (1.25, -1.2, 0)
circulo.rotation_euler = (0, 0, math.radians(15 + 90))
circulo.keyframe_insert(data_path="location", frame=FRAME_MEIO)
circulo.keyframe_insert(data_path="rotation_euler", frame=FRAME_MEIO)

circulo.location = (2.5, -2, 0)
circulo.rotation_euler = (0, 0, math.radians(15 + 180))
circulo.keyframe_insert(data_path="location", frame=FRAME_FINAL)
circulo.keyframe_insert(data_path="rotation_euler", frame=FRAME_FINAL)

# 6.2 Animacao do cubo (3D): escala + rotacao em eixos diferentes (X, Y, Z)
scene.frame_set(FRAME_INICIAL)
cubo.rotation_euler = (math.radians(25), math.radians(15), math.radians(40))
cubo.scale = (1.2, 0.8, 1.5)
cubo.keyframe_insert(data_path="rotation_euler", frame=FRAME_INICIAL)
cubo.keyframe_insert(data_path="scale", frame=FRAME_INICIAL)

cubo.rotation_euler = (
    math.radians(25 + 90),
    math.radians(15 + 45),
    math.radians(40 + 180),
)
cubo.scale = (0.7, 1.6, 0.9)
cubo.keyframe_insert(data_path="rotation_euler", frame=FRAME_FINAL)
cubo.keyframe_insert(data_path="scale", frame=FRAME_FINAL)

# 6.3 BONUS: easing suave (aceleracao/desaceleracao) nas curvas animadas
for obj in (circulo, cubo):
    for fcurve in obj.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.easing = 'EASE_IN_OUT'

# ---------------------------------------------------------------
# 7. Camera e luz, para permitir o render estatico da cena final
# ---------------------------------------------------------------
bpy.ops.object.camera_add(location=(0, -12, 7))
camera = bpy.context.active_object
camera.name = "AC03_camera"
camera.rotation_euler = (math.radians(65), 0, 0)
mover_para_colecao(camera)
scene.camera = camera

bpy.ops.object.light_add(type='SUN', location=(4, -6, 10))
luz = bpy.context.active_object
luz.name = "AC03_luz"
luz.rotation_euler = (math.radians(35), math.radians(15), 0)
luz.data.energy = 4.0
mover_para_colecao(luz)

# Retorna a timeline para o frame inicial
scene.frame_set(FRAME_INICIAL)

print("Cena 'Parque Geometrico' criada com sucesso na colecao AC03_transformacoes.")
