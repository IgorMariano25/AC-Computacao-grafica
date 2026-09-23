# AP1 — Relatório

**Disciplina:** Computação Gráfica I · **Professor:** Jonh Edson
**Aluno:** Igor Mariano · **Software:** Blender 4.5 LTS
**Enunciado:** [`AP1.md`](AP1.md) · **Script principal:** [`AP1_IgorMariano.py`](AP1_IgorMariano.py) · **Capturas:** [`AP1_capturas.py`](AP1_capturas.py) · **Storyboard:** [`AP1_Storyboard.md`](AP1_Storyboard.md)

---

## 1. Conceito e título da peça

**Título: “Do Mucuripe ao Futuro”.**

A peça parte de uma imagem que qualquer pessoa de Fortaleza reconhece — o sol nascendo sobre o mar do Mucuripe, com a jangada saindo para o mar e o farol ainda aceso — e transforma essa cena cotidiana na assinatura da marca **Ibmec**.

A ideia central é uma **transformação com dupla leitura**: o sol que nasce sobre o Atlântico é, ao mesmo tempo, o **pingo amarelo da letra “i”** do logo. O que começa como paisagem termina como marca. O percurso do sol pelo enquadramento é o fio narrativo dos 15 segundos.

Os valores pedidos no enunciado aparecem traduzidos em elementos concretos do litoral cearense:

| Valor pedido | Como aparece na cena |
| --- | --- |
| Solidez | o deck-mirante de concreto que sustenta a palavra e o farol de pedra sobre o rochedo |
| Futuridade | o sol/pingo que se encaixa no logo e a luz do farol apontando para a frente |
| Criatividade e cultura | a cúpula do planetário do Centro Dragão do Mar |
| Empreendedorismo | a jangada do Mucuripe: sair todo dia para o mar em busca do sustento |
| Construção | as letras que sobem do deck, peça por peça, como uma obra sendo erguida |

A cena é **figurativa e legível a partir de um único quadro**: mesmo parada, entende-se que é o litoral de Fortaleza e que a palavra **ibmec** é o assunto principal.

## 2. Ideia de entrada, transformação e apresentação da palavra

A palavra não aparece pronta: ela é **descoberta** e depois **construída**.

1. **Entrada (0 s – 5 s).** A câmera está quase na altura da água, olhando o horizonte. Só existem mar, jangada e o farol. O sol começa a nascer — é o objeto `LOGO_Ponto_i`, o pingo do “i”, já modelado e já na cor amarela oficial da marca.
2. **Transformação (5 s – 10 s).** A câmera sobe e gira para o deck-mirante. As cinco letras sobem da plataforma em sequência (i, b, m, e, c), cada uma com a sua própria entrada, porque **cada letra é um objeto independente** com pivô no seu lugar.
3. **Apresentação (10 s – 15 s).** A câmera assume o enquadramento principal. O sol desce da linha do horizonte e **encaixa como pingo do “i”**, completando o logotipo. A luz do farol faz o último varrimento e a peça termina no lock-up da marca.

A integridade da marca foi preservada: a palavra está em caixa baixa, com o azul e o amarelo **extraídos diretamente do arquivo `AP1-Logo-Ibmec-3D.blend`** (`#002555` e `#F5AC00`), sem deformação, sem rotação que prejudique a leitura, e ocupando pouco mais da metade da largura do quadro na câmera principal.

> Detalhe técnico: se o SVG oficial das letras separadas for informado em `CAMINHO_SVG_LOGO`, o script importa as curvas reais da marca no lugar do texto 3D. Se os materiais `Azul Ibmec` / `Amarelo Ibmec` já existirem no arquivo, o script os reaproveita em vez de criar cores novas.

## 3. Os três objetos autorais

Todos foram **modelados do zero por script**, a partir de perfis e primitivas geradas em `bmesh` — nenhum modelo externo foi importado. Estão na subcoleção `02_Objetos_Autorais`.

### 3.1 `OBJ_Farol_Mucuripe` — Farol do Mucuripe

- **Referência:** o farol que guarda a enseada do Mucuripe, ponto de orientação da navegação cearense desde o século XIX.
- **Função na peça:** é o **âncora vertical da composição** (lado esquerdo do quadro) e o símbolo da orientação — a instituição como referência que aponta um caminho. É também a única fonte de luz direcional da narrativa.
- **Como foi feito:** superfície de revolução (`spin`) de um perfil de 12 pontos desenhado à mão, que resolve base alargada, fuste cônico e varanda num único passo; segunda revolução para a cúpula; `inset` + extrusão para dentro no vão da porta; faixa da varanda pintada em azul Ibmec por seleção de faces por altura; modificador **Bevel** para quebrar as arestas vivas. O filho `Farol_Lanterna_Vidro` já está no lugar para receber a emissão de luz na AP2.

