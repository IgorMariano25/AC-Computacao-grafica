"""AP2: acabamento pontual, exclusivamente na nuvem; NAO renderiza.

Preserva geometria, hierarquia, cameras, animacoes e marca da fonte.
As verificacoes de integridade e reabertura rodam no Blender da nuvem.
"""
import os
if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted':
    raise RuntimeError('Execute somente em GitHub Actions hospedado. Blender local proibido.')
import bpy
import hashlib
import json
import math
import platform
import struct
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'AP2/OFICIAL'
BASE = ROOT / 'AP2/V1/Fontes/Auditorio_AP2.blend'
FINAL = OUT / 'AP2_IgorMariano.blend'
BASE_SHA = 'd53dfa2612c6891293ffdd181b7fe78bbe4cd9e96d4e90c25a7ccd8a1a1135ae'
LOG = OUT / 'nuvem'
LOG.mkdir(parents=True, exist_ok=True)

def dump(name, value):
    (LOG/name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def linear(v):
    return v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4

def rgba(rgb):
    return (*[linear(x) for x in rgb], 1)

def curves(action):
    if not action:
        return []
    result = [f for layer in action.layers for strip in layer.strips
              for bag in getattr(strip, 'channelbags', []) for f in bag.fcurves]
    return result or list(action.fcurves)

def action_record():
    return {a.name: sorted([(f.data_path, f.array_index,
             [(tuple(k.co), tuple(k.handle_left), tuple(k.handle_right), k.interpolation,
               k.handle_left_type, k.handle_right_type) for k in f.keyframe_points])
             for f in curves(a)], key=repr) for a in bpy.data.actions}

def mesh_hash(mesh):
    h = hashlib.sha256()
    for v in mesh.vertices:
        h.update(struct.pack('<3f', *v.co))
    for p in mesh.polygons:
        h.update(struct.pack('<I', len(p.vertices)))
        h.update(struct.pack('<'+'I'*len(p.vertices), *p.vertices))
    if mesh.shape_keys:
        for key in mesh.shape_keys.key_blocks:
            h.update(key.name.encode())
            for p in key.data:
                h.update(struct.pack('<3f', *p.co))
    return h.hexdigest()

def geometry_record():
    result = {}
    for o in bpy.context.scene.objects:
        r = {'type': o.type, 'parent': o.parent.name if o.parent else None,
             'collections': sorted(c.name for c in o.users_collection),
             'hide_render': o.hide_render}
        if o.type == 'MESH':
            r['geometry'] = mesh_hash(o.data)
        elif o.type in ('CURVE', 'FONT'):
            r['geometry'] = repr([(sp.type, [(tuple(p.co),p.radius) for p in sp.points],
                                    [(tuple(p.co),tuple(p.handle_left),tuple(p.handle_right)) for p in sp.bezier_points]) for sp in o.data.splines])
        result[o.name] = r
    return result

def animation_samples(names):
    s = bpy.context.scene
    values = []
    for frame in range(1,361):
        s.frame_set(frame)
        values.append({'frame':frame,'camera':s.camera.name if s.camera else None,
            'objects': {name:[round(v,7) for row in s.objects[name].matrix_world for v in row] for name in names},
            'lenses':{o.name:round(o.data.lens,7) for o in s.objects if o.type=='CAMERA'},
            'shape_keys':{k.name:{b.name:round(b.value,7) for b in k.key_blocks} for k in bpy.data.shape_keys}})
    s.frame_set(1)
    return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()

def markers():
    return [(m.name,m.frame,m.camera.name if m.camera else None) for m in bpy.context.scene.timeline_markers]

def material(name, color, roughness, metal=0, spec=.3):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    n = m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value = rgba(color)
    n.inputs['Roughness'].default_value = roughness
    n.inputs['Metallic'].default_value = metal
    n.inputs['Specular IOR Level'].default_value = spec
    m.diffuse_color = rgba(color)
    m['modelo_didatico'] = 'Blinn-Phong: aproximacao visual PBR via Principled/GGX, nao equacao literal'
    return m, n

def image_node(m, prefix, channel, uv_name=None, box=False):
    path = OUT/'texturas'/f'{prefix}_{channel}.png'
    if not path.is_file():
        path = ROOT/'AC5/texturas'/f'{prefix}_{channel}.png'
    if not path.is_file():
        raise FileNotFoundError(path)
    im = bpy.data.images.load(str(path),check_existing=True)
    im.colorspace_settings.name = 'sRGB' if channel=='BaseColor' else 'Non-Color'
    im.pack()
    im.filepath = '//texturas/'+path.name
    node = m.node_tree.nodes.new('ShaderNodeTexImage')
    node.image = im
    node.label = 'AC05 '+channel+' (CC0)'
    if box:
        node.projection = 'BOX'
        node.projection_blend = .15
        coord = m.node_tree.nodes.get('Coordenadas_AC05')
        if coord is None:
            coord=m.node_tree.nodes.new('ShaderNodeTexCoord');coord.name='Coordenadas_AC05'
        m.node_tree.links.new(coord.outputs['Generated'],node.inputs['Vector'])
    else:
        uv=m.node_tree.nodes.get('UV_AC05')
        if uv is None:
            uv=m.node_tree.nodes.new('ShaderNodeUVMap');uv.name='UV_AC05';uv.uv_map=uv_name or 'UV_AC05'
        m.node_tree.links.new(uv.outputs['UV'],node.inputs['Vector'])
    return node

def ramp(m, source, low, high, position=(0,1)):
    n=m.node_tree.nodes.new('ShaderNodeValToRGB')
    n.color_ramp.elements[0].position=position[0]
    n.color_ramp.elements[0].color=low
    n.color_ramp.elements[1].position=position[1]
    n.color_ramp.elements[1].color=high
    m.node_tree.links.new(source,n.inputs['Fac'])
    return n.outputs['Color']

def micro_bump(m, shader, scale, distance, strength=.2):
    n=m.node_tree.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=scale
    n.inputs['Detail'].default_value=2
    coord=m.node_tree.nodes.new('ShaderNodeTexCoord')
    m.node_tree.links.new(coord.outputs['Generated'],n.inputs['Vector'])
    bump=m.node_tree.nodes.new('ShaderNodeBump')
    bump.inputs['Distance'].default_value=distance;bump.inputs['Strength'].default_value=strength
    m.node_tree.links.new(n.outputs['Fac'],bump.inputs['Height'])
    m.node_tree.links.new(bump.outputs['Normal'],shader.inputs['Normal'])
    return n

def cloth(name, low, high):
    m,n=material(name,low,.85,spec=.22)
    tex=image_node(m,'tecido','BaseColor',box=True)
    m.node_tree.links.new(ramp(m,tex.outputs['Color'],rgba(low),rgba(high),(.002,.012)),n.inputs['Base Color'])
    rough=image_node(m,'tecido','Roughness',box=True)
    m.node_tree.links.new(rough.outputs['Color'],n.inputs['Roughness'])
    n.inputs['Sheen Weight'].default_value=.10
    n.inputs['Sheen Roughness'].default_value=.85
    # Trama da AC05 reutilizada como altura: projecao tridimensional dispensa novas UVs.
    bump=m.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.00020
    bump.inputs['Strength'].default_value=.22
    m.node_tree.links.new(tex.outputs['Color'],bump.inputs['Height'])
    m.node_tree.links.new(bump.outputs['Normal'],n.inputs['Normal'])
    m['AC05_reuso']='BaseColor e Roughness; BaseColor tambem como microaltura; projecao box Generated'
    return m

def bounds(o):
    pts=[o.matrix_world@Vector(p) for p in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])

