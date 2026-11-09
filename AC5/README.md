# AC05 — Materiais PBR e texturas

Projeto de Igor Mariano, continuando `AC4/AC04_IgorMariano.blend`, que deriva da AP1. Os nomes históricos `IgorRodrigues` da AP1 não foram alterados.

## Entrega

O projeto foi executado no Blender 4.5.3 LTS na nuvem. Esta pasta contém os arquivos essenciais da entrega: cena, render, capturas reais dos editores, relatório, mapas e scripts. O ZIP, as prévias, os logs e os arquivos auxiliares permanecem apenas locais, ignorados pelo Git.

Execuções: [render final](https://github.com/IgorMariano25/AC-Computacao-grafica/actions/runs/42702894498) e [capturas finais](https://github.com/IgorMariano25/AC-Computacao-grafica/actions/runs/42705087078).

- `AC05_IgorMariano.blend`: cena final, com texturas empacotadas.
- `imagens/AC05_render_final.png`: imagem real da câmera principal, 1920 × 1080.
- `imagens/AC05_ShaderEditor.png`: nós do material de madeira.
- `imagens/AC05_UVEditor.png`: UVs do púlpito sobre a textura.
- `Relatorio_AC05_IgorMariano.md`: escolhas, propriedades, referências e observações.

Materiais: púlpito de madeira, capelo de tecido preto (solicitação do aluno) e diploma de metal espelhado. Madeira e tecido usam mapas de imagem de cor, rugosidade e normal, com UVs próprias. O diploma combina a aparência de metal e espelho citada no enunciado. Esta adaptação não apresenta o capelo como objeto metálico.

## Reprodução em Blender 4.5 LTS

Na pasta AC5, em um ambiente com Blender instalado:

```powershell
blender -b --python-exit-code 1 --python scripts/preparar_ac5.py -- --render
```

Isso carrega a cópia local em `base_AC4`, quando disponível, ou `../AC4/AC04_IgorMariano.blend`, já versionado no repositório, e salva `AC05_IgorMariano.blend`, empacota as imagens e renderiza pela câmera principal. O script recusa sobrescrever uma saída já existente; para reproduzir, preserve a entrega existente em outro local antes de executar. Para apenas preparar, retire `-- --render`.

Capturas reais dos editores exigem sessão gráfica. Em Linux, utilize Xvfb:

```sh
LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s '-screen 0 1600x1000x24' sh -c 'openbox & blender --factory-startup --window-geometry 0 0 1600 1000 --python-exit-code 1 --python scripts/capturar_editores.py'
```

O script requer `scrot`, Openbox e Xvfb no Linux; carrega a cena preservando um layout novo, fotografa a interface real e encerra sem salvar mudanças de layout no projeto. Não tenta produzir capturas de interface com `-b`, modo em que a interface não existe. Nenhum desses comandos foi executado no computador local do aluno.

Os seis mapas já são fornecidos. Para regenerá-los, use `python scripts/gerar_texturas.py` (dependência: NumPy). Os scripts do Blender usam apenas módulos incluídos no Blender.

## Originais

AP1 e AC4 permanecem fora do destino de gravação. Os registros de integridade permanecem na cópia local, fora do Git. A cópia de entrada preserva a câmera, as luzes e a geometria; o motor de render passa de EEVEE para Cycles para refletir o ambiente no material espelhado.

## Referências

- [Enunciado AC05](https://jonh-carvalho.github.io/CG_26.2_8001/Avalia/AC05/)
- [Materiais](https://jonh-carvalho.github.io/CG_26.2_8001/Disciplina/aula12/01_Materiais/)
- [Texturas em computação gráfica](https://jonh-carvalho.github.io/CG_26.2_8001/Disciplina/aula12/03_Texturas/)
- [UV Unwrapping](https://jonh-carvalho.github.io/CG_26.2_8001/Disciplina/aula12/04_UVWraping/)
- [Texturas no Blender](https://jonh-carvalho.github.io/CG_26.2_8001/Disciplina/aula12/05_TexturasBlender/)
- [Manual Blender 4.5](https://docs.blender.org/manual/en/4.5/)

Os exemplos genéricos de criar cubos, latas, planetas ou personagens são exercícios das referências, não entregáveis adicionais da AC05. O projeto conserva os três objetos da AP1. Não se utilizaram imagens de Poly Haven ou ambientCG; a procedência dos mapas autorais está em `texturas/FONTES_E_LICENCA.json`.
