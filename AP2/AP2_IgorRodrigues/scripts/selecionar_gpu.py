"""Seleciona GPUs compativeis com Cycles no computador de renderizacao.
Uso: abra o .blend, Scripting > Text > Open > selecionar_gpu.py > Run Script.
Nao inicia render, nao salva o .blend e nao executa automaticamente ao abrir.
"""
import bpy
import json

BACKENDS = ('OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL')

def selecionar_gpu(salvar_preferencias=True):
    """Detecta todos os backends; ativa as GPUs do primeiro disponivel."""
    if bpy.context.scene.render.engine != 'CYCLES':
        raise RuntimeError('Abra a cena AP2 com o motor Cycles antes de executar.')
    prefs = bpy.context.preferences.addons['cycles'].preferences
    anterior = prefs.compute_device_type
    usos = {d.id: d.use for d in prefs.devices}
    encontrados = {}
    tentativas = []

    def restaurar():
        prefs.compute_device_type = anterior
        for d in prefs.devices:
            d.use = usos.get(d.id, False)

    # NVIDIA: OptiX/CUDA; AMD: HIP; Intel: oneAPI; Apple: Metal.
    # A enumeracao e feita pelo Cycles e depende de hardware e drivers.
    for backend in BACKENDS:
        try:
            prefs.compute_device_type = backend
            prefs.refresh_devices()
            placas = [
                {'nome': d.name, 'id': d.id, 'tipo': d.type}
                for d in prefs.devices if d.type == backend
            ]
            if placas:
                encontrados[backend] = placas
            tentativas.append({'backend': backend, 'placas': placas})
        except (TypeError, ValueError, RuntimeError) as erro:
            tentativas.append({'backend': backend, 'erro': str(erro)})

    if not encontrados:
        restaurar()
        raise RuntimeError(
            'Nenhuma GPU compativel com Cycles foi encontrada. Verifique o driver '
            'e Preferences > System. Nenhum render foi iniciado. Detalhes: '
            + json.dumps(tentativas, ensure_ascii=False)
        )

    # Cycles usa um backend por vez; GPU de fabricantes diferentes nao sao
    # combinadas automaticamente. Todas as placas do backend escolhido sao ativadas.
    selecionado = next(b for b in BACKENDS if b in encontrados)
    try:
        prefs.compute_device_type = selecionado
        prefs.refresh_devices()
        placas = [d for d in prefs.devices if d.type == selecionado]
        if not placas:
            raise RuntimeError('A GPU deixou de estar disponivel durante a selecao.')
        for d in prefs.devices:
            d.use = d.type == selecionado
    except (TypeError, ValueError, RuntimeError):
        restaurar()
        raise

    for scene in bpy.data.scenes:
        if scene.render.engine == 'CYCLES':
            scene.cycles.device = 'GPU'

    resultado = {
        'backend': selecionado,
        'gpus': [d.name for d in placas],
        'todos_os_backends_detectados': encontrados,
        'preferencias_salvas': False,
        'render_iniciado': False
    }
    if salvar_preferencias:
        try:
            bpy.ops.wm.save_userpref()
            resultado['preferencias_salvas'] = True
        except RuntimeError as erro:
            resultado['aviso'] = (
                'GPU ativa nesta sessao; nao foi possivel salvar preferencias: ' + str(erro)
            )
    print('AP2_GPU_SELECIONADA', json.dumps(resultado, ensure_ascii=False, indent=2))
    return resultado

if __name__ == '__main__':
    try:
        resultado = selecionar_gpu()
    except RuntimeError as erro:
        mensagem_erro = str(erro).split(' Detalhes:')[0]
        if not bpy.app.background:
            def desenhar_erro(self, context):
                self.layout.label(text=mensagem_erro)
            bpy.context.window_manager.popup_menu(
                desenhar_erro, title='AP2: GPU nao configurada', icon='ERROR'
            )
        raise
    else:
        if not bpy.app.background:
            def desenhar(self, context):
                self.layout.label(text='Backend: ' + resultado['backend'])
                for nome in resultado['gpus']:
                    self.layout.label(text=nome)
                self.layout.label(text='GPU configurada. Nenhum render iniciado.')
            bpy.context.window_manager.popup_menu(
                desenhar, title='AP2: GPU selecionada', icon='INFO'
            )
