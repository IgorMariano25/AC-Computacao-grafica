# AP1 — Storyboard · “Do Mucuripe ao Futuro”

**Duração:** 15 s · **24 fps** · **frames 1 a 360** · **1920×1080**
**Câmeras já criadas no `.blend`:** `CAM_SB1_Amanhecer`, `CAM_SB2_Construcao`, `CAM_SB3_Assinatura`, `CAM_Principal`
**Marcadores na timeline:** `SB1_Amanhecer_no_Mucuripe@1` · `SB2_Construcao_da_Palavra@121` · `SB3_Assinatura_Ibmec@241` · `Fim_15s@360`

As imagens de cada momento são geradas por [`AP1_capturas.py`](AP1_capturas.py) em `saida/06_`, `saida/07_` e `saida/08_`.

---

## Momento 1 — Amanhecer no Mucuripe · 0 s a 5 s (frames 1–120)

**Câmera:** `CAM_SB1_Amanhecer` — quase na altura da água, lente 50 mm, olhando o horizonte.

**Quadro:** só mar, céu e a silhueta da jangada navegando da direita para a esquerda. O farol aparece recortado no canto esquerdo, com a lanterna ainda acesa. Nenhuma letra em cena.

**Ação:** um ponto amarelo começa a subir na linha do horizonte — é o objeto `LOGO_Ponto_i`. O espectador lê como o sol nascendo.

**Intenção:** estabelecer lugar e hora. Fortaleza antes de qualquer marca.

**Na AP2:** keyframes de translação em Z do `LOGO_Ponto_i`; jangada transladando em X com balanço leve em Y; `Simple Deform` da vela oscilando; céu do World indo de azul-noite para laranja.

---

## Momento 2 — A construção da palavra · 5 s a 10 s (frames 121–240)

**Câmera:** `CAM_SB2_Construcao` — três quartos pela esquerda, lente 45 mm, a meia altura, revelando o deck-mirante.

**Quadro:** a câmera sai do mar e encontra o deck de concreto sobre a areia. O sol já está alto, à direita do quadro, esperando.

**Ação:** as cinco letras sobem da plataforma em sequência — **i, b, m, e, c** — com defasagem de cerca de 6 frames entre elas, como peças de uma construção sendo erguidas. A palavra ainda está incompleta: falta o pingo do “i”.

**Intenção:** mostrar solidez e construção. A marca não cai pronta do céu, ela é erguida.

**Na AP2:** keyframes de `location.z` e `scale` de cada `LOGO_Letra_*`, com ease-out; movimento da câmera interpolando de `CAM_SB1` para `CAM_SB2`.

---

## Momento 3 — A assinatura Ibmec · 10 s a 15 s (frames 241–360)

**Câmera:** `CAM_SB3_Assinatura` resolvendo no enquadramento de `CAM_Principal` — frontal, lente 35 mm, com o farol à esquerda, o planetário à direita e a jangada ao fundo.

**Quadro:** o enquadramento principal da peça, com a palavra **ibmec** ocupando o centro e pouco mais da metade da largura do quadro.

**Ação:** o sol desce da linha do horizonte, atravessa o quadro e **encaixa no lugar do pingo do “i”**. No instante do encaixe, a lanterna do farol dá um último varrimento de luz sobre as letras. A peça congela no lock-up da marca pelos últimos ~2 s.

**Intenção:** a virada de leitura. O que era paisagem vira logotipo: o sol de Fortaleza é o pingo do “i” do Ibmec.

**Na AP2:** trajetória do `LOGO_Ponto_i` em arco até a posição final (que já é a posição atual dele no arquivo); emissão pulsando em `Farol_Lanterna_Vidro`; câmera parando suavemente; possível fade final.

---

## Linha do tempo resumida

| Frames | Tempo | Momento | Câmera | Evento-chave |
| --- | --- | --- | --- | --- |
| 1–120 | 0–5 s | Amanhecer no Mucuripe | `CAM_SB1_Amanhecer` | o sol (pingo do “i”) nasce sobre o mar |
| 121–240 | 5–10 s | Construção da palavra | `CAM_SB2_Construcao` | as cinco letras sobem do deck |
| 241–330 | 10–13,75 s | Assinatura | `CAM_SB3` → `CAM_Principal` | o sol encaixa como pingo do “i” |
| 331–360 | 13,75–15 s | Lock-up | `CAM_Principal` | marca completa, luz do farol passando |