def finish_materials():
    blue=cloth('AP2OF_Tecido_Azul',(.045,.19,.32),(.07,.26,.42))
    oxford=cloth('AP2OF_Oxford_Preto',(.018,.020,.025),(.042,.045,.052))
    plastic,_=material('AP2OF_Plastico_Preto_Fosco',(.035,.038,.042),.63,spec=.32)
    iron,_=material('AP2OF_Ferro_Pintado_Preto',(.035,.038,.043),.46,metal=.15,spec=.4)
    wall,_=material('AP2OF_Parede_Branca_Fosca',(.86,.855,.84),.88,spec=.18)
    wood,n=material('AP2OF_Madeira_Preta_Pulpito',(.035,.032,.027),.6,spec=.3)
    tex=image_node(wood,'madeira','BaseColor',box=True)
    wood.node_tree.links.new(ramp(wood,tex.outputs['Color'],rgba((.023,.022,.020)),rgba((.075,.069,.058)),(.01,.3)),n.inputs['Base Color'])
    rough=image_node(wood,'madeira','Roughness',box=True)
    wood.node_tree.links.new(ramp(wood,rough.outputs['Color'],(.5,.5,.5,1),(.7,.7,.7,1)),n.inputs['Roughness'])
    bump=wood.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.00035
    wood.node_tree.links.new(tex.outputs['Color'],bump.inputs['Height']);wood.node_tree.links.new(bump.outputs['Normal'],n.inputs['Normal'])
    wood['AC05_reuso']='Madeira BaseColor dessaturada/escurecida e Roughness; relevo superficial via Bump'
    paper,n=material('AP2OF_Papel_Diploma',(.9,.885,.82),.9,spec=.15)
    noise=micro_bump(paper,n,220,.00009,.13)
    paper.node_tree.links.new(ramp(paper,noise.outputs['Fac'],rgba((.87,.855,.79)),rgba((.93,.917,.86))),n.inputs['Base Color'])
    paper['modelo_didatico']='Lambert difuso literal: Diffuse BSDF roughness 0 com pequena componente PBR'
    diffuse=paper.node_tree.nodes.new('ShaderNodeBsdfDiffuse');diffuse.label='Lambert: rugosidade 0'
    diffuse.inputs['Roughness'].default_value=0
    color_link=n.inputs['Base Color'].links[0].from_socket
    normal_link=n.inputs['Normal'].links[0].from_socket
    paper.node_tree.links.new(color_link,diffuse.inputs['Color']);paper.node_tree.links.new(normal_link,diffuse.inputs['Normal'])
    mix=paper.node_tree.nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=.08
    paper.node_tree.links.new(diffuse.outputs[0],mix.inputs[1]);paper.node_tree.links.new(n.outputs[0],mix.inputs[2])
    paper.node_tree.links.new(mix.outputs[0],paper.node_tree.nodes.get('Material Output').inputs['Surface'])
    changed=[]
    done=set()
    for o in bpy.context.scene.objects:
        if o.type not in ('MESH','CURVE','FONT') or not hasattr(o.data,'materials'):
            continue
        is_pulpito=o.name=='Objeto_A_Pulpito_Pitch' or o.name.startswith('Pulpito_curvo')
        # Malhas instanciadas mantem compartilhamento; pulpito recebe copia apenas dos slots.
        if is_pulpito:
            o.data=o.data.copy()
        key=o.data.as_pointer()
        if key in done:
            continue
        done.add(key)
        for i,old in enumerate(list(o.data.materials)):
            if old is None: continue
            name=old.name
            replacement=None
            if is_pulpito and name.startswith(('Plastico_antracite','Metal_preto','Madeira_mel')):
                replacement=wood
            elif name.startswith('Estofado_azul'): replacement=blue
            elif name.startswith('Plastico_antracite'): replacement=plastic
            elif name.startswith('Metal_preto'): replacement=iron
            elif name.startswith('Paredes_marfin'): replacement=wall
            elif name.startswith('AP2_Capelo_preto'): replacement=oxford
            elif name.startswith('AP2_Papel_diploma'): replacement=paper
            if replacement:
                o.data.materials[i]=replacement
                changed.append({'objeto':o.name,'slot':i,'antes':name,'depois':replacement.name})
        # O modelo original possui laterais em tecido e nao possui uma capa inferior separada.
        # Reatribui faces laterais e face inferior do assento sem alterar vertices.
        if o.type=='MESH' and o.name.startswith('Poltrona_'):
            plastic_index=next((i for i,m in enumerate(o.data.materials) if m==plastic),None)
            if plastic_index is None:
                o.data.materials.append(plastic);plastic_index=len(o.data.materials)-1
            count=0
            basis=o.matrix_world.to_3x3()
            normal_basis=basis.inverted().transposed()
            for p in o.data.polygons:
                mat=o.data.materials[p.material_index]
                if mat != blue: continue
                center=basis@p.center
                normal=(normal_basis@p.normal).normalized()
                # Altura relativa ao objeto no sistema global; a importacao converteu os eixos locais.
                if abs(center.x)>.252 or (.395<center.z<.425 and abs(center.x)<.252 and normal.z<-.65):
                    p.material_index=plastic_index;count+=1
            changed.append({'objeto':o.name,'faces_laterais_inferiores_plastico':count})
    required=[blue,plastic,iron,wall,wood,oxford,paper]
    for m in required:
        if m.users==0: raise RuntimeError('Material sem alvo: '+m.name)
    return changed

