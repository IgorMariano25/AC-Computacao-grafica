"""Capturas REAIS da interface Blender. Executar em sessão gráfica/Xvfb.
Não funciona em -b: não há janela para fotografar em background.
"""
from pathlib import Path
import bpy, traceback, subprocess
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'AC05_IgorMariano.blend'),load_ui=False,use_scripts=False)
obj=bpy.data.objects['Objeto_A_Pulpito_Pitch']
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); bpy.context.view_layer.objects.active=obj
step=0

def screenshot(name):
    # Captura o framebuffer X11 real; o screenshot interno pode retornar preto
    # com Mesa/software GL em Xvfb, mesmo com a interface desenhada corretamente.
    bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP',iterations=2)
    subprocess.run(['scrot','--overwrite',str(ROOT/'imagens'/name)],check=True)

def tick():
    global step
    try:
        window=bpy.context.window_manager.windows[0]
        area=max(window.screen.areas,key=lambda a:a.width*a.height)
        print('AC5_CAPTURE',step,window.width,window.height,area.type,area.width,area.height,flush=True)
        if step==0:
            with bpy.context.temp_override(window=window,area=area):
                bpy.ops.screen.screen_full_area(use_hide_panels=True)
            step+=1; return 2
        if step==1:
            area.type='NODE_EDITOR'; area.ui_type='ShaderNodeTree'
            area.spaces.active.shader_type='OBJECT'
            area.spaces.active.show_region_ui=False
            area.spaces.active.show_region_toolbar=False
            step=1.5; return 3
        if step==1.5:
            # As dimensões dos nós só existem após o primeiro desenho do editor.
            region=next(r for r in area.regions if r.type=='WINDOW')
            with bpy.context.temp_override(window=window,area=area,region=region): bpy.ops.node.view_all()
            step=2; return 4
        if step==2:
            screenshot('AC05_ShaderEditor.png')
            area.type='IMAGE_EDITOR'; area.ui_type='UV'
            area.spaces.active.image=bpy.data.images.get('madeira_BaseColor.png')
            obj=bpy.data.objects['Objeto_A_Pulpito_Pitch']; bpy.context.view_layer.objects.active=obj; obj.select_set(True)
            with bpy.context.temp_override(window=window,area=area):
                bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
            step+=1; return 3
        if step==3:
            region=next(r for r in area.regions if r.type=='WINDOW')
            with bpy.context.temp_override(window=window,area=area,region=region): bpy.ops.image.view_all(fit_view=True)
            step+=1; return 4
        if step==4:
            screenshot('AC05_UVEditor.png')
            (ROOT/'imagens'/'capturas_reais.txt').write_text('Capturas reais da interface do Blender '+bpy.app.version_string+' em sessão gráfica virtual Xvfb/Linux. Nenhuma interface simulada.\n',encoding='utf-8')
            bpy.ops.wm.quit_blender(); return None
    except Exception:
        (ROOT/'imagens'/'erro_captura.txt').write_text(traceback.format_exc(),encoding='utf-8')
        bpy.ops.wm.quit_blender(); return None

if bpy.app.background: raise RuntimeError('Capturas exigem sessão gráfica; não utilizar -b.')
bpy.app.timers.register(tick,first_interval=5)