### 3.2 `OBJ_Jangada_Mucuripe` — Jangada

- **Referência:** a jangada de vela triangular das praias do Mucuripe e do Futuro, símbolo maior do litoral do Ceará.
- **Função na peça:** representa o **empreendedorismo** — sair, arriscar, voltar com o resultado. Ocupa o espaço negativo entre a palavra e a linha do horizonte, dando profundidade ao quadro sem competir com as letras.
- **Como foi feito:** composição de malhas — cinco troncos gerados em laço e amarrados lado a lado, mais mastro inclinado, retranca e caixa de pesca; a proa foi afinada e levantada por **edição proporcional feita à mão** (deslocamento dos vértices em função da coordenada X); modificador **Bevel**. A vela (`Jangada_Vela`) é uma grade triangular com **Solidify** (espessura do pano) e **Simple Deform / Bend** (barriga da vela ao vento).

### 3.3 `OBJ_Planetario_Dragao_do_Mar` — Planetário do Centro Dragão do Mar

- **Referência:** a cúpula branca do planetário do Centro Dragão do Mar de Arte e Cultura, na Praia de Iracema.
- **Função na peça:** é o elemento de **cultura, conhecimento e inovação**; equilibra a composição no lado direito com uma massa arredondada, contrapondo a verticalidade do farol.
- **Como foi feito:** superfície de revolução do tambor + arco de 13 pontos da cúpula; `inset` + extrusão para o pórtico de entrada; tambor em azul Ibmec e cúpula em concreto claro por índice de material. O filho `Planetario_Rampa` é uma **curva de Bézier** com `extrude` e `bevel_depth` (passarela suspensa), com `tilt` de 90° para deixar o tabuleiro na horizontal — é o uso explícito de curvas e superfícies pedido no requisito 6.

## 4. Técnicas de modelagem e transformações utilizadas

O requisito pedia **pelo menos dois** recursos além da escala de primitivas. Foram usados:

| Técnica | Onde |
| --- | --- |
| Superfície de revolução (`spin`) | farol, cúpula da lanterna, planetário, rochedo |
| Extrusão de face | porta do farol, pórtico do planetário, piso do deck |
| `Inset` de face | porta, pórtico, piso do deck |
| Bevel (operador de malha e modificador) | farol, jangada, deck, letras |
| Texto 3D convertido em malha | as cinco letras (`extrude` + `bevel_depth` + tesselação) |
| Curva de Bézier com `extrude`/`bevel`/`tilt` | passarela do planetário |
| Modificador **Array** | escadaria do deck-mirante |
| Modificador **Solidify** | vela da jangada |
| Modificador **Simple Deform (Bend)** | vela da jangada |
| Modificador **Displace** + textura procedural | ondulação do mar |
| Modificador **Wave** | marolas (já animadas, prontas para a AP2) |
| Lofting de anéis (composição de malhas) | tronco do coqueiro |
| Deformação por função matemática | proa da jangada, dunas e linha da costa |
| Duplicatas vinculadas | os três coqueiros compartilham a mesma malha |
| Hierarquia pai/filho | palavra → letras; farol → lanterna; jangada → vela; planetário → passarela |

**Transformações geométricas aplicadas de forma intencional:**

- **Translação:** posicionamento de cada objeto no espaço da composição (farol à esquerda e ao fundo, planetário à direita, jangada sobre o mar em plano médio, palavra no centro sobre o deck).
- **Rotação:** o pivô `LOGO_Palavra_Ibmec` gira 90° em X para levantar as letras — elas são construídas deitadas no plano XY e passam a ficar de pé, de frente para a câmera; a jangada gira −127° em Z para navegar em diagonal; farol, planetário e coqueiros recebem rotações pequenas em Z para quebrar a simetria.
- **Escala:** a palavra é medida depois de montada e o pivô recebe a escala exata que a deixa com **8,2 m de largura** — a largura calculada para ocupar pouco mais da metade do quadro na câmera principal. Os coqueiros usam escalas diferentes (1,00 / 0,88 / 1,12) para não parecerem cópias.