def light_collection():
    c=bpy.data.collections.new('14_AP2OF_Iluminacao')
    bpy.context.scene.collection.children.link(c)
    return c

def panel_patches():
    patches=[]
    for o in bpy.context.scene.objects:
        if o.type!='MESH': continue
        indices={i for i,m in enumerate(o.data.materials) if m and m.name.startswith('Difusor_luminaria')}
        if not indices: continue
        normals=o.matrix_world.to_3x3().inverted().transposed()
        polys=[p for p in o.data.polygons if p.material_index in indices and (normals@p.normal).normalized().z<-.7]
        groups=[]
        for p in polys:
            coords=[o.matrix_world@o.data.vertices[i].co for i in p.vertices]
            keys={tuple(round(c,5) for c in v) for v in coords}
            touching=[g for g in groups if g['keys']&keys]
            group={'keys':keys,'points':coords}
            for g in touching:
                group['keys'].update(g['keys']);group['points']+=g['points'];groups.remove(g)
            groups.append(group)
        for g in groups:
            lo=Vector([min(p[i] for p in g['points']) for i in range(3)])
            hi=Vector([max(p[i] for p in g['points']) for i in range(3)])
            if (hi.x-lo.x)*(hi.y-lo.y)>.05:
                patches.append((o.name,(lo+hi)/2,hi-lo))
    return patches

