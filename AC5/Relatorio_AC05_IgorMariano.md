# AC05 — Materiais PBR e texturas

**Aluno:** Igor Mariano · **Disciplina:** Computação Gráfica · **Ferramenta:** Blender 4.5 LTS

## Continuidade da cena

A entrada é uma cópia da versão atual `AC04_IgorMariano.blend`, derivada da AP1. O auditório, os três objetos autorais, a palavra Ibmec e a câmera principal são mantidos. Os scripts preservam posições e geometria, verificando esses dados antes de salvar uma nova cena em AC5. Os arquivos AP1 e AC4 não são sobrescritos.

## Materiais

| Objeto | Material | Base Color | Roughness | Metallic |
|---|---|---|---|---|
| Púlpito (`Objeto_A_Pulpito_Pitch`) | `MAT_Madeira_Nogueira_PBR` | Imagem marrom com veios | Imagem 0,38–0,58 | 0 |
| Capelo (`Objeto_B_Capelo_Formatura`) | `MAT_Tecido_Preto_PBR` | Imagem quase preta, sRGB 0,035–0,080 | Imagem 0,72–0,87 | 0 |
| Diploma (`Objeto_C_Diploma_Ibmec`) | `MAT_Metal_Espelhado_PBR` | Prata clara, sRGB 0,92 | 0,025 | 1 |

Todos utilizam Principled BSDF. Madeira e tecido são dielétricos (IOR 1,5). A madeira representa o mobiliário do auditório. O capelo mantém o aspecto de vestimenta de formatura, com tecido preto conforme orientação do aluno; Sheen Weight 0,20 e Sheen Roughness 0,70 modelam um brilho suave nas bordas. O diploma é tratado como peça comemorativa em metal polido. É uma aproximação de superfície espelhada por condutor de baixa rugosidade, sem modelar uma camada de vidro sobre prata.

O enunciado menciona madeira, metal e espelho. Neste projeto, o diploma reúne metal e acabamento espelhado; o capelo foi deliberadamente mantido em tecido preto. Portanto, não são três objetos distintos de madeira, metal e espelho. Essa adaptação está explicitada para não atribuir ao material de tecido um comportamento metálico.

## Mapas e conexões

Madeira e tecido recebem três PNGs de 1024 × 1024. BaseColor é sRGB e se liga à entrada Base Color. Roughness é Non-Color e se liga à entrada Roughness. Normal é Non-Color e passa pelo nó Normal Map, em espaço tangente OpenGL (+Y), antes de chegar à entrada Normal. A força normal é 0,25 na madeira e 0,18 no tecido: o relevo é superficial, sem deslocamento da malha.

Os seis mapas são gerados por `gerar_texturas.py`, preparado com assistência de IA. A madeira combina ondas periódicas de diferentes frequências e uma pequena ondulação longitudinal. O tecido combina dois padrões perpendiculares para sugerir urdidura e trama. Os mapas normais derivam dos gradientes desses padrões, com correção da orientação vertical da imagem. A periodicidade permite repetir sem uma descontinuidade abrupta nas bordas. São texturas sintéticas, não fotografias nem materiais medidos. Os mapas acompanham o projeto sob CC0-1.0; não há imagens externas de bancos de textura.

## UV e organização

O script cria `UV_AC05` nas duas malhas texturizadas e usa Smart UV Project com limite angular de 66 graus e margem entre ilhas de 0,025. A projeção considera a escala real do objeto temporariamente e restaura exatamente as coordenadas da geometria. O método é apropriado para separar as superfícies do púlpito e as partes do capelo; a orientação das ilhas pode variar entre componentes, portanto não se afirma continuidade perfeita dos veios em toda a peça. A captura real do UV Editor permite revisar as ilhas e sua relação com a textura.

Cada mapa usa explicitamente `UV_AC05`. As imagens são empacotadas no `.blend` e também entregues em `texturas/`, com caminhos relativos. Não foram criados objetos auxiliares; por isso não há necessidade de uma coleção de objetos de teste. Os materiais anteriores permanecem nos arquivos originais. O material da marca é copiado mantendo seus valores e ligações, sem textura ou relevo.

## Iluminação e execução

As luzes, a câmera e o World partem da AC4, sem reposicionamento. A renderização foi executada em Cycles CPU com 64 amostras e denoising para calcular reflexos no diploma. No render conferido, a marca branca permanece legível; os veios marrons do púlpito aparecem claramente, o capelo preto apresenta brilho amplo e discreto e o diploma reflete faixas claras e escuras do ambiente. A trama fina e os relevos são sutis no enquadramento geral: a imagem final comprova a aparência global, enquanto os nós documentam a configuração detalhada. O render levou aproximadamente seis minutos na execução remota.

O Blender local não foi aberto. A execução autorizada ocorreu na nuvem, com render em background e capturas dos editores em sessão gráfica virtual. O registro de execução e os logs permanecem na cópia local; as execuções públicas estão vinculadas no README. O Blender 4.5.3 emitiu um aviso de que a entrada havia sido salva por uma compilação mais nova; as verificações do script confirmaram geometria e transformações preservadas e o render foi inspecionado visualmente. O aviso foi mantido no log.

## Referências

As orientações de Principled BSDF, UV, mapas de dados e empacotamento seguem o [enunciado AC05](https://jonh-carvalho.github.io/CG_26.2_8001/Avalia/AC05/) e as aulas [Materiais](https://jonh-carvalho.github.io/CG_26.2_8001/Disciplina/aula12/01_Materiais/), [UV Unwrapping](https://jonh-carvalho.github.io/CG_26.2_8001/Disciplina/aula12/04_UVWraping/) e [Texturas no Blender](https://jonh-carvalho.github.io/CG_26.2_8001/Disciplina/aula12/05_TexturasBlender/). O índice também aponta para Texturas em Computação Gráfica; sua consulta automatizada não retornou conteúdo útil nesta sessão. Os exercícios adicionais dessas aulas não foram tratados como solicitações para modificar o conceito da AP1.
