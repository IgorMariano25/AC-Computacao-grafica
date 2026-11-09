"""Blender 4.5: copia a AC4, configura PBR/UVs, empacota e opcionalmente renderiza.
blender -b --python scripts/preparar_ac5.py -- --render
Nunca salva em AP1 ou AC4. Sem --render apenas prepara a cópia AC5.
"""
from pathlib import Path
import sys, json, math, hashlib
import bpy

ROOT = Path(__file__).resolve().parents[1]
# Prefere a cópia local; em um clone do Git usa a AC4 já versionada.
SOURCE = ROOT/'base_AC4'/'AC04_IgorMariano.blend'
if not SOURCE.is_file():
    SOURCE = ROOT.parent/'AC4'/'AC04_IgorMariano.blend'
OUTPUT = ROOT/'AC05_IgorMariano.blend'
OBJECTS = ['Objeto_A_Pulpito_Pitch','Objeto_B_Capelo_Formatura','Objeto_C_Diploma_Ibmec']

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path, data): path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4

def uv_project(obj):
    # Operação na malha copiada; escala aplicada à geometria apenas temporariamente
    # para que a projeção considere dimensões reais, sem alterar a geometria final.
    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    mesh = obj.data
    old = [v.co.copy() for v in mesh.vertices]
    scale = obj.matrix_world.to_scale()
    for v in mesh.vertices:
        v.co.x *= abs(scale.x); v.co.y *= abs(scale.y); v.co.z *= abs(scale.z)
    layer = mesh.uv_layers.get('UV_AC05') or mesh.uv_layers.new(name='UV_AC05')
    mesh.uv_layers.active = layer
    layer.active_render = True
    try:
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.025,area_weight=0,correct_aspect=True,scale_to_bounds=True)
    finally:
        if obj.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
        for v, co in zip(mesh.vertices, old): v.co = co
        mesh.update()
    return layer

def material(name, prefix, metallic, roughness, strength):
    mat=bpy.data.materials.new(name); mat.use_nodes=True
    nodes=mat.node_tree.nodes; links=mat.node_tree.links; nodes.clear()
    bs=nodes.new('ShaderNodeBsdfPrincipled'); bs.location=(400,180); bs.width=270
    bs.inputs['Metallic'].default_value=metallic
    bs.inputs['Roughness'].default_value=roughness
    bs.inputs['IOR'].default_value=1.5
    bs.inputs['Base Color'].default_value=(*[linear(.92)]*3,1)
    if prefix=='tecido':
        bs.inputs['Sheen Weight'].default_value=.20
        bs.inputs['Sheen Roughness'].default_value=.70
    out=nodes.new('ShaderNodeOutputMaterial'); out.location=(760,180)
    links.new(bs.outputs['BSDF'],out.inputs['Surface'])
    if prefix:
        uv=nodes.new('ShaderNodeUVMap'); uv.uv_map='UV_AC05'; uv.location=(-900,180)
        for channel,y in [('BaseColor',440),('Roughness',100),('Normal',-240)]:
            tex=nodes.new('ShaderNodeTexImage'); tex.location=(-550,y); tex.width=260
            tex.label=channel+' | '+('sRGB' if channel=='BaseColor' else 'Non-Color')
            im=bpy.data.images.load(str(ROOT/'texturas'/f'{prefix}_{channel}.png'),check_existing=True)
            im.colorspace_settings.name='sRGB' if channel=='BaseColor' else 'Non-Color'
            im.pack(); im.filepath=f'//texturas/{prefix}_{channel}.png'; tex.image=im
            links.new(uv.outputs['UV'],tex.inputs['Vector'])
            if channel=='Normal':
                normal=nodes.new('ShaderNodeNormalMap'); normal.location=(0,-180); normal.uv_map='UV_AC05'
                normal.inputs['Strength'].default_value=strength
                links.new(tex.outputs['Color'],normal.inputs['Color']); links.new(normal.outputs['Normal'],bs.inputs['Normal'])
            else: links.new(tex.outputs['Color'],bs.inputs['Base Color' if channel=='BaseColor' else 'Roughness'])
            if channel=='BaseColor': nodes.active=tex
    return mat

