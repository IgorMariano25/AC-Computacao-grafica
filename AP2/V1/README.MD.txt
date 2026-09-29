AUDITÓRIO AP1 — MODELOS 3D PARA BLENDER 4.5 LTS

Reconstrução geométrica aproximada a partir das quatro fotografias fornecidas.
São malhas 3D editáveis: é possível mudar o ponto de vista, mover objetos e editar
vértices. As imagens de prévia foram renderizadas dessas mesmas malhas.

COMEÇAR — IMPORTAÇÃO DIRETA
1. Extraia o ZIP para uma pasta.
2. No Blender: File > Import > glTF 2.0 (.glb/.gltf).
3. Selecione Auditorio_AP1.glb.
4. Pressione Home na janela 3D para enquadrar a cena.
5. Ative Material Preview para ver as cores e texturas.
6. Salve como .blend em File > Save As.
Não é necessário instalar extensões ou localizar texturas: todas estão no GLB.

ARQUIVOS 3D
- Auditorio_AP1.glb: ambiente completo, mobiliário, teto e detalhes.
- Pulpito_Curvo.glb: púlpito independente, com base, rodízios, tampo de madeira,
  corpo curvo, perfurações reais na face frontal e identificação recriada.
- Poltrona_Azul.glb: poltrona independente, voltada para -Y no Blender, com
  estofamento, braços, estrutura, pés e carenagem traseira.
- Palco_Completo.glb: palco, fundo ripado, telão, painéis, púlpito, mesa e bandeiras.
  Mantém as posições do auditório, para reutilização por partes.
Importe o auditório OU o palco completo no mesmo espaço para evitar sobreposição.

CÂMERAS, LUZES E COLEÇÕES — OPCIONAL
O GLB contém a geometria, materiais e hierarquia. Para preparar uma cena com
câmeras e luzes:
1. Abra o espaço Scripting no Blender.
2. No Text Editor, escolha Open e abra Preparar_Blender.py.
3. Clique Run Script / Alt+P e escolha Auditorio_AP1.glb no seletor de arquivos.
4. O script cria uma NOVA cena, preservando a cena anterior, e importa o modelo.
5. NumPad 0: câmera principal. F12: renderização Cycles. File > Save As: .blend.
Execute o script uma vez para cada nova cena desejada. Ele não precisa ser usado
se você já importou o GLB e prefere configurar o projeto manualmente.
As luzes são uma configuração inicial; ajuste exposição e energia a seu gosto.

ORGANIZAÇÃO
01_Arquitetura: paredes, piso principal, portas.
02_Palco: plataforma, revestimento ripado, tela e painéis.
03_Plateia_pisos: patamares, circulação, rampa e vagas acessíveis.
04_Poltronas: 195 objetos individuais que compartilham a mesma malha.
05_Pulpito: púlpito curvo.
06_Detalhes: corrimãos e extintores.
07_Mesa_e_bandeiras: mesa, laptop, cadeiras e bandeiras.
08_Fundos: parede traseira separada.
09_Teto: forro modular, luminárias e grelhas.

Na importação direta esses grupos aparecem como objetos pais no Outliner.
O script opcional transforma a organização também em coleções do Blender.
Para cortes, oculte o teto e a parede traseira; as paredes laterais podem ser
ocultadas pelo objeto Paredes_laterais. Para revelar a plateia por cima, selecione
os objetos desejados e pressione H; Alt+H os mostra novamente no viewport.

As poltronas usam uma malha compartilhada para economizar memória. Alterar a
posição de uma poltrona não move as outras. Para editar a geometria de apenas uma,
use Object > Relations > Make Single User > Object & Data antes de editar.

ESCALA E LIMITES
Unidade: metro. Interior estimado: 14,60 m × 20,80 m; forro a 4,20 m.
Palco: 0,55 m de altura. Plateia: 12 fileiras de 16 poltronas, mais 3 frontais.
Esses valores organizam a representação e NÃO são medidas ou capacidade
confirmadas do auditório. Não houve levantamento, planta, calibração de lente ou
fotogrametria. A perspectiva panorâmica das referências impede medições exatas.
O número de fileiras/assentos, níveis, portas e detalhes não visíveis foi estimado.
Identificação Ibmec foi recriada com tipografia aproximada. Bandeiras e brasões
foram simplificados. Materiais são aproximações de tecido, carpete, madeira,
metal e plástico. Não foram incluídas pessoas nem marcas de navegação das fotos.
A rampa e vagas acessíveis são representações visuais, sem validação normativa.

PRÉVIAS E VERIFICAÇÃO
Previa_01_Palco.png / Previa_02_Plateia.png: vistas internas.
Previa_03_Corte.png: visão geral sem teto, laterais e parede traseira.
Previa_04_Pulpito.png / Previa_05_Poltrona.png: modelos separados.
As prévias usam renderização técnica simples; a iluminação será diferente no
Blender. Os arquivos GLB foram relidos e verificados para integridade estrutural,
índices de triângulos, normais, valores finitos e texturas incorporadas.
Não foi possível executar o Blender neste ambiente. O script opcional teve sua
sintaxe verificada, mas a importação e o render no Blender 4.5 não foram testados.
Não há arquivo .blend pré-gerado; os GLB são os modelos prontos para importar.
