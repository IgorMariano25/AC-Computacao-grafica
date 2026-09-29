# AP1 — Ibmec em 15 segundos

Cena-conceito da peça de 15 s pedida na [AP1](AP1.md), construída **inteiramente por script** no Blender 4.5 LTS.

São **três montagens alternativas** da mesma peça, todas com a palavra **Ibmec** como elemento principal do enquadramento e com as cores oficiais da marca:

| Cenário | Peça | Script | Coleção | Palavra Ibmec |
| --- | --- | --- | --- | --- |
| 🌅 litoral | “Do Mucuripe ao Futuro” · Ibmec Fortaleza | [`AP1_IgorMariano.py`](AP1_IgorMariano.py) | `AP1_Ibmec_Conceito` | texto 3D (ou SVG) |
| 🎓 educação | “A Sala que Abre o Mundo” · Ibmec | [`AP1_IgorMariano_Educacao.py`](AP1_IgorMariano_Educacao.py) | `AP1_Ibmec_Educacao` | texto 3D (ou SVG) |
| 🎓 educação + logo | “A Sala que Abre o Mundo” · Ibmec | [`AP1_IgorMariano_Educacao_Logo.py`](AP1_IgorMariano_Educacao_Logo.py) | `AP1_Ibmec_Educacao_Logo` | **logo oficial** do [`Logo-Ibmec-3D.blend`](Logo-Ibmec-3D.blend) |

Os três usam as mesmas constantes de configuração, os mesmos materiais `Azul Ibmec` / `Amarelo Ibmec` e a mesma timeline de 360 frames — dá para rodar um, avaliar, e rodar o outro no mesmo arquivo sem conflito de nomes (cada um limpa só a sua própria coleção).

| Arquivo | O que é |
| --- | --- |
| [`AP1_IgorMariano.py`](AP1_IgorMariano.py) | script principal (cenário litoral) — monta a cena inteira do zero |
| [`AP1_IgorMariano_Educacao.py`](AP1_IgorMariano_Educacao.py) | script do cenário de **educação** — anfiteatro do Ibmec, também do zero |
| [`AP1_IgorMariano_Educacao_Logo.py`](AP1_IgorMariano_Educacao_Logo.py) | mesmo cenário de educação, mas com a **marca real importada** do `Logo-Ibmec-3D.blend` e o pingo do “i” em amarelo |
| [`AP1_capturas.py`](AP1_capturas.py) | gera as 8 imagens dos entregáveis (render Workbench, ~1 s cada) |
| [`AP1_Relatorio.md`](AP1_Relatorio.md) | relatório: conceito, objetos autorais, técnicas, plano da AP2 |
| [`AP1_Storyboard.md`](AP1_Storyboard.md) | storyboard com os três momentos da peça |

## Como rodar

1. Abra o **Blender 4.5 LTS** (arquivo novo, ou o `AP1-Logo-Ibmec-3D.blend` se quiser reaproveitar os materiais oficiais).
2. Aba **Scripting** → **Open** → o script escolhido → **Run Script** (`Alt+P`).
3. Salve com o nome correspondente (`AP1_IgorMariano.blend`, `AP1_IgorMariano_Educacao.blend`, `AP1_IgorMariano_Educacao_Logo.blend`).
4. Aba **Scripting** → **Open** → `AP1_capturas.py` → **Run Script** — as imagens saem em `saida/`.

No Windows, as mensagens do script aparecem em **Window → Toggle System Console**.

> Para capturar o cenário de **educação** com o `AP1_capturas.py`, troque, no bloco `detalhes`, os nomes `OBJ_Farol_Mucuripe` / `OBJ_Jangada_Mucuripe` / `OBJ_Planetario_Dragao_do_Mar` por `OBJ_Livro_Aberto` / `OBJ_Globo_Armilar` / `OBJ_Capelo_Formatura`, e, no bloco `quadros`, os nomes das câmeras por `CAM_SB1_Sala_Antes_da_Aula` / `CAM_SB2_Conhecimento_se_Abre` / `CAM_SB3_Assinatura_Ibmec`. `CAM_Principal` e `LOGO_Palavra_Ibmec` têm o mesmo nome nos dois cenários.

## Ajustes rápidos

Tudo que costuma precisar de ajuste está no bloco `0. CONFIGURACAO`, no topo de cada script:

| Constante | Para quê |
| --- | --- |
| `CAMINHO_SVG_LOGO` | caminho do `Ibmec-letras-separadas.svg`; se preenchido, o script usa as **curvas oficiais** da marca no lugar do texto 3D |
| `CAMINHO_FONTE` | `.ttf` da fonte institucional; vazio faz o script procurar uma fonte adequada no sistema |
| `LARGURA_PALAVRA` | largura da palavra em metros (8,2 no cenário litoral; 7,6 no painel da sala de aula) |
| `ALTURA_BASE_PALAVRA` / `PROFUNDIDADE_PALAVRA` | onde a palavra **Ibmec** se apoia — deck-mirante no litoral, painel frontal na sala |
| `HEX_AZUL_IBMEC` / `HEX_AMARELO_IBMEC` | cores da marca — já preenchidas com os valores lidos do `AP1-Logo-Ibmec-3D.blend` |
| `SALVAR_BLEND` / `CAMINHO_BLEND` | salvar o arquivo automaticamente ao final |

