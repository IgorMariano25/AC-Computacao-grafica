"""Gera mapas de imagem autorais e repetíveis; não executa Blender.
Requer numpy. PNG codificado pela biblioteca padrão; sem fotografias externas.
"""
from pathlib import Path
import json, struct, zlib
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

def main():
    target = ROOT / 'texturas'
    target.mkdir(exist_ok=True)
    n = 1024
    y, x = np.mgrid[0:n, 0:n] / n
    # Funções periódicas: bordas correspondentes, veios verticais em V.
    grain = .5 + .30*np.sin(2*np.pi*(19*x+.24*np.sin(2*np.pi*y)))
    grain += .12*np.sin(2*np.pi*(71*x+.12*np.sin(4*np.pi*y)))
    grain += .07*np.sin(2*np.pi*(157*x+.05*np.sin(6*np.pi*y)))
    grain = np.clip(grain,0,1)
    brush = .5 + .22*np.sin(2*np.pi*96*y) + .22*np.sin(2*np.pi*96*x)
    brush = np.clip(brush,0,1)
    def save(name, arr):
        data=np.uint8(np.clip(arr,0,1)*255+.5)
        channels=1 if data.ndim==2 else data.shape[2]
        def chunk(tag, content):
            return struct.pack('>I',len(content))+tag+content+struct.pack('>I',zlib.crc32(tag+content)&0xffffffff)
        raw=b''.join(b'\x00'+row.tobytes() for row in data)
        png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,0 if channels==1 else 2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
        (target/name).write_bytes(png)
    def normal(height, amplitude):
        # PNG primeira linha = V alto: derivada V inverte o eixo das linhas.
        du = (np.roll(height,-1,axis=1)-np.roll(height,1,axis=1))*n/2
        dv = -(np.roll(height,-1,axis=0)-np.roll(height,1,axis=0))*n/2
        v = np.stack((-du*amplitude,-dv*amplitude,np.ones_like(height)),axis=-1)
        v /= np.linalg.norm(v,axis=-1,keepdims=True)
        return .5+.5*v
    dark, light = np.array([.19,.075,.025]), np.array([.53,.30,.12])
    save('madeira_BaseColor.png',dark+(light-dark)*grain[:,:,None])
    save('madeira_Roughness.png',.38+.20*grain)
    save('madeira_Normal.png',normal(grain,.0015))
    save('tecido_BaseColor.png',np.repeat((.035+.045*brush)[:,:,None],3,axis=2))
    save('tecido_Roughness.png',.72+.15*brush)
    save('tecido_Normal.png',normal(brush,.00065))
    info = {'resolucao':[n,n], 'origem':'Algoritmos originais de scripts/gerar_texturas.py, preparados com assistência de IA para esta atividade.', 'licenca':'CC0-1.0 para os seis mapas gerados neste pacote; sem imagens de terceiros.', 'madeira':{'roughness':[.38,.58], 'metallic':0,'normal_strength':.25},'tecido':{'roughness':[.72,.87],'metallic':0,'normal_strength':.18},'cor':'BaseColor sRGB; Roughness e Normal Non-Color; Normal tangente OpenGL (+Y).'}
    (target/'FONTES_E_LICENCA.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__ == '__main__': main()