def finish_lighting():
    s=bpy.context.scene
    c=light_collection()
    records=[]
    for m in bpy.data.materials:
        if not m.name.startswith('Difusor_luminaria') or not m.use_nodes: continue
        for n in m.node_tree.nodes:
            if n.type=='BSDF_PRINCIPLED':
                n.inputs['Emission Color'].default_value=(.94,.97,1,1)
                n.inputs['Emission Strength'].default_value=3
    patches=panel_patches()
    if not patches:
        raise RuntimeError('Nao foi possivel localizar as faces inferiores das luminarias existentes.')
    for i,(source,center,dim) in enumerate(patches,1):
        data=bpy.data.lights.new(f'AP2OF_Painel_{i:02}','AREA');data.shape='RECTANGLE'
        data.energy=45;data.color=(.92,.96,1);data.size=max(.1,dim.x);data.size_y=max(.1,dim.y)
        o=bpy.data.objects.new(data.name,data);c.objects.link(o)
        o.location=center+Vector((0,0,-.055))
        o['origem_luminaria']=source
        records.append({'nome':o.name,'tipo':data.type,'watts':data.energy,'posicao':list(o.location),'dimensoes':[data.size,data.size_y]})
    ceiling=s.objects.get('Forro_modular')
    walls=s.objects.get('Paredes_laterais')
    if ceiling is None or walls is None:
        raise RuntimeError('Forro ou paredes nao encontrados; nao inferir arquitetura.')
    lo,hi=bounds(walls);roof=bounds(ceiling)[0].z
    lens_mat,lens_node=material('AP2OF_Lente_Foco',(.96,.92,.83),.35,spec=.25)
    lens_node.inputs['Emission Color'].default_value=(1,.89,.74,1)
    lens_node.inputs['Emission Strength'].default_value=3
    rim_mat,_=material('AP2OF_Aro_Foco',(.48,.49,.50),.3,metal=.7,spec=.4)
    # Focos ao longo das paredes: acompanham a arquitetura existente.
    for side,x in [('E',lo.x+.45),('D',hi.x-.45)]:
        for i,y in enumerate((2.7,6.2,9.7,13.2,16.7,19.7),1):
            data=bpy.data.lights.new(f'AP2OF_Foco_{side}_{i:02}','SPOT')
            data.energy=24;data.color=(1,.89,.74);data.spot_size=math.radians(70);data.spot_blend=.65;data.shadow_soft_size=.045
            o=bpy.data.objects.new(data.name,data);c.objects.link(o);o.location=(x,y,roof-.07)
            target=Vector((lo.x+.16 if side=='E' else hi.x-.16,y,roof-1.15))
            o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
            # Pequena lente/aro visivel; nao recorta nem desloca o forro existente.
            verts=[(x,y,roof-.012)]
            for radius in (.045,.060):
                verts += [(x+radius*math.cos(a*math.tau/32),y+radius*math.sin(a*math.tau/32),roof-.012) for a in range(32)]
            faces=[(0,1+(a+1)%32,1+a) for a in range(32)]
            faces += [(1+a,1+(a+1)%32,33+(a+1)%32,33+a) for a in range(32)]
            mesh=bpy.data.meshes.new(o.name+'_Lente_Malha');mesh.from_pydata(verts,[],faces)
            mesh.materials.append(lens_mat);mesh.materials.append(rim_mat)
            for p in mesh.polygons: p.material_index=0 if p.index<32 else 1
            fixture=bpy.data.objects.new(o.name+'_Lente',mesh);c.objects.link(fixture)
            records.append({'nome':o.name,'tipo':data.type,'watts':data.energy,'posicao':list(o.location),'alvo':list(target)})
    # Fontes narrativas animadas sao preservadas; preenchimentos estaticos sao moderados.
    old=[]
    for o in s.objects:
        if o.type!='LIGHT' or o.name.startswith('AP2OF_'): continue
        d=o.data
        if d.animation_data or o.animation_data: continue
        previous=d.energy
        if d.type in ('AREA','POINT','SPOT'): d.energy=min(previous,120 if d.type=='AREA' else 60)
        elif d.type=='SUN': d.energy=min(previous,.15)
        old.append({'nome':o.name,'antes':previous,'depois':d.energy})
    if s.world:
        # Preserva a rede animada de um World, se houver.
        if s.world.use_nodes and not s.world.node_tree.animation_data:
            for n in s.world.node_tree.nodes:
                if n.type=='BACKGROUND': n.inputs['Strength'].default_value=.05
    return {'novas_luzes':records,'preenchimentos_ajustados':old,'quantidade_paineis':len(patches),'validacao_visual':'Pendente: nenhuma renderizacao autorizada nesta etapa.'}

