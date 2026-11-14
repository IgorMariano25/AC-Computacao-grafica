# Selecao automatica de GPU para a AP2

Estado desta etapa: script preparado; o AP2_IgorMariano.blend ainda permanece
na versao anterior, configurada para CPU. Nenhum Blender foi executado localmente.

O script scripts/selecionar_gpu.py consulta os dispositivos reconhecidos pelo
Cycles e procura todos os backends suportados:
- NVIDIA: OptiX ou CUDA.
- AMD: HIP.
- Intel: oneAPI.
- Apple: Metal.

A compatibilidade depende do modelo, do sistema operacional, da versao do
Blender e dos drivers. Nao e possivel garantir suporte a qualquer placa existente.
Se houver varias opcoes, a prioridade e OptiX, CUDA, HIP, oneAPI e Metal.
O Cycles utiliza um backend por vez. O script ativa as GPUs desse backend,
desativa CPU como dispositivo Cycles e muda as cenas Cycles para GPU Compute.
Se nao houver GPU compativel, informa o problema e restaura as preferencias anteriores.

## No computador que vai renderizar

1. Abra AP2_IgorMariano.blend.
2. Abra Scripting > Text > Open e escolha scripts/selecionar_gpu.py.
3. Clique Run Script. Uma mensagem mostra o backend e as placas selecionadas.
4. Salve o .blend para manter GPU Compute no projeto. O script salva as
   preferencias de hardware da instalacao, mas nao salva o projeto nem inicia render.
5. Confira um frame de teste antes de renderizar a animacao completa.

O script nao e executado automaticamente ao abrir o .blend. Precisa ser
executado no computador de renderizacao, pois as placas disponiveis sao locais
a esse computador. A deteccao e automatica depois de clicar Run Script.