Se os materiais `Azul Ibmec` e `Amarelo Ibmec` já existirem no arquivo aberto, o script os **reaproveita** em vez de criar cores novas.

## Cores da marca

Extraídas do `AP1-Logo-Ibmec-3D.blend`:

| Material | sRGB | Linear (Blender) |
| --- | --- | --- |
| Azul Ibmec | `#002555` | `(0.0000, 0.0185, 0.0908)` |
| Amarelo Ibmec | `#F5AC00` | `(0.9131, 0.4125, 0.0000)` |

## Estrutura da cena — cenário litoral

```
AP1_Ibmec_Conceito
├── 01_Palavra_Ibmec        pivô + 5 letras + pingo do "i" (objetos separados)
├── 02_Objetos_Autorais     farol · jangada · planetário (os três autorais)
├── 03_Cenario_Fortaleza    mar · praia · deck · escadaria · rochedo · coqueiros
└── 04_Camera_e_Auxiliares  câmera principal + alvo + 3 câmeras de storyboard + sol
```

## Estrutura da cena — cenário de educação

```
AP1_Ibmec_Educacao
├── 01_Palavra_Ibmec           pivô + 5 letras + pingo do "i" (a "lâmpada da ideia")
├── 02_Objetos_Autorais        livro aberto · globo armilar · capelo (os três autorais)
├── 03_Cenario_Sala_de_Aula    piso · paredes · painel frontal · palco · degraus ·
│                              arquibancada · bancadas · púlpito · mesa · luminárias · cadeiras
└── 04_Camera_e_Auxiliares     câmera principal + alvo + 3 câmeras de storyboard + luz de área
```

### “A Sala que Abre o Mundo” — conceito

Um anfiteatro do **Ibmec** antes da aula. A palavra **Ibmec** ocupa, em relevo, a reentrância escura do painel frontal, acima do palco — é o elemento mais legível do enquadramento e a assinatura que fecha a peça. Nos 15 s previstos para a AP2: a sala acende luminária por luminária, o **livro** se abre no púlpito, o **globo armilar** gira, o **capelo** entra em quadro e o pingo amarelo do “i” desce como uma lâmpada acesa, encaixando-se na letra.

Os três objetos autorais, todos modelados do zero:

| Objeto | Papel no conceito | Técnicas |
| --- | --- | --- |
| `OBJ_Livro_Aberto` | o conhecimento que se abre na aula | grades curvadas por função · `Solidify` · `Bevel` |
| `OBJ_Globo_Armilar` | o mundo que a formação alcança | superfície de revolução · 3 curvas de Bézier cíclicas com bevel |
| `OBJ_Capelo_Formatura` | a entrega da educação, o futuro do aluno | revolução · `inset` + extrusão · composição de malhas · curva do cordão |

O cenário usa ainda `Array` (degraus, arquibancada, bancadas e duas direções de luminárias) e duplicatas vinculadas nas 16 cadeiras.

Storyboard (marcadores na timeline): `SB1_Sala_Antes_da_Aula` @1 · `SB2_Conhecimento_se_Abre` @121 · `SB3_Assinatura_Ibmec` @241 · `Fim_15s` @360.

### Versão com o logo oficial

`AP1_IgorMariano_Educacao_Logo.py` monta exatamente o mesmo cenário, mas **importa a marca real** em vez de reconstruí-la:

1. faz `append` dos objetos do `Logo-Ibmec-3D.blend`, junto com os materiais oficiais `Azul Ibmec` e `Amarelo Ibmec` (descarta a câmera e a luz do arquivo de origem);
2. identifica o pingo do “i” — no arquivo ele se chama `ponto_amarelo` — renomeia para `LOGO_Ponto_i` e **força o material Amarelo Ibmec** (`FORCAR_PINGO_AMARELO`), com as letras em `LOGO_Letra_01_i` … `LOGO_Letra_05_c`;
3. detecta se o logo veio deitado no plano XY e, só nesse caso, aplica os 90° em X pelo pivô; depois centraliza, apoia a linha de base e escala até `LARGURA_PALAVRA`;
4. se o `.blend` não for achado, cai para o SVG oficial e, por fim, para o texto 3D — a cena nunca fica sem a palavra.

| Constante (bloco `0. CONFIGURACAO`) | Para quê |
| --- | --- |
| `CAMINHO_BLEND_LOGO` | caminho fixo do `.blend` do logo; vazio faz o script procurar por `NOMES_BLEND_LOGO` na pasta do arquivo aberto, na pasta do script e em `PASTAS_BUSCA_LOGO` |
| `PISTAS_PINGO` | pedaços de nome que identificam o pingo (`ponto`, `pingo`, `amarel`, `dot`); sem correspondência, ele é achado pela geometria (peça mais alta e menor) |
| `FORCAR_PINGO_AMARELO` | mantém o pingo do “i” em **Amarelo Ibmec** mesmo que venha com outro material |
| `EXTRUSAO_LOGO_IMPORTADO` | extrusão aplicada só às curvas que chegarem planas |

Timeline nos dois cenários: **24 fps, frames 1–360 = 15 s exatos**.
