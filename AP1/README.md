# AP1 — Auditório Ibmec (Conceito)

**Autor:** Igor Rodrigues — matrícula 202407095992

Modelagem 3D no Blender de um conjunto de objetos autorais relacionados a uma cena de auditório/formatura, entregue como composição estática (sem animação) para a AP1.

![Enquadramento principal](capturas/01_enquadramento_principal.png)

---

## Como abrir

1. Abra `AP1_IgorRodrigues.blend` no **Blender 4.5 LTS**.
2. Pronto — não é necessário rodar nenhum script para visualizar ou editar o arquivo.

## Visualização na cena

- O projeto abre posicionado na **Camera_Principal**, em shading Solid/Matcap cinza.
- `Numpad 0` alterna a view para a câmera principal.
- `F12` gera uma imagem estática usando o motor Workbench.
- Os *overlays* (seleção, origens, guias) ficam ocultos por padrão para apresentar o modelo limpo. Ative-os manualmente se for editar a cena.

## Objetos autorais

Estão organizados na coleção `AP1_Ibmec_Conceito > Objetos_Autorais`:

| Objeto | Descrição |
|---|---|
| `Objeto_A_Pulpito_Pitch` | Púlpito de apresentação |
| `Objeto_B_Capelo_Formatura` | Capelo de formatura |
| `Objeto_C_Diploma_Ibmec` | Diploma/folha enrolada |

| Púlpito | Capelo | Diploma |
|---|---|---|
| ![Púlpito](capturas/02_pulpito_pitch.png) | ![Capelo](capturas/03_capelo_formatura.png) | ![Diploma](capturas/04_diploma_ibmec.png) |

## Marca Ibmec

O objeto `Marca_Ibmec` reaproveita a curva original de `Logo-Ibmec-3D.blend`. A forma da curva foi preservada; apenas posição, orientação e escala uniforme foram ajustadas para se encaixar na composição. Os materiais estão em cinza neutro, adequado à etapa inicial da AP1.

## Relação AP1 → AP2

Esta entrega é **estática** (sem keyframes):

- A timeline usa **24 fps**, do frame **1 ao 360**.
- Os marcadores na timeline apenas registram o planejamento já pensado para a AP2 — não há animação ainda.
- As câmeras de detalhe existem para visualizar os objetos individualmente e gerar as capturas de imagem.
- O arquivo de origem `Auditorio_AP2(2).blend` **não** precisa ser substituído por este.

## Relatório e imagens

Abra `Relatorio_AP1_IgorRodrigues.md` mantendo as pastas ao lado dele:

- `capturas/` — renders retirados diretamente do arquivo Blender.
- `conceito/` — guias ilustrativos de referência conceitual (identificados como tal no relatório).
- `referencias/` — imagens de referência visual usadas no processo de modelagem.

## Detalhes técnicos de modelagem

- As três malhas autorais usam **grupos de vértices** para identificar seus componentes.
- Púlpito e capelo mantêm o modificador **Bevel editável**.
- A espessura da folha do diploma e do canudo foi aplicada (Solidify) **antes** da união das malhas.
- A folha do diploma pode ser separada usando o grupo de vértices `Folha_Diploma`, útil para desenvolver a animação na AP2.

