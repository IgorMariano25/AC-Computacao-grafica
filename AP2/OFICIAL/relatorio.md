# AP2 — Ibmec: Da Plateia ao Palco da Vida Profissional

Aluno: Igor Mariano. Os arquivos históricos da AP1 usam o nome Igor Rodrigues.

**Estado: preparado e verificado na nuvem, sem renderização.** Entrega: `AP2_IgorMariano.blend`, gerado e reaberto no Blender 4.5.3 LTS. A aparência final depende da renderização posterior.

## Fontes e escolha da base

Foram examinados o relatório, os scripts e o inventário da AP1; as versões e os scripts da AP2; e o relatório, o script de materiais e os mapas da AC05. Não existe `relatorio.md` anterior na AP2 disponível localmente. A pasta V2 contém relatórios JSON, mas não os `.blend` que eles mencionam: seus registros históricos não comprovam a disponibilidade dessas cenas.

Base selecionada: `AP2/V1/Fontes/Auditorio_AP2.blend`, SHA-256 `d53dfa2612c6891293ffdd181b7fe78bbe4cd9e96d4e90c25a7ccd8a1a1135ae`. Ela é idêntica ao arquivo de `Correcoes_camera`, com revisão multicâmera posterior à versão `Corrigida`. A data de cópia de novembro, isoladamente, não foi usada como evidência da revisão. Os 65 arquivos originais conferidos permaneceram intactos, conforme `nuvem/verificacao_entrega.json`.

## Conceito, planos e animação

O conceito da AP1 associa a formação profissional ao percurso da plateia ao palco. Púlpito, capelo e diploma representam apresentar, conquistar e atuar; a marca Ibmec encerra a sequência. A revisão de acabamento mantém as ações e os cortes existentes, conforme o roteiro de `Correcoes_camera`:

| Frames | Plano e ação já implementados na base |
| --- | --- |
| 1–48 | Câmera principal: apresentação do palco e aproximação. |
| 49–84 | Plateia vista do palco. |
| 85–120 | Púlpito; foco acende entre 95 e 110. |
| 121–174 | Capelo: lançamento a partir de 130, ápice em 148 e pouso em 170. |
| 175–216 | Diploma: folha passa de enrolada a aberta até 210. |
| 217–360 | Retorno ao palco, tela acende até 242, marca sobe até 277; encerramento estabilizado. |

Esse desdobramento multicâmera já existia na AP2 e difere dos intervalos gerais planejados na AP1. A revisão de acabamento não altera novamente o storyboard. O conceito e os três elementos narrativos são mantidos. A base usa translação/rotação do capelo, transformação da marca, deslocamento da câmera, distância focal e shape key da folha. O script histórico usa Bézier com alças AUTO_CLAMPED nas ações suaves e interpolação CONSTANT no corte da câmera de detalhes. A verificação comparou ações e keyframes e avaliou transformações, propriedades de câmera e shape keys nos 360 quadros antes/depois, inclusive após reabrir o arquivo salvo. Os marcadores dos seis planos e as quatro câmeras foram preservados.

## Acabamento preparado

| Superfície | Ajuste aplicado |
| --- | --- |
| Poltronas | Tecido azul nos estofados, trama discreta, laterais e base inferior com plástico preto fosco. Reatribuição de faces sem mover vértices. |
| Ferro próximo às cadeiras | Acabamento preto com reflexão suave, representando ferro pintado. |
| Paredes | Branco ligeiramente quente, rugosidade alta e especular discreto. |
| Púlpito | Madeira preta com veios sutis, preservando perfurações, silhueta e marca original. |
| Capelo | Oxford preto, rugosidade alta, brilho de borda muito discreto; borla preservada. |
| Diploma | Papel claro com microvariação procedural de cor e relevo. A base contém uma folha sem texto de certificado; não se inventou texto ou assinatura. |

Os mapas BaseColor e Roughness da madeira e do tecido da AC05 são reaproveitados. A madeira é escurecida; o tecido é remapeado para azul e preto. A projeção BOX com coordenadas Generated evita mudar as UVs existentes e acompanha os objetos animados. BaseColor é sRGB; Roughness é Non-Color. O relevo superficial usa Bump a partir da imagem de cor; os mapas Normal originais acompanham o pacote como recursos da AC05, mas não são conectados como normais tangentes em uma projeção tridimensional. O acabamento metálico espelhado do diploma da AC05 é substituído por papel conforme a instrução atual.

Lambert é representado no papel por Diffuse BSDF com roughness 0, misturado com pequena participação PBR. Nos demais materiais, Principled BSDF/GGX combina difusa e especular para uma aproximação visual do comportamento Blinn-Phong, sem alegar que implementa literalmente sua equação. Phong não precisa ser aplicado adicionalmente: os três modelos foram apresentados como alternativas. As categorias de planejamento, animação e câmera não são modelos de reflexão; elas são tratadas como decisões de sequência.

