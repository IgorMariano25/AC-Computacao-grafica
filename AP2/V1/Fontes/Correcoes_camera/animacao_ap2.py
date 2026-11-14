"""AP2 — adaptação para o auditório fornecido (Blender 4.5 LTS).
Execute em uma CÓPIA da AP1. Não salva nem sobrescreve arquivos automaticamente.
Scripting > Open > animacao_ap2.py > Run Script. Duração: 360 frames / 24 fps.
Resolve os nomes reais, separa a tela, cria capelo/diploma se ausentes e mantém
as curvas e os materiais originais da logo. Usa as quatro câmeras em seis planos.
Pode executar novamente sem deriva.
"""
import bpy
import bmesh
import json
from math import radians, pi, sin, cos
from mathutils import Vector, Matrix

NOMES = {'camera':'Camera_Principal','pulpito':'Objeto_A_Pulpito_Pitch',
         'capelo':'Objeto_B_Capelo_Formatura','marca':'Marca_Ibmec','tela':'Tela_Projecao'}
F_INICIO, F_FIM = 1, 360
CAMERA_RECUO, CAMERA_SUBIDA = 12.0, 1.5
CAPELO_ALTURA, MARCA_PROFUNDIDADE, FOCO_POTENCIA = 2.5, 3.0, 800.0
s=bpy.context.scene


def bounds(o):
    bpy.context.view_layer.update()
    pts=[o.matrix_world @ Vector(v) for v in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]),Vector([max(p[i] for p in pts) for i in range(3)])


def collection(name):
    c=bpy.data.collections.get(name)
    if c is None:c=bpy.data.collections.new(name);s.collection.children.link(c)
    return c


props=collection('12_AP2_Elementos')
lights=collection('13_AP2_Luzes')


def move_to(o,c):
    for old in list(o.users_collection):old.objects.unlink(o)
    c.objects.link(o)


def resolve(name, aliases, typ=None):
    for n in [name]+aliases:
        o=s.objects.get(n)
        if o is not None and (typ is None or o.type==typ):o.name=name;return o
    raise RuntimeError('Não encontrei '+name+'. Abra o auditório completo antes de executar.')


def material(name,color,rough=.5,metal=0):
    m=bpy.data.materials.get(name)
    if m:return m
    m=bpy.data.materials.new(name);m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Roughness'].default_value=rough;n.inputs['Metallic'].default_value=metal
    m.diffuse_color=(*color,1);return m


def cube(name,loc,dim,mat,bevel=.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);move_to(o,props)
    if bevel:
        m=o.modifiers.new('Bordas','BEVEL');m.width=bevel;m.segments=3
    return o


def cylinder(name,loc,r,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=r,depth=depth,location=loc);o=bpy.context.object;o.name=name;o.data.materials.append(mat);move_to(o,props)
    return o


def cord(name,points,r,mat):
    d=bpy.data.curves.new(name,'CURVE');d.dimensions='3D';d.bevel_depth=r;d.bevel_resolution=3
    spl=d.splines.new('POLY');spl.points.add(len(points)-1)
    for p,co in zip(spl.points,points):p.co=(*co,1)
    o=bpy.data.objects.new(name,d);props.objects.link(o);d.materials.append(mat);return o


def attach(o,parent):
    mw=o.matrix_world.copy();o.parent=parent;o.matrix_world=mw


def base(o):
    """Guarda pose final em coordenadas globais na primeira execução."""
    if '_ap2_pose_final' not in o:
        bpy.context.view_layer.update();o['_ap2_pose_final']=json.dumps([list(row) for row in o.matrix_world])
    matrix=Matrix(json.loads(o['_ap2_pose_final']))
    if o.animation_data:o.animation_data_clear()
    o.parent=None;o.matrix_world=matrix;o.rotation_mode='XYZ'
    bpy.context.view_layer.update()
    return o.location.copy(),o.rotation_euler.copy(),o.scale.copy()


def key(o,frame,loc=None,rot=None,scale=None):
    for prop,value in [('location',loc),('rotation_euler',rot),('scale',scale)]:
        if value is not None:setattr(o,prop,value);o.keyframe_insert(prop,frame=frame)


def curves(action):
    if not action:return []
    # Blender 4.5 actions may contain separate slots for object and camera data.
    result=[f for layer in action.layers for strip in layer.strips
            for bag in getattr(strip,'channelbags',[]) for f in bag.fcurves]
    if result:return result
    return list(action.fcurves)


# Validate essential source objects before preparing animation.
cam=resolve(NOMES['camera'],['Camera_Palco'],'CAMERA')
pulpito=resolve(NOMES['pulpito'],['Pulpito_curvo_perfurado','Pulpito_curvo'],'MESH')
ceiling=s.objects.get('Forro_modular');roof=bounds(ceiling)[0].z if ceiling else 4.2
back=s.objects.get('Parede_fundos');back_y=bounds(back)[0].y if back else 20.8