def configure_render():
    s=bpy.context.scene
    s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=128
    s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.025
    s.cycles.max_bounces=8;s.cycles.diffuse_bounces=4;s.cycles.glossy_bounces=4
    s.cycles.use_light_tree=True
    s.render.resolution_x=1920;s.render.resolution_y=1200;s.render.resolution_percentage=100
    s.render.fps=24;s.render.fps_base=1;s.frame_start=1;s.frame_end=360;s.use_preview_range=False
    s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264'
    s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD'
    s.render.ffmpeg.audio_codec='NONE';s.render.filepath='//render_final/AP2_IgorMariano.mp4'
    s.render.use_file_extension=True
    s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast'
    s.view_settings.exposure=0;s.view_settings.gamma=1
    # Luz e material precisam ser avaliados fisicamente quando a renderizacao for autorizada.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D': area.spaces.active.shading.type='SOLID'
    s['AP2OF_Sem_render']=True
    s['AP2OF_Conceito']='Ibmec: Da Plateia ao Palco da Vida Profissional'
    s['AP2OF_Validacao_visual']='Pendente: preparacao sem render por instrucao do usuario'

def check_images():
    result=[]
    for im in bpy.data.images:
        if im.source not in ('FILE','TILED'): continue
        if not im.packed_file:
            path=Path(bpy.path.abspath(im.filepath))
            if not path.is_file(): raise RuntimeError('Imagem ausente: '+im.name+' '+str(path))
            im.pack()
        result.append({'nome':im.name,'packed':bool(im.packed_file),'path':im.filepath})
    for font in bpy.data.fonts:
        if font.filepath and font.filepath!='<builtin>' and not font.packed_file:
            font.pack()
    return result