def main():
    if bpy.app.version[:2]!=(4,5): raise RuntimeError('Requer Blender 4.5 LTS')
    if OUTPUT.exists(): raise FileExistsError('A saída já existe; preserve-a antes de executar novamente.')
    original_sha=sha(SOURCE)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),use_scripts=False)
    scene=bpy.context.scene
    for name in OBJECTS+['Marca_Ibmec','Camera_Principal']:
        if name not in scene.objects: raise RuntimeError('Objeto ausente: '+name)
    scene.camera=bpy.data.objects['Camera_Principal']
    matrices={o.name:[list(row) for row in o.matrix_world] for o in scene.objects}
    geometry={o.name:[tuple(v.co) for v in o.data.vertices] for o in scene.objects if o.type=='MESH'}
    lighting=[{'nome':o.name,'energia':o.data.energy,'tipo':o.data.type,'cor':list(o.data.color),'matriz':[list(r) for r in o.matrix_world],'hide_render':o.hide_render} for o in scene.objects if o.type=='LIGHT']
    configs=[('MAT_Madeira_Nogueira_PBR','madeira',0,.48,.25),('MAT_Tecido_Preto_PBR','tecido',0,.80,.18),('MAT_Metal_Espelhado_PBR',None,1,.025,0)]
    record=[]
    for name,cfg in zip(OBJECTS,configs):
        obj=bpy.data.objects[name]; obj.data=obj.data.copy()
        if cfg[1]: uv_project(obj)
        mat=material(*cfg); obj.data.materials.clear(); obj.data.materials.append(mat)
        for p in obj.data.polygons: p.material_index=0
        obj['AC05_material']=mat.name
        if cfg[1]:
            uv=obj.data.uv_layers['UV_AC05']
            coords=[[float(d.uv.x),float(d.uv.y)] for d in uv.data]
            if not all(math.isfinite(c) and -.001<=c<=1.001 for p in coords for c in p): raise RuntimeError('UV inválida')
            dump(ROOT/'imagens'/f'{name}_UV.json',{'objeto':name,'metodo':'Smart UV Project 66 graus, margem .025, escala real temporária','uv':coords,'faces':[list(p.loop_indices) for p in obj.data.polygons]})
        record.append({'objeto':name,'material':mat.name,'metallic':cfg[2],'roughness_nominal':cfg[3],'normal_strength':cfg[4],'mapas':cfg[1]})
    # Marca: cópia dos materiais existentes, sem mudar cores, ligações ou geometria.
    brand=bpy.data.objects['Marca_Ibmec']; brand.data=brand.data.copy()
    for i,slot in enumerate(brand.material_slots):
        if slot.material:
            copied=slot.material.copy(); copied.name='MAT_Ibmec_Preservado_'+str(i); brand.data.materials[i]=copied
    for o in scene.objects:
        if matrices[o.name]!=[list(r) for r in o.matrix_world]: raise RuntimeError('Transformação alterada: '+o.name)
        if o.type=='MESH' and geometry[o.name]!=[tuple(v.co) for v in o.data.vertices]: raise RuntimeError('Geometria alterada: '+o.name)
    # Cycles é usado para reflexos do espelho; câmera, luzes e World da AC4 mantidos.
    scene.render.engine='CYCLES'; scene.cycles.device='CPU'; scene.cycles.samples=64
    scene.cycles.use_denoising=True; scene.cycles.use_adaptive_sampling=True
    scene.render.resolution_x=1920; scene.render.resolution_y=1080; scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'; scene.render.filepath='//imagens/AC05_render_final.png'
    bpy.ops.object.select_all(action='DESELECT'); obj=bpy.data.objects[OBJECTS[0]]; obj.select_set(True); bpy.context.view_layer.objects.active=obj
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT),compress=True)
    report={'blender':bpy.app.version_string,'origem_sha256':original_sha,'materiais':record,'luzes_preservadas':lighting,'geometria_e_transformacoes_preservadas':True,'motor':'Cycles CPU 64 amostras','render_executado':False}
    dump(ROOT/'configuracao_ac5.json',report)
    if '--render' in sys.argv:
        bpy.ops.render.render(write_still=True)
        report['render_executado']=True
        dump(ROOT/'configuracao_ac5.json',report)
    assert sha(SOURCE)==original_sha

if __name__=='__main__': main()
