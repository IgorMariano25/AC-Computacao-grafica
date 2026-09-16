# AC03 - Questões Teóricas

**Disciplina:** Computação Gráfica I · **Professor:** Jonh Edson
**Atividade:** [`AC03.md`](AC03.md) · **Entrega:** [`AC03_Relatorio.md`](AC03_Relatorio.md) · **Script:** [`AC03_IgorMariano.py`](AC03_IgorMariano.py)

## 1. Explique a diferença entre translação, rotação e escala em computação gráfica.

- **Translação**: desloca um objeto de uma posição para outra no espaço, somando um vetor de deslocamento às coordenadas de todos os seus pontos, sem alterar sua forma, tamanho ou orientação.
- **Rotação**: gira o objeto em torno de um eixo (em 3D) ou de um ponto (em 2D), alterando sua orientação, mas preservando forma e tamanho.
- **Escala**: multiplica as coordenadas dos pontos do objeto por um fator, alterando seu tamanho (e podendo alterar suas proporções, se os fatores forem diferentes por eixo). Forma e orientação são mantidas, mas as dimensões mudam.

Essas três operações são transformações geométricas lineares (afins) fundamentais, geralmente representadas por matrizes, e podem ser combinadas para posicionar e ajustar objetos em uma cena.

## 2. Qual é a diferença entre transformar um objeto no espaço local e no espaço global?

- **Espaço local**: as transformações são aplicadas em relação ao próprio sistema de coordenadas do objeto (sua origem e seus eixos locais). Por exemplo, rotacionar no eixo Z local gira o objeto em torno do seu próprio eixo, independentemente de como ele está orientado na cena.
- **Espaço global**: as transformações são aplicadas em relação ao sistema de coordenadas do mundo (a cena como um todo). Rotacionar no eixo Z global gira o objeto em torno do eixo Z fixo da cena, o que pode produzir um resultado diferente se o objeto já estiver rotacionado localmente.

A diferença fica evidente quando o objeto já sofreu alguma rotação: uma nova transformação local segue a orientação atual do objeto, enquanto uma transformação global ignora essa orientação e usa os eixos fixos do mundo.

## 3. Em uma cena 3D, por que rotações em eixos diferentes podem gerar resultados visuais distintos?

Porque rotações em 3D não são comutativas: a ordem e o eixo em que são aplicadas alteram o resultado final. Rotacionar primeiro em X e depois em Y produz uma orientação diferente de rotacionar primeiro em Y e depois em X, já que cada rotação modifica os eixos de referência para a rotação seguinte. Além disso, cada eixo (X, Y, Z) representa um "giro" em um plano diferente (YZ, XZ e XY, respectivamente), então rotacionar em eixos distintos afeta partes diferentes da geometria, gerando aparências visuais diferentes mesmo com os mesmos ângulos.

## 4. No Blender, por que usar `math.radians()` ao definir `rotation_euler` por script?

Porque internamente o Blender (assim como a maioria das bibliotecas gráficas e a API do Python) trabalha com ângulos em **radianos**, não em graus. Como é mais intuitivo pensar e especificar ângulos em graus (ex.: 90°, 45°), a função `math.radians()` converte esse valor em graus para o equivalente em radianos antes de atribuí-lo a `rotation_euler`. Sem essa conversão, o valor seria interpretado diretamente como radianos, resultando em rotações com ângulos muito maiores (ou menores) do que o pretendido.

## 5. Dê um exemplo prático de quando vale mais a pena usar Python em vez de transformar manualmente pela interface.

Um exemplo prático é a criação de uma cena com múltiplos objetos que seguem um padrão repetitivo, como posicionar 50 cópias de um mesmo objeto em formato de grade ou círculo, cada uma com uma rotação e escala ligeiramente diferentes. Fazer isso manualmente pela interface seria demorado, repetitivo e propenso a erros de precisão. Com Python, é possível usar um laço `for` para calcular automaticamente as posições, rotações e escalas de cada objeto com precisão matemática, além de poder reexecutar o script facilmente caso seja necessário ajustar algum parâmetro (como a quantidade de objetos ou o espaçamento entre eles).

Na própria AC03 isso aparece em escala menor: em [`AC03_IgorMariano.py`](AC03_IgorMariano.py) toda a cena é reconstruída do zero a cada execução, então corrigir um ângulo é editar uma linha e rodar de novo — pela interface, seria refazer o posicionamento de seis objetos à mão.

---

## Referências

* **Material da disciplina:** `aula04/tg2d3d.pdf` (transformações 2D/3D e coordenadas homogêneas) · `aula05/tg3d.md` (matrizes 4×4 e rotação por eixo) · `blender/blender.md` (espaço local x global na interface) · `blender/scripts/02_cube_transform.py` e `08_parenting_hierarchy.py`
* **Externas:** [Blender Python API — `Object.rotation_euler`](https://docs.blender.org/api/current/bpy.types.Object.html) · [Blender Manual — Transformações](https://docs.blender.org/manual/en/latest/scene_layout/object/editing/transform/index.html) · [`math.radians`](https://docs.python.org/3/library/math.html#math.radians)