# Screen: separate only the two large white faces; the roll, frame and panels stay.
tela=s.objects.get(NOMES['tela'])
if tela is None:
    panel=resolve('Painel_ripado_e_tela',[],'MESH')
    white={i for i,m in enumerate(panel.data.materials) if m and m.name.startswith('Tela_branca')}
    candidates=[p for p in panel.data.polygons if p.material_index in white]
    if not candidates:raise RuntimeError('A malha do painel não tem a superfície Tela_branca.')
    biggest=max(p.area for p in candidates);chosen={p.index for p in candidates if p.area>biggest*.8}
    screenmesh=panel.data.copy();screenmesh.name='Tela_Projecao_Malha'
    bm=bmesh.new();bm.from_mesh(screenmesh);bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index not in chosen],context='FACES');bm.to_mesh(screenmesh);bm.free()
    # Duplicate the source mesh so any other linked panel is unaffected.
    panel.data=panel.data.copy();bm=bmesh.new();bm.from_mesh(panel.data);bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.index in chosen],context='FACES');bm.to_mesh(panel.data);bm.free()
    tela=bpy.data.objects.new(NOMES['tela'],screenmesh);props.objects.link(tela);tela.matrix_world=panel.matrix_world.copy()
    m=next(m for m in panel.data.materials if m and m.name.startswith('Tela_branca')).copy();m.name='AP2_Tela_Emissiva'
    tela.data.materials.clear();tela.data.materials.append(m)
    for p in tela.data.polygons:p.material_index=0

# Cap: actual 3D model, with mortarboard, crown, cord and tassel.
capelo=s.objects.get(NOMES['capelo'])
if capelo is None:
    black=material('AP2_Capelo_preto',(.008,.011,.016),.82)
    gold=material('AP2_Borla_dourada',(.65,.34,.035),.55)
    capelo=bpy.data.objects.new(NOMES['capelo'],None);props.objects.link(capelo);capelo.empty_display_type='CUBE';capelo.empty_display_size=.25
    capelo.location=(-4.50,2.06,1.43);bpy.context.view_layer.update()
    x,y,z=capelo.location
    parts=[cylinder('AP2_Capelo_copa',(x,y,z+.095),.135,.19,black),cube('AP2_Capelo_abaco',(x,y,z+.208),(.55,.55,.036),black,.008),cylinder('AP2_Capelo_botao',(x,y,z+.237),.018,.014,black)]
    parts.append(cord('AP2_Capelo_cordao',[(x,y,z+.247),(x+.14,y-.07,z+.245),(x+.26,y-.19,z+.232),(x+.285,y-.20,z+.14)],.007,gold))
    for i in range(9):
        a=i*2*pi/9;dx=.012*cos(a);dy=.012*sin(a)
        parts.append(cord('AP2_Borla_%02d'%i,[(x+.285+dx,y-.20+dy,z+.145),(x+.290+dx,y-.20+dy,z+.047)],.003,gold))
    for o in parts:attach(o,capelo)

# Diploma: curved paper with an explicit roll/unroll shape key, independent of the tube.
folha=s.objects.get('Objeto_C_Diploma_Ibmec_Folha')
if folha is None:
    paper=material('AP2_Papel_diploma',(.90,.86,.70),.87)
    width,length=.36,.54;nx,ny=10,48
    def surface(angle):
        return [(width*(i/nx-.5),length/angle*sin(angle*j/ny),length/angle*(1-cos(angle*j/ny))) for j in range(ny+1) for i in range(nx+1)]
    verts=surface(radians(7));faces=[]
    for j in range(ny):
        for i in range(nx):a=j*(nx+1)+i;faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new('AP2_Folha_subdividida');mesh.from_pydata(verts,[],faces);mesh.materials.append(paper)
    folha=bpy.data.objects.new('Objeto_C_Diploma_Ibmec_Folha',mesh);props.objects.link(folha);folha.location=(-3.45,1.74,1.435)
    folha.shape_key_add(name='Base_aberta');rolled=folha.shape_key_add(name='Enrolado')
    for p,co in zip(rolled.data,surface(radians(330))):p.co=co
    sol=folha.modifiers.new('Espessura_papel','SOLIDIFY');sol.thickness=.002
    blue=material('AP2_Canudo_azul',(.004,.014,.055),.55)
    tube=cylinder('Objeto_C_Diploma_Ibmec_Canudo',(-3.85,1.97,1.48),.047,.47,blue);tube.rotation_euler=(radians(90),0,0)
    for yy in [1.752,2.188]:
        band=cylinder('AP2_Canudo_anel',(-3.85,yy,1.48),.048,.012,gold if 'gold' in globals() else material('AP2_Borla_dourada',(.65,.34,.035)));band.rotation_euler=(radians(90),0,0);attach(band,tube)

