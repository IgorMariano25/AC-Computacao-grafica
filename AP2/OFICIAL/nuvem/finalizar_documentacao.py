"""Finaliza documentação local; não importa nem executa Blender."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))
def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

validation = read_json(root/'nuvem/validacao_final.json')
final = root/'AP2_IgorMariano.blend'
assert digest(final) == validation['saida_sha256']
assert validation['status'] == 'PREPARADO_SEM_RENDER'
assert validation['reabertura_verificada'] and validation['quadros_verificados'] == 360
originals = read_json(root/'nuvem/integridade_originais.json')
changed = [entry['path'] for entry in originals if digest(Path(entry['path'])) != entry['sha256'].lower()]
assert not changed, changed

runs = read_json(root/'nuvem/execucoes.json')
runs['preparacao_intermediaria'] = {
    'status':'success', 'run_url':'https://github.com/IgorMariano25/AC-Computacao-grafica/actions/runs/43626234469',
    'commit_entrada':'9b5c1ed1b1e1a14901f8a3eeabfb10ef65089247',
    'observacao':'Preservacao verificada; remapeamento de caminhos relativos corrigido na execucao final.',
    'render_executado':False}
runs['preparacao'] = {
    'status':'success', 'run_url':'https://github.com/IgorMariano25/AC-Computacao-grafica/actions/runs/43626601049',
    'commit_entrada':'da8065add228135388213aa1d699a31a44e9b872',
    'commit_resultado':'f08793b4e37c3fd1ccc133337e77f909e8ad6e7e',
    'comando':'$RUNNER_TEMP/blender-4.5.3-linux-x64/blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python AP2/OFICIAL/scripts/preparar_oficial.py',
    'render_executado':False, 'saida_sha256':digest(final)}
write_json(root/'nuvem/execucoes.json', runs)

report = root/'relatorio.md'
content = report.read_text(encoding='utf-8-sig')
replacements = [
('**Estado: preparação em andamento, sem renderização.** Este documento será complementado pelos resultados efetivos da execução em nuvem. Os scripts não constituem um `.blend` final validado.',
 '**Estado: preparado e verificado na nuvem, sem renderização.** Entrega: `AP2_IgorMariano.blend`, gerado e reaberto no Blender 4.5.3 LTS. A aparência final depende da renderização posterior.'),
('Os originais devem permanecer intactos.', 'Os 65 arquivos originais conferidos permaneceram intactos, conforme `nuvem/verificacao_entrega.json`.'),
('A verificação de preservação deve comparar as curvas e avaliar os 360 quadros antes/depois, inclusive depois de reabrir o arquivo salvo.',
 'A verificação comparou ações e keyframes e avaliou transformações, propriedades de câmera e shape keys nos 360 quadros antes/depois, inclusive após reabrir o arquivo salvo. Os marcadores dos seis planos e as quatro câmeras foram preservados.'),
('| Superfície | Ajuste previsto pelo script |', '| Superfície | Ajuste aplicado |'),
('O script procura as faces inferiores dos difusores já modelados para posicionar fontes AREA retangulares logo abaixo das grelhas; as superfícies recebem emissão. Focos SPOT próximos às paredes são distribuídos conforme os limites da arquitetura. As posições das placas e saídas de ar não são reconstruídas. As fontes narrativas animadas permanecem intactas; preenchimentos estáticos e World são moderados. Os valores são iniciais e precisam de avaliação em render posterior.',
 'Foram adicionadas 20 fontes AREA retangulares de 45 W, posicionadas pelas faces inferiores dos difusores existentes, logo abaixo das grelhas; suas superfícies receberam emissão. Foram distribuídos 12 focos SPOT de 24 W próximos às paredes, acompanhados de pequenos aros e lentes. As posições das placas e saídas de ar foram preservadas. As duas fontes narrativas animadas permaneceram intactas; dez preenchimentos estáticos passaram de 420 W para 120 W e o World foi moderado. Os valores precisam de avaliação visual em render posterior.'),
('Configuração prevista:', 'Configuração salva e verificada:'),
('Imagens devem ser empacotadas no `.blend` e os mapas da AC05 também acompanham `texturas/`.',
 'As 12 imagens da cena estão empacotadas no `.blend`; os mapas da AC05 também acompanham `texturas/`, com caminhos relativos `//texturas/` verificados após reabertura.'),
('O ambiente pretendido é GitHub Actions, runner hospedado `ubuntu-22.04`, Blender 4.5.3 LTS obtido do distribuidor oficial e conferido por SHA-256. A integração de API recusou a criação do workflow com HTTP 403; foi solicitado acesso ao navegador para dar continuidade. O script bloqueia sua execução fora do runner hospedado e não chama operadores de renderização. Logs e resultados efetivos deverão constar de `nuvem/`.',
 'O Blender foi executado exclusivamente no GitHub Actions, runner hospedado `ubuntu-22.04`, versão 4.5.3 LTS, build `67807e1800cc`, obtida do distribuidor oficial e conferida por SHA-256. A [execução final](https://github.com/IgorMariano25/AC-Computacao-grafica/actions/runs/43626601049) terminou com sucesso. O resultado veio do commit `f08793b4e37c3fd1ccc133337e77f909e8ad6e7e`, na branch `codex/ap2-oficial-cloud-20261114`, sem alterar as branches AP2/master. Nenhuma execução local do Blender ocorreu.\n\n'
 'Os comandos foram `blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python AP2/OFICIAL/scripts/inspecionar_nuvem.py` e o mesmo comando com `scripts/preparar_oficial.py`. Os scripts bloqueiam execução fora de runner hospedado e não chamam renderização. Comandos completos, execuções, logs e verificações estão em `nuvem/execucoes.json`, `log_inspecao.txt`, `log_preparo.txt` e `validacao_final.json`.\n\n'
 'Desafios e soluções: a integração de API retornou HTTP 403 para escrita, então o workflow foi enviado pelo navegador autenticado autorizado. A inspeção identificou os eixos locais das poltronas, e a seleção de faces foi ajustada para atribuir plástico às laterais e à parte inferior sem alterar vértices. Uma primeira gravação remapeou caminhos relativos para a pasta de origem; a execução final desativou esse remapeamento e confirmou os caminhos após reabertura. Geometria, hierarquia, coleções e ações existentes passaram nas comparações automatizadas. Isso verifica preservação estrutural e preparação; não comprova exposição, reflexos ou acabamento visual.\n\n'
 'SHA-256 do arquivo final: `9b77c4f6ad4b1c4b0f3b2193c9e26cba1303d63a7111f8531187302c9739eb96`.')]
for old,new in replacements:
    assert old in content, old
    content = content.replace(old,new)
report.write_text(content, encoding='utf-8')

(root/'LEIA-ME.md').write_text('''# AP2 — preparada para renderização posterior

Arquivo final: **`AP2_IgorMariano.blend`**, produzido e reaberto no Blender 4.5.3 LTS exclusivamente em GitHub Actions. Estado: `PREPARADO_SEM_RENDER`.

## Para levar ao ambiente de renderização

Copie a pasta `OFICIAL`. O `.blend` contém as 12 imagens da cena empacotadas; `texturas/` também inclui os seis mapas originais da AC05 e sua licença. No outro ambiente, abra o arquivo com Blender 4.5.3 LTS ou compatível e confira o dispositivo de renderização disponível. A cena está salva no quadro 1, em modo Solid, com Cycles/CPU configurado.

Já estão configurados: 1920×1200 (16:10), 24 fps, quadros 1–360, 15 segundos, Cycles com 128 amostras e denoising, saída MPEG-4/H.264 em `//render_final/AP2_IgorMariano.mp4`. Essa pasta de saída será relativa à localização do `.blend`. O arquivo permanece sem áudio.

Nenhuma prévia ou vídeo novo foi renderizado, conforme a instrução inicial do pedido. A avaliação visual de materiais, exposição, sombras e reflexos deve ocorrer no ambiente de renderização posterior. As prévias históricas não comprovam o acabamento atual.

## Conteúdo da entrega

- `AP2_IgorMariano.blend`: materiais, iluminação, animação e saída preparadas.
- `relatorio.md`: conceito, storyboard existente, alterações, fontes, licenças e limitações.
- `texturas/`: recursos da AC05.
- `nuvem/validacao_final.json`: preservação da cena, comparação dos 360 quadros, reabertura e imagens empacotadas.
- `nuvem/verificacao_entrega.json`: hash do download e conferência dos 65 arquivos originais.
- `nuvem/execucoes.json`, `registro_execucao.json` e logs: ambiente, comandos e resultados.
- `scripts/`: inspeção e preparo usados na nuvem; não executar no computador local.
- `nuvem/ap2-completo-autocontido.yml`: workflow final utilizado. Os workflows de inspeção permanecem como histórico. A repetição do preparo sobre um arquivo final existente é bloqueada para protegê-lo.

Base preservada: `../V1/Fontes/Auditorio_AP2.blend`, idêntica à revisão em `Correcoes_camera`. Não havia `relatorio.md` anterior na AP2, e os `.blend` mencionados nos registros da V2 não estavam disponíveis.

[Execução final na nuvem](https://github.com/IgorMariano25/AC-Computacao-grafica/actions/runs/43626601049). SHA-256 do `.blend`: `9b77c4f6ad4b1c4b0f3b2193c9e26cba1303d63a7111f8531187302c9739eb96`.
''', encoding='utf-8')

verification = {
    'status':'ENTREGA_CONFERIDA_SEM_RENDER', 'data_utc':datetime.now(timezone.utc).isoformat(),
    'blend':final.name, 'blend_bytes':final.stat().st_size, 'blend_sha256':digest(final),
    'hash_download_confere_com_nuvem':True, 'originais_conferidos':len(originals),
    'originais_alterados':changed, 'blender_local_executado':False, 'render_executado':False,
    'validacao_visual':False, 'commit_download':'f08793b4e37c3fd1ccc133337e77f909e8ad6e7e'}
write_json(root/'nuvem/verificacao_entrega.json', verification)
print(json.dumps(verification,ensure_ascii=False,indent=2))