## Iluminação e saída preparadas

Foram adicionadas 20 fontes AREA retangulares de 45 W, posicionadas pelas faces inferiores dos difusores existentes, logo abaixo das grelhas; suas superfícies receberam emissão. Foram distribuídos 12 focos SPOT de 24 W próximos às paredes, acompanhados de pequenos aros e lentes. As posições das placas e saídas de ar foram preservadas. As duas fontes narrativas animadas permaneceram intactas; dez preenchimentos estáticos passaram de 420 W para 120 W e o World foi moderado. Os valores precisam de avaliação visual em render posterior.

Configuração salva e verificada: Cycles, 128 amostras, denoising, amostragem adaptativa, AgX, 1920×1200 a 100% (16:10, preservando a proporção 1280×800 da base), 24 fps, frames 1–360, duração de 15 s. Saída `//render_final/AP2_IgorMariano.mp4`, contêiner MPEG-4, codec H.264. Não foi acrescentado áudio: os aplausos da AP1 eram planejamento, sem arquivo de áudio fornecido. As 12 imagens da cena estão empacotadas no `.blend`; os mapas da AC05 também acompanham `texturas/`, com caminhos relativos `//texturas/` verificados após reabertura.

## Execução e limites

A instrução inicial do pedido — preparar sem renderizar — prevalece sobre as menções posteriores à produção de prévias e vídeo. Portanto, nenhuma nova imagem ou animação deve ser renderizada nesta etapa. As prévias antigas foram apenas consultadas e não são evidência dos novos materiais ou luzes. Não há comprovação visual de exposição, sombras, reflexos ou aparência final enquanto não houver render posterior.

O Blender foi executado exclusivamente no GitHub Actions, runner hospedado `ubuntu-22.04`, versão 4.5.3 LTS, build `67807e1800cc`, obtida do distribuidor oficial e conferida por SHA-256. A [execução final](https://github.com/IgorMariano25/AC-Computacao-grafica/actions/runs/43626601049) terminou com sucesso. O resultado veio do commit `f08793b4e37c3fd1ccc133337e77f909e8ad6e7e`, na branch `codex/ap2-oficial-cloud-20261114`, sem alterar as branches AP2/master. Nenhuma execução local do Blender ocorreu.

Os comandos foram `blender -b --factory-startup --disable-autoexec --python-exit-code 1 --python AP2/OFICIAL/scripts/inspecionar_nuvem.py` e o mesmo comando com `scripts/preparar_oficial.py`. Os scripts bloqueiam execução fora de runner hospedado e não chamam renderização. Comandos completos, execuções, logs e verificações estão em `nuvem/execucoes.json`, `log_inspecao.txt`, `log_preparo.txt` e `validacao_final.json`.

Desafios e soluções: a integração de API retornou HTTP 403 para escrita, então o workflow foi enviado pelo navegador autenticado autorizado. A inspeção identificou os eixos locais das poltronas, e a seleção de faces foi ajustada para atribuir plástico às laterais e à parte inferior sem alterar vértices. Uma primeira gravação remapeou caminhos relativos para a pasta de origem; a execução final desativou esse remapeamento e confirmou os caminhos após reabertura. Geometria, hierarquia, coleções e ações existentes passaram nas comparações automatizadas. Isso verifica preservação estrutural e preparação; não comprova exposição, reflexos ou acabamento visual.

SHA-256 do arquivo final: `9b77c4f6ad4b1c4b0f3b2193c9e26cba1303d63a7111f8531187302c9739eb96`.

## Fontes e licenças

- AP1: `Relatorio_AP1_IgorRodrigues.md`, storyboard e geometria fornecidos no projeto.
- AP2: `Correcoes_camera/animacao_ap2.py`, `LEIA-ME_AP2.txt`, `Verificacao_AP2.json` e a cena selecionada. Registros históricos não substituem a nova validação.
- AC05: `Relatorio_AC05_IgorMariano.md`, `scripts/gerar_texturas.py` e seis mapas sintéticos autorais, com licença CC0-1.0 declarada em `texturas/FONTES_E_LICENCA.json`.
- Quatro fotografias anexadas pelo usuário: referência visual para poltronas, teto, focos e púlpito. Não foram redistribuídas nem transformadas em texturas; não foi presumida licença de redistribuição.
- Marca Ibmec: recurso original do projeto, preservado; nenhuma nova licença sobre a marca é concedida.
- Manual oficial do Blender: [Diffuse BSDF](https://docs.blender.org/manual/th/4.5/render/shader_nodes/shader/diffuse.html) para Lambert com roughness 0, e [Principled BSDF](https://docs.blender.org/manual/en/4.5/render/shader_nodes/shader/principled.html) para a resposta física difusa/especular. A associação didática a Blinn-Phong é uma aproximação visual do projeto, não uma equivalência declarada pelo manual.