# Standalone stage mark: copy the original curves and shaders, never recreate letters.
marca=s.objects.get(NOMES['marca'])
if marca is None:
    original=s.objects.get('Logo_Painel_Esquerdo') or s.objects.get('Logo_Painel_Direito')
    if not original:raise RuntimeError('Não encontrei a logo original nos painéis.')
    lo,hi=bounds(original);center=(lo+hi)/2;scale=2.5/(hi.x-lo.x)
    marca=bpy.data.objects.new(NOMES['marca'],None);props.objects.link(marca);marca.empty_display_type='PLAIN_AXES';marca.empty_display_size=.25;marca.location=(0,2.9,1.02)
    copy=original.copy();copy.data=original.data;copy.name='AP2_Logo_Curvas_Originais';props.objects.link(copy);copy.parent=None
    copy.matrix_world=Matrix.Translation(marca.location)@Matrix.Scale(scale,4)@Matrix.Translation(-center)@original.matrix_world
    bpy.context.view_layer.update();attach(copy,marca)

# Reset final poses before inserting keyframes (prevents accumulated movement).
cam_loc,cam_rot,_=base(cam);cap_loc,cap_rot,_=base(capelo);mark_loc,_,mark_scale=base(marca)
front=cam.matrix_world.to_quaternion()@Vector((0,0,-1));front.z=0
if front.length<.001:front=Vector((0,-1,0))
front.normalize()
start=cam_loc-front*CAMERA_RECUO+Vector((0,0,CAMERA_SUBIDA))
start.y=min(start.y,back_y-.70);start.z=min(start.z,roof-.30)
key(cam,1,start,cam_rot);key(cam,290,cam_loc,cam_rot);key(cam,360,cam_loc,cam_rot);s.camera=cam


def spotlight(name,target):
    aim=bpy.data.objects.get(name+'_Alvo')
    if aim is None:aim=bpy.data.objects.new(name+'_Alvo',None);lights.objects.link(aim)
    if target.type=='EMPTY':aim.location=target.matrix_world.translation+Vector((0,0,.15))
    else:lo,hi=bounds(target);aim.location=(lo+hi)/2
    o=s.objects.get(name)
    if o is None:d=bpy.data.lights.new(name,'SPOT');o=bpy.data.objects.new(name,d);lights.objects.link(o)
    o.location=aim.location-front*2+Vector((0,0,2.8));o.location.z=min(o.location.z,roof-.18)
    o.data.spot_size=radians(48);o.data.spot_blend=.55;o.data.shadow_soft_size=.18
    track=next((c for c in o.constraints if c.type=='TRACK_TO'),None) or o.constraints.new('TRACK_TO');track.track_axis='TRACK_NEGATIVE_Z';track.up_axis='UP_Y';track.target=aim
    if o.data.animation_data:o.data.animation_data_clear()
    return o


def switch(o,f0,f1):
    for f,v in [(1,0),(f0,0),(f1,FOCO_POTENCIA),(360,FOCO_POTENCIA)]:o.data.energy=v;o.data.keyframe_insert('energy',frame=f)


switch(spotlight('Spot_Pulpito',pulpito),95,110)
switch(spotlight('Spot_Mesa',capelo),120,130)
# Allow a margin for the rotating mortarboard, not only the cap origin.
cap_children=[o for o in capelo.children_recursive if o.type in ['MESH','CURVE']]
cap_top=max(bounds(o)[1].z for o in cap_children) if cap_children else bounds(capelo)[1].z
height=max(.15,min(CAPELO_ALTURA,roof-.32-cap_top));s['AP2_Altura_capelo']=height
key(capelo,1,cap_loc,cap_rot);key(capelo,130,cap_loc,cap_rot)
key(capelo,148,cap_loc+Vector((0,0,height)),(cap_rot.x+radians(20),cap_rot.y,cap_rot.z+pi))
key(capelo,170,cap_loc,(cap_rot.x,cap_rot.y,cap_rot.z+2*pi));key(capelo,360,cap_loc,(cap_rot.x,cap_rot.y,cap_rot.z+2*pi))

if folha.data.shape_keys and 'Enrolado' in folha.data.shape_keys.key_blocks:
    keys=folha.data.shape_keys
    if keys.animation_data:keys.animation_data_clear()
    rolled=keys.key_blocks['Enrolado']
    for f,v in [(1,1),(175,1),(210,0),(360,0)]:rolled.value=v;rolled.keyframe_insert('value',frame=f)