**Espaço, composição e projeção:** a câmera principal (`CAM_Principal`, lente 35 mm) está em `(0, −15, 5.2)` com uma constraint **Track To** apontada para o empty `CAM_Alvo_Principal`. A projeção perspectiva foi usada deliberadamente: o farol, mais distante, aparece pequeno e recortado contra o céu; a palavra, no plano próximo, domina o centro; a jangada fica acima da linha das letras, contra o mar, sem disputar leitura com elas.

## 5. Organização técnica do arquivo

```
AP1_Ibmec_Conceito
├── 01_Palavra_Ibmec        LOGO_Palavra_Ibmec (pivô) → LOGO_Letra_01_i … 05_c, LOGO_Ponto_i
├── 02_Objetos_Autorais     OBJ_Farol_Mucuripe → Farol_Lanterna_Vidro
│                           OBJ_Jangada_Mucuripe → Jangada_Vela
│                           OBJ_Planetario_Dragao_do_Mar → Planetario_Rampa
├── 03_Cenario_Fortaleza    CEN_Mar_Atlantico, CEN_Praia_Beira_Mar, CEN_Deck_Mirante,
│                           CEN_Escadaria_Deck, CEN_Rochedo_Farol, CEN_Coqueiro_01…03
└── 04_Camera_e_Auxiliares  CAM_Principal, CAM_Alvo_Principal, CAM_SB1…SB3, LUZ_Sol_Fortaleza
```

Prefixos: `LOGO_` palavra · `OBJ_` objeto autoral · `CEN_` cenário · `CAM_` câmera · `MAT_` material · `MOD_` modificador.

**Timeline:** 24 fps, frames 1 a 360 = **15 segundos exatos**, com marcadores em 1, 121, 241 e 360 correspondendo aos três momentos do storyboard.

## 6. Plano para a AP2

| Frente | O que será feito |
| --- | --- |
| Animação da câmera | keyframes ligando as três posições de storyboard já criadas (`CAM_SB1` → `CAM_SB2` → `CAM_Principal`), com interpolação Bezier e ease-in/ease-out |
| Animação do pingo | `LOGO_Ponto_i` nasce no horizonte, sobe e desce até encaixar no “i” — o keyframe final já está na posição correta |
| Animação das letras | entrada escalonada de i, b, m, e, c subindo do deck, com defasagem de ~6 frames entre elas |
| Objetos autorais | jangada navegando com balanço no eixo Y, vela oscilando via `Simple Deform`, feixe do farol girando |
| Cenário | o modificador **Wave** do mar já anima sozinho com o tempo; só será ajustada a velocidade |
| Iluminação | sol animado do nascer ao dia claro, luz emissiva em `Farol_Lanterna_Vidro`, World com gradiente de céu |
| Materiais e texturas | rugosidade/reflexo no mar, textura de areia e de madeira, verniz nas letras |
| Render | Eevee Next, 1920×1080, 24 fps, 360 frames, saída em MP4 (H.264) |

## 7. Como reproduzir

```bash
# 1. Abrir o Blender 4.5 LTS
# 2. Aba Scripting > Open > AP1_IgorMariano.py > Run Script  (monta a cena inteira)
# 3. Aba Scripting > Open > AP1_capturas.py     > Run Script  (gera as 8 imagens)
```

O script é idempotente: rodar de novo apaga e reconstrói a coleção `AP1_Ibmec_Conceito` sem gerar duplicatas `.001`.

## 8. Checklist dos requisitos da AP1

| # | Requisito | Onde é atendido |
| --- | --- | --- |
| 1 | Blender 4.5 LTS | script verifica `bpy.app.version` e avisa se for outra versão |
| 2 | Coleção `AP1_Ibmec_Conceito` organizada | quatro subcoleções numeradas |
| 3 | Palavra Ibmec em destaque e legível | 8,2 m de largura, centro do quadro, cores oficiais |
| 4 | Três objetos autorais nomeados | `OBJ_Farol_Mucuripe`, `OBJ_Jangada_Mucuripe`, `OBJ_Planetario_Dragao_do_Mar` |
| 5 | Translação, rotação e escala intencionais | seção 4 deste relatório |
| 6 | Dois ou mais recursos além de escala | 15 técnicas listadas na seção 4 |
| 7 | Câmera principal configurada | `CAM_Principal` com Track To e DOF já apontado para a palavra |
| 8 | 15 s a 24 fps = 360 frames | `frame_start = 1`, `frame_end = 360`, `fps = 24` |
| 9 | Storyboard com três momentos | [`AP1_Storyboard.md`](AP1_Storyboard.md) + três câmeras + marcadores na timeline |
