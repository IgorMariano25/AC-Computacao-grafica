"""Blender 4.5 LTS — importa o auditório numa NOVA cena e adiciona câmeras/luzes.
Abra no espaço Scripting > Text Editor > Open > Run Script (Alt+P).
Escolha Auditorio_AP1.glb. A cena anterior fica preservada.
"""
import bpy
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty


def preparar(filepath):
    cena = bpy.data.scenes.new('Auditorio AP1 | Referencia fotografica')
    bpy.context.window.scene = cena
    cena.unit_settings.system = 'METRIC'
    cena.unit_settings.scale_length = 1.0
    bpy.ops.import_scene.gltf(filepath=filepath)
    grupos = {}
    imported = list(cena.objects)
    for ob in imported:
        pai = ob
        grupo = '00_Origem'
        while pai:
            if len(pai.name) > 3 and pai.name[:2].isdigit() and pai.name[2] == '_':
                grupo = pai.name.split('.')[0]
                break
            pai = pai.parent
        if grupo not in grupos:
            col = bpy.data.collections.new(grupo)
            cena.collection.children.link(col)
            grupos[grupo] = col
        for col in list(ob.users_collection):
            col.objects.unlink(ob)
        grupos[grupo].objects.link(ob)
    extras = bpy.data.collections.new('10_Cameras_e_luzes')
    cena.collection.children.link(extras)

    def camera(nome, pos, alvo, lente):
        dados = bpy.data.cameras.new(nome)
        dados.lens = lente
        dados.clip_end = 150
        obj = bpy.data.objects.new(nome, dados)
        extras.objects.link(obj)
        obj.location = pos
        obj.rotation_euler = (Vector(alvo) - obj.location).to_track_quat('-Z', 'Y').to_euler()
        return obj

    cena.camera = camera('Camera_01_Palco', (0, 12.4, 2.65), (0, 1.1, 1.8), 22)
    camera('Camera_02_Plateia', (0, 2.8, 2.35), (0, 14.1, 2.0), 21)
    camera('Camera_03_Pulpito', (4.5, 4.0, 2.15), (3.2, 1.95, 1.2), 50)
    corte = camera('Camera_04_Corte', (24, 32, 25), (0, 10, 1.4), 40)
    corte.data.type = 'ORTHO'
    corte.data.ortho_scale = 29
    for y in (2.0, 6.0, 10.0, 14.0, 18.0):
        for x in (-3.6, 3.6):
            dados = bpy.data.lights.new(f'Luz_{x}_{y}', 'AREA')
            dados.energy = 420
            dados.shape = 'DISK'
            dados.size = 3.0
            obj = bpy.data.objects.new(dados.name, dados)
            extras.objects.link(obj)
            obj.location = (x, y, 4.04)
    mundo = bpy.data.worlds.new('Ambiente AP1')
    mundo.use_nodes = True
    mundo.node_tree.nodes['Background'].inputs['Color'].default_value = (0.78, 0.83, 1.0, 1)
    mundo.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.2
    cena.world = mundo
    cena.render.engine = 'CYCLES'
    cena.cycles.samples = 48
    cena.cycles.use_denoising = True
    cena.render.resolution_x = 1600
    cena.render.resolution_y = 1000
    cena.render.resolution_percentage = 100
    cena.view_settings.view_transform = 'AgX'
    cena['Observacao'] = 'Reconstrucao aproximada por fotos. Medidas e numero de assentos estimados.'
    bpy.ops.object.select_all(action='DESELECT')
    for tela in bpy.data.screens:
        for area in tela.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.clip_end = 150
                area.spaces.active.shading.type = 'MATERIAL'
                area.spaces.active.region_3d.view_distance = 24
                area.spaces.active.region_3d.view_location = (0, 10, 1.2)
    print('Auditorio importado. Use NumPad 0 para camera; F12 para render; File > Save As para salvar .blend.')


class AP1_OT_importar(bpy.types.Operator, ImportHelper):
    bl_idname = 'import_scene.auditorio_ap1'
    bl_label = 'Importar e preparar Auditorio AP1'
    filename_ext = '.glb'
    filter_glob: StringProperty(default='*.glb', options={'HIDDEN'})

    def execute(self, context):
        preparar(self.filepath)
        self.report({'INFO'}, 'Auditorio preparado em uma nova cena. Salve como .blend.')
        return {'FINISHED'}


if __name__ == '__main__':
    anterior = getattr(bpy.types, 'AP1_OT_importar', None)
    if anterior:
        bpy.utils.unregister_class(anterior)
    bpy.utils.register_class(AP1_OT_importar)
    bpy.ops.import_scene.auditorio_ap1('INVOKE_DEFAULT')