else:
    bends=[m for m in folha.modifiers if m.type=='SIMPLE_DEFORM' and m.deform_method=='BEND']
    if not bends:raise RuntimeError('O diploma existente não tem Enrolado nem modificador Bend.')
    for m in bends:
        k='_ap2_bend_final_'+m.name
        if k not in folha:folha[k]=m.angle
        for f,v in [(1,radians(330)),(175,radians(330)),(210,folha[k]),(360,folha[k])]:m.angle=v;folha.keyframe_insert(f'modifiers["{m.name}"].angle',frame=f)

mat=tela.active_material
if mat is None or not mat.use_nodes:raise RuntimeError('A tela precisa de um material com nós.')
node=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
if mat.node_tree.animation_data:mat.node_tree.animation_data_clear()
node.inputs['Emission Color'].default_value=(1,1,1,1)
for f,v in [(1,0),(217,0),(242,3),(360,3)]:node.inputs['Emission Strength'].default_value=v;node.inputs['Emission Strength'].keyframe_insert('default_value',frame=f)
for f in [1,217]:key(marca,f,mark_loc-Vector((0,0,MARCA_PROFUNDIDADE)),scale=mark_scale*.6)
for f in [277,360]:key(marca,f,mark_loc,scale=mark_scale)

# Clamp Bézier handles so peaks and holds do not overshoot scene limits.
ids=[cam,capelo,marca,folha.data.shape_keys,mat.node_tree]+[o.data for o in lights.objects if o.type=='LIGHT']
for data in ids:
    ad=getattr(data,'animation_data',None)
    if ad:
        for fc in curves(ad.action):
            for k in fc.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
# Auxiliary cameras are real render cameras, bound to timeline markers.
# Camera_Corte has two fixed poses with a hard cut at frame 175.
plateia=resolve('Camera_Plateia',[],'CAMERA')
pulpito_cam=resolve('Camera_Pulpito',[],'CAMERA')
corte=resolve('Camera_Corte',[],'CAMERA')

def camera_pose(o,position,target,lens):
    o.parent=None;o.rotation_mode='XYZ';o.location=position
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.type='PERSP';o.data.lens=lens;o.data.sensor_fit='HORIZONTAL';o.data.sensor_width=36
    o.data.shift_x=0;o.data.shift_y=0;o.data.clip_start=.05;o.data.clip_end=200
    o.data.dof.use_dof=False

for auxiliary in [plateia,pulpito_cam,corte]:
    auxiliary.animation_data_clear();auxiliary.data.animation_data_clear()
camera_pose(plateia,(0,2.8,2.35),(0,14.1,2.0),21)
camera_pose(pulpito_cam,(4.6,4.5,2.15),(3.2,1.95,1.20),45)
camera_pose(corte,(-4.2,5.8,2.85),(-4.4,2.0,2.65),27)
key(corte,1,corte.location.copy(),corte.rotation_euler.copy())
corte.data.keyframe_insert('lens',frame=1)
camera_pose(corte,(-3.65,3.00,2.55),(-3.65,1.98,1.45),48)
key(corte,175,corte.location.copy(),corte.rotation_euler.copy())
corte.data.keyframe_insert('lens',frame=175)
for animated in [corte,corte.data]:
    for fc in curves(animated.animation_data.action):
        for k in fc.keyframe_points:k.interpolation='CONSTANT'

s.render.fps=24;s.render.fps_base=1;s.frame_start=1;s.frame_end=360
s.use_preview_range=False
# Remove old AP2 labels and camera bindings so no earlier cut overrides this edit.
for m in list(s.timeline_markers):
    if m.name.startswith('AP2 |') or m.camera:s.timeline_markers.remove(m)
planos=[(1,48,cam,'Geral do palco'),(49,84,plateia,'Plateia'),
        (85,120,pulpito_cam,'Púlpito'),(121,174,corte,'Capelo'),
        (175,216,corte,'Diploma'),(217,360,cam,'Marca e plano final')]
for first,last,camera,label in planos:
    marker=s.timeline_markers.new('AP2 | '+label,frame=first);marker.camera=camera
s['AP2_Planos']=json.dumps([{'inicio':a,'fim':b,'camera':c.name,'plano':d} for a,b,c,d in planos],ensure_ascii=False)
s['AP2_Preparado']=True;s.camera=cam;s.frame_set(1)
for name in NOMES.values():print(name,'OK' if name in s.objects else 'NÃO ENCONTRADO')
for a,b,c,d in planos:print(f'{a:03}–{b:03}: {c.name} — {d}')
print('AP2 multicâmera: 360 frames a 24 fps. NumPad 0 e Espaço para assistir. Salve como um NOVO .blend.')
