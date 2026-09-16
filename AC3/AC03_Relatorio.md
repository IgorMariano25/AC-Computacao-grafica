# AC03 - Texto de entrega

**Disciplina:** Computação Gráfica I · **Professor:** Jonh Edson
**Atividade:** [`AC03.md`](AC03.md) — Estudo Dirigido 03: transformações geométricas 2D e 3D no Blender 4.5 LTS.

## Arquivos da entrega

| Arquivo | Conteúdo |
|---|---|
| [`AC03_IgorMariano.blend`](AC03_IgorMariano.blend) | cena "Parque Geométrico" (Blender 4.5 LTS, header `BLENDER-v405`) |
| [`AC03_IgorMariano.py`](AC03_IgorMariano.py) | script que cria os objetos, transforma, anima e monta câmera e luz |
| [`AC03_IgorMariano_cena_inicial.png`](AC03_IgorMariano_cena_inicial.png) | render da cena no frame 1 (1920×1080) |
| [`AC03_IgorMariano_cena_final.png`](AC03_IgorMariano_cena_final.png) | render da cena no frame 120 (1920×1080) |
| [`AC03_Questoes_Teoricas.md`](AC03_Questoes_Teoricas.md) | respostas às cinco questões teóricas |

Os dois renders são o mesmo enquadramento de câmera em frames diferentes, e é a
comparação entre eles que mostra a animação: o cubo (à esquerda) saiu de uma forma
alongada para uma quase cúbica, mudando escala e orientação ao mesmo tempo, e o
círculo transladou em X levando o triângulo junto por herança.

| Frame 1 | Frame 120 |
|---|---|
| ![Cena inicial](AC03_IgorMariano_cena_inicial.png) | ![Cena final](AC03_IgorMariano_cena_final.png) |

## O que foi aplicado

A cena reúne três elementos 2D no plano XY (`obj2d_quadrado`, `obj2d_triangulo` e
`obj2d_circulo`) e três sólidos 3D (`obj3d_cubo`, `obj3d_cilindro` e
`obj3d_esfera`), todos dentro da coleção `AC03_transformacoes`.

Nos objetos 2D apliquei translação em X e Y, rotação em Z (30°, 45° e 15°) e
escala não uniforme em X/Y, mantendo Z inalterado por serem planos. Nos objetos 3D
apliquei translação nos três eixos, rotação combinada em X, Y e Z (por exemplo, o
cubo em 25°/15°/40°) e escala distinta por eixo, o que evidencia a diferença visual
entre rotacionar em eixos diferentes.

A animação vai do frame 1 ao 120 a 24 fps (5 segundos): o círculo translada em X e
rotaciona 180° em Z, enquanto o cubo escala e rotaciona simultaneamente em eixos
diferentes. Como bônus, o triângulo é filho do círculo (parent/child), herdando a
transformação composta, e as curvas usam easing `EASE_IN_OUT` com um keyframe
intermediário no frame 60.

## Manual x Python

A parte feita por Python foi a criação de todos os objetos, as transformações
numéricas, a hierarquia, os keyframes, a câmera e a luz — tudo em
[`AC03_IgorMariano.py`](AC03_IgorMariano.py), usando `math.radians()` para converter
os ângulos de graus para radianos. A parte manual, feita pela interface do Blender,
foi o ajuste fino de enquadramento com `G` e `R`, a conferência das transformações
no viewport e a geração dos dois renders com `F12`.

## Referências

* **Material da disciplina:** `aula04/tg2d3d.pdf` e `aula05/tg3d.md` (teoria das transformações 2D/3D) · `aula04/Aula5.Ex3–Ex6` (cubo, pirâmide, cilindro e esfera em 3D) · `blender/blender.md` e `blender/modelagem.md` · `blender/scripts/02_cube_transform.py`, `05_rotation_scale_animation.py`, `08_parenting_hierarchy.py` e `09_render_sequence.py` (base direta da automação, da animação, da hierarquia e do render)
* **Externas:** [Blender Python API (`bpy`)](https://docs.blender.org/api/current/) · [Blender Manual](https://docs.blender.org/manual/en/latest/)
