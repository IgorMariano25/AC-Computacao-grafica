# AP1 — “Do Mucuripe ao Futuro” · Ibmec Fortaleza

Cena-conceito da peça de 15 s pedida na [AP1](AP1.md), construída **inteiramente por script** no Blender 4.5 LTS.

| Arquivo | O que é |
| --- | --- |
| [`AP1_IgorMariano.py`](AP1_IgorMariano.py) | script principal — monta a cena inteira do zero |
| [`AP1_capturas.py`](AP1_capturas.py) | gera as 8 imagens dos entregáveis (render Workbench, ~1 s cada) |
| [`AP1_Relatorio.md`](AP1_Relatorio.md) | relatório: conceito, objetos autorais, técnicas, plano da AP2 |
| [`AP1_Storyboard.md`](AP1_Storyboard.md) | storyboard com os três momentos da peça |

## Como rodar

1. Abra o **Blender 4.5 LTS** (arquivo novo, ou o `AP1-Logo-Ibmec-3D.blend` se quiser reaproveitar os materiais oficiais).
2. Aba **Scripting** → **Open** → `AP1_IgorMariano.py` → **Run Script** (`Alt+P`).
3. Salve como `AP1_IgorMariano.blend`.
4. Aba **Scripting** → **Open** → `AP1_capturas.py` → **Run Script** — as imagens saem em `saida/`.

No Windows, as mensagens do script aparecem em **Window → Toggle System Console**.

## Ajustes rápidos

Tudo que costuma precisar de ajuste está no bloco `0. CONFIGURACAO`, no topo de `AP1_IgorMariano.py`:

| Constante | Para quê |
| --- | --- |
| `CAMINHO_SVG_LOGO` | caminho do `Ibmec-letras-separadas.svg`; se preenchido, o script usa as **curvas oficiais** da marca no lugar do texto 3D |
| `CAMINHO_FONTE` | `.ttf` da fonte institucional; vazio faz o script procurar uma fonte adequada no sistema |
| `LARGURA_PALAVRA` | largura da palavra em metros (8,2 é o valor calculado para o enquadramento atual) |
| `HEX_AZUL_IBMEC` / `HEX_AMARELO_IBMEC` | cores da marca — já preenchidas com os valores lidos do `AP1-Logo-Ibmec-3D.blend` |
| `SALVAR_BLEND` / `CAMINHO_BLEND` | salvar o arquivo automaticamente ao final |

Se os materiais `Azul Ibmec` e `Amarelo Ibmec` já existirem no arquivo aberto, o script os **reaproveita** em vez de criar cores novas.

## Cores da marca

Extraídas do `AP1-Logo-Ibmec-3D.blend`:

| Material | sRGB | Linear (Blender) |
| --- | --- | --- |
| Azul Ibmec | `#002555` | `(0.0000, 0.0185, 0.0908)` |
| Amarelo Ibmec | `#F5AC00` | `(0.9131, 0.4125, 0.0000)` |

## Estrutura da cena

```
AP1_Ibmec_Conceito
├── 01_Palavra_Ibmec        pivô + 5 letras + pingo do "i" (objetos separados)
├── 02_Objetos_Autorais     farol · jangada · planetário (os três autorais)
├── 03_Cenario_Fortaleza    mar · praia · deck · escadaria · rochedo · coqueiros
└── 04_Camera_e_Auxiliares  câmera principal + alvo + 3 câmeras de storyboard + sol
```

Timeline: **24 fps, frames 1–360 = 15 s exatos**.