def main():
    if bpy.app.version[:2]!=(4,5): raise RuntimeError('Requer Blender 4.5 LTS')
    if sha(BASE)!=BASE_SHA: raise RuntimeError('A base difere da versao examinada.')
    if FINAL.exists() and sha(FINAL) != 'a2f7b16359f539f18b12be3f5efede99947b66c31f65b8d74af973807f7c661c':
        raise FileExistsError('Saida existente diferente da revisao intermediaria conhecida; preserve-a antes de executar.')
    bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False)
    s=bpy.context.scene;s.frame_set(1)
    before_geometry=geometry_record();before_actions=action_record();before_markers=markers()
    names=sorted(s.objects.keys())
    before_animation=animation_samples(names)
    for name in ('Objeto_A_Pulpito_Pitch','Objeto_B_Capelo_Formatura','Objeto_C_Diploma_Ibmec_Folha','Marca_Ibmec'):
        if name not in s.objects: raise RuntimeError('Objeto narrativo ausente: '+name)
    changes=finish_materials();lighting=finish_lighting();configure_render();images=check_images()
    assert action_record()==before_actions,'Acoes alteradas'
    assert markers()==before_markers,'Cortes alterados'
    after=geometry_record()
    assert all(after[name]==value for name,value in before_geometry.items()),'Geometria ou hierarquia alterada'
    assert animation_samples(names)==before_animation,'Transformacoes/cameras/shape keys alteradas nos 360 quadros'
    s.frame_set(1)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(FINAL),compress=True,relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(FINAL),load_ui=False,use_scripts=False)
    assert action_record()==before_actions,'Acoes divergentes depois de reabrir'
    assert markers()==before_markers,'Marcadores divergentes depois de reabrir'
    assert animation_samples(names)==before_animation,'Animacao divergente depois de reabrir'
    after=geometry_record()
    assert all(after[name]==value for name,value in before_geometry.items()),'Geometria divergente depois de reabrir'
    images=check_images()
    assert sha(BASE)==BASE_SHA,'Fonte alterada'
    saved_scene=bpy.context.scene
    assert saved_scene.render.filepath=='//render_final/AP2_IgorMariano.mp4','Saida de video remapeada indevidamente'
    assert (saved_scene.render.resolution_x,saved_scene.render.resolution_y,saved_scene.render.resolution_percentage)==(1920,1200,100)
    assert (saved_scene.frame_start,saved_scene.frame_end,saved_scene.render.fps,saved_scene.render.fps_base)==(1,360,24,1)
    assert saved_scene.render.image_settings.file_format=='FFMPEG'
    assert saved_scene.render.ffmpeg.format=='MPEG4' and saved_scene.render.ffmpeg.codec=='H264'
    for im in bpy.data.images:
        if im.name.startswith(('madeira_','tecido_')):
            assert im.filepath.startswith('//texturas/'),'Caminho relativo de textura invalido: '+im.filepath
    report={'status':'PREPARADO_SEM_RENDER','blender':bpy.app.version_string,'ambiente':'GitHub Actions github-hosted','plataforma':platform.platform(),'base':'AP2/V1/Fontes/Auditorio_AP2.blend','base_sha256':BASE_SHA,'saida':FINAL.name,'saida_sha256':sha(FINAL),'render_executado':False,'validacao_visual':False,'geometria_hierarquia_colecoes_preservadas':True,'acoes_keyframes_cameras_preservados':True,'quadros_verificados':360,'animacao_sha256':before_animation,'reabertura_verificada':True,'marcadores':before_markers,'materiais':changes,'iluminacao':lighting,'imagens':images,'render':{'resolucao':[1920,1200],'fps':24,'frames':[1,360],'motor':'Cycles','amostras':128,'formato':'MP4/H.264','saida':'//render_final/AP2_IgorMariano.mp4'}}
    dump('validacao_final.json',report)
    print('AP2OF_PREPARADO_SEM_RENDER',FINAL,sha(FINAL))

if __name__=='__main__':
    main()

