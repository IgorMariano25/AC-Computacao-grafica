"""Monta YAML de texto; nao importa nem executa Blender. Pode rodar localmente."""
from pathlib import Path
import ast

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
template = (HERE/'ap2-preparar.yml').read_text(encoding='utf-8-sig')

def script_step(filename, label):
    content = (ROOT/'scripts'/filename).read_text(encoding='utf-8-sig').rstrip()
    ast.parse(content)
    indented = '\n'.join('          '+line for line in content.splitlines())
    return ('      - name: '+label+'\n        run: |\n'
            '          mkdir -p AP2/OFICIAL/scripts\n'
            "          cat > AP2/OFICIAL/scripts/"+filename+" <<'PY'\n"+
            indented+'\n          PY\n')

inspection = template.replace('      - name: Inspecionar sem renderizar',
    script_step('inspecionar_nuvem.py','Preparar script de inspecao')+
    '      - name: Inspecionar sem renderizar')
(HERE/'ap2-inspecao-autocontida.yml').write_text(inspection,encoding='utf-8')
full = inspection.replace('      - name: Inspecionar sem renderizar',
    script_step('preparar_oficial.py','Preparar script de acabamento')+
    '      - name: Inspecionar sem renderizar')
run = '''      - name: Aplicar acabamento e validar sem renderizar
        run: |
          set -o pipefail
          "$RUNNER_TEMP/blender-4.5.3-linux-x64/blender" -b --factory-startup --disable-autoexec --python-exit-code 1 --python AP2/OFICIAL/scripts/preparar_oficial.py 2>&1 | tee AP2/OFICIAL/nuvem/log_preparo.txt
'''
full = full.replace('      - name: Devolver resultados na branch de trabalho',
                    run+'      - name: Devolver resultados na branch de trabalho')
(HERE/'ap2-completo-autocontido.yml').write_text(full,encoding='utf-8')
print('Workflows de texto montados; Blender nao executado.')
