# AP2 — preparada para renderização posterior

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
