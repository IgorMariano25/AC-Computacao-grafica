"""Inspecao somente leitura. Executar exclusivamente em runner hospedado GitHub."""
import os
if os.environ.get('GITHUB_ACTIONS') != 'true' or os.environ.get('RUNNER_ENVIRONMENT') != 'github-hosted':
    raise RuntimeError('Execucao permitida somente em GitHub Actions hospedado, nunca local.')
import bpy, json, hashlib, platform
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'AP2/OFICIAL/nuvem'
OUT.mkdir(parents=True, exist_ok=True)
BASE = ROOT / 'AP2/V1/Fontes/Auditorio_AP2.blend'
assert hashlib.sha256(BASE.read_bytes()).hexdigest() == 'd53dfa2612c6891293ffdd181b7fe78bbe4cd9e96d4e90c25a7ccd8a1a1135ae'
bpy.ops.wm.open_mainfile(filepath=str(BASE), load_ui=False)
s = bpy.context.scene
def bounds(o):
    pts = [o.matrix_world @ Vector(p) for p in o.bound_box]
    return [[round(f(p[i] for p in pts), 5) for i in range(3)] for f in (min,max)]
def obj(o):
    d = dict(name=o.name,type=o.type,location=list(o.location),rotation=list(o.rotation_euler),scale=list(o.scale),parent=o.parent.name if o.parent else None,hide_render=o.hide_render,collections=[c.name for c in o.users_collection])
    if o.type in ('MESH','CURVE','FONT'):
        d.update(bounds=bounds(o),materials=[m.name if m else None for m in o.data.materials])
    if o.type == 'MESH':
        d.update(mesh=o.data.name,vertices=len(o.data.vertices),polygons=len(o.data.polygons),uvs=[u.name for u in o.data.uv_layers],groups=[v.name for v in o.vertex_groups])
    if o.type == 'LIGHT':
        d.update(light_type=o.data.type,energy=o.data.energy,color=list(o.data.color))
    return d
report = dict(blender=bpy.app.version_string,platform=platform.platform(),base=str(BASE),base_sha256=hashlib.sha256(BASE.read_bytes()).hexdigest(),engine=s.render.engine,world=s.world.name if s.world else None,frame=[s.frame_start,s.frame_end],fps=s.render.fps,resolution=[s.render.resolution_x,s.render.resolution_y],camera=s.camera.name if s.camera else None,markers=[dict(name=m.name,frame=m.frame,camera=m.camera.name if m.camera else None) for m in s.timeline_markers],objects=[obj(o) for o in s.objects],materials=[],images=[dict(name=i.name,path=i.filepath,packed=bool(i.packed_file),source=i.source) for i in bpy.data.images])
for m in bpy.data.materials:
    d=dict(name=m.name,users=m.users)
    if m.use_nodes:
        d['nodes']=[dict(name=n.name,type=n.type,inputs={i.name:list(i.default_value) if hasattr(i.default_value,'__len__') and not isinstance(i.default_value,str) else i.default_value for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(int,float,str,tuple))}) for n in m.node_tree.nodes]
    report['materials'].append(d)
(OUT/'inspecao_base.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print('INSPECAO_CONCLUIDA',len(report['objects']),'objetos; nenhum render executado.')
