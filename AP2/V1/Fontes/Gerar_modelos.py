import os, math, json, struct, io, copy
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from collections import defaultdict
from pathlib import Path
ROOT=str(Path(__file__).resolve().parent / 'gerado')
OUT=ROOT+'/auditorio_ap1'
os.makedirs(OUT,exist_ok=True)
os.makedirs(ROOT+'/work',exist_ok=True)
PI=math.pi
materials=[];textures=[]; meshes=[]; objects=[]
def texture(name,img):
    s=io.BytesIO();img.save(s,format='PNG');textures.append((name,s.getvalue()));return len(textures)-1
def mat(name,col,rough=.6,metal=0,tex=None):
    d={'name':name,'pbrMetallicRoughness':{'baseColorFactor':[*col,1],'metallicFactor':metal,'roughnessFactor':rough},'doubleSided':True}
    if tex is not None:d['pbrMetallicRoughness']['baseColorTexture']={'index':tex}
    materials.append(d);return len(materials)-1
rng=np.random.default_rng(51)
def grain(col,amt,size=256):
    a=np.clip(np.array(col)[None,None,:]+rng.normal(0,amt,(size,size,1)),0,255).astype('uint8');return Image.fromarray(a)
tex_carpet=texture('Carpete_cinza',grain([141,148,158],14))
tex_cloth=texture('Tecido_azul',grain([27,71,117],9))
a=np.zeros((256,512,3));noise=rng.normal(0,4,(256,512,1));v=np.arange(256)[:,None,None];a[:]=[169,119,56];a+=noise+9*np.sin(v*.55)+5*np.sin(v*.21);tex_wood=texture('Madeira_mel',Image.fromarray(np.clip(a,0,255).astype('uint8')))
font='/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf';fontb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def logo_img(w=1024,h=300):
    im=Image.new('RGB',(w,h),(19,38,100));d=ImageDraw.Draw(im)
    d.rectangle((20,20,215,h-20),fill=(244,195,13))
    d.text((69,-8),'i',font=ImageFont.truetype(font,270),fill='white')
    d.text((242,58),'Ibmec',font=ImageFont.truetype(font,188),fill='white')
    return im
tex_logo=texture('Ibmec_recriado',logo_img())
banner=Image.new('RGB',(768,1280));b=np.zeros((1280,768,3));yy=np.linspace(0,1,1280)[:,None,None];b[:]=[9,28,82];b+=(1-yy)*np.array([18,31,57]);b+=rng.normal(0,1.5,(1280,768,1));banner=Image.fromarray(np.clip(b,0,255).astype('uint8'));d=ImageDraw.Draw(banner);banner.paste(logo_img(1024,300).resize((610,179)),(79,106));d.line((75,397,693,397),fill=(172,142,71),width=3);d.text((78,435),'BARRA',font=ImageFont.truetype(fontb,25),fill=(220,225,237));d.text((78,496),'Ibmec  |  Conhecimento',font=ImageFont.truetype(font,25),fill=(220,225,237));tex_banner=texture('Painel_azul_recriado',banner)
# Flag approximations: crests not reconstructed.
flag=Image.new('RGB',(320,448),(20,99,49));d=ImageDraw.Draw(flag);d.polygon([(160,55),(290,224),(160,393),(30,224)],fill=(245,199,22));d.ellipse((89,151,231,297),fill=(22,55,130));d.arc((82,190,239,270),195,345,fill='white',width=9);tex_br=texture('Bandeira_Brasil_estilizada',flag)
flag2=Image.new('RGB',(320,448),(241,241,238));d=ImageDraw.Draw(flag2);d.rectangle((0,0,160,224),fill=(73,146,195));d.rectangle((160,224,320,448),fill=(73,146,195));d.ellipse((116,170,204,278),fill=(163,71,46));tex_rj=texture('Bandeira_RJ_estilizada',flag2)
flag3=Image.new('RGB',(320,448),(233,235,238));d=ImageDraw.Draw(flag3);d.polygon([(0,0),(320,448),(320,365),(66,0)],fill=(48,143,193));tex_city=texture('Terceira_bandeira_estilizada',flag3)
wall=mat('Paredes_marfin',(.87,.86,.81),.9);carpet=mat('Carpete_cinza',(1,1,1),.98,tex=tex_carpet);cloth=mat('Estofado_azul',(1,1,1),.95,tex=tex_cloth);wood=mat('Madeira_mel',(1,1,1),.6,tex=tex_wood);black=mat('Plastico_antracite',(.028,.033,.038),.46);metal=mat('Metal_preto',(.035,.042,.048),.32,.7);screen=mat('Tela_branca',(.94,.94,.91),.96);blue=mat('Azul_institucional',(.025,.055,.2),.7);logo=mat('Ibmec', (1,1,1),.65,tex=tex_logo);banmat=mat('Painel_Ibmec',(1,1,1),.8,tex=tex_banner);yellow=mat('Amarelo_sinalizacao',(.95,.73,.04),.6);white=mat('Branco_sinalizacao',(.92,.92,.85),.65);chrome=mat('Aco_cromado',(.5,.56,.61),.23,.85);gold=mat('Ponta_bandeira',(.72,.45,.10),.3,.65);red=mat('Extintor_vermelho',(.65,.026,.018),.4);green=mat('Sinal_saida',(.018,.25,.10));lightmat=mat('Difusor_luminaria',(.94,.96,1),.4);materials[lightmat]['emissiveFactor']=[.75,.79,.86]
flagmats=[mat('Bandeira_'+n,(1,1,1),.9,tex=t) for n,t in [('Brasil',tex_br),('RJ_simplificada',tex_rj),('Terceira_simplificada',tex_city)]]
class Mesh:
 def __init__(self,name):self.name=name;self.parts=defaultdict(lambda:[[],[],[],[]])
 def add(self,verts,faces,ma,normals=None,uv=None):
    V=np.array(verts,float);F=np.array(faces,int)
    if normals is None:
      # Split faces for flat normals.
      V=V[F].reshape(-1,3);F=np.arange(len(V)).reshape(-1,3);N=np.cross(V[F[:,1]]-V[F[:,0]],V[F[:,2]]-V[F[:,0]]);N/=np.maximum(np.linalg.norm(N,axis=1)[:,None],1e-10);N=np.repeat(N,3,axis=0);U=np.zeros((len(V),2)) if uv is None else np.array(uv)[np.array(faces)].reshape(-1,2)
    else:N=np.array(normals);U=np.zeros((len(V),2)) if uv is None else np.array(uv)
    p=self.parts[ma];base=len(p[0]);p[0].extend(V.tolist());p[1].extend(N.tolist());p[2].extend(U.tolist());p[3].extend((F+base).tolist())
 def finish(self):meshes.append(self);return len(meshes)-1

def Rx(a):c,s=math.cos(a),math.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def Rz(a):c,s=math.cos(a),math.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def box(m,c,d,ma,r=0,rot=None):
 c=np.array(c);h=np.array(d)/2;R=np.eye(3) if rot is None else rot
 r=min(r,min(h)*.95)
 for axis in range(3):
  b=(axis+1)%3;e=(axis+2)%3
  for sign in [-1,1]:
   def vals(k):return np.array([-h[k],-h[k]+r*.293,-h[k]+r,h[k]-r,h[k]-r*.293,h[k]]) if r else np.array([-h[k],h[k]])
   vs=[];ns=[];us=[];bv=vals(b);ev=vals(e)
   for u in bv:
    for v in ev:
     p=np.zeros(3);p[axis]=h[axis]*sign;p[b]=u;p[e]=v
     if r:
      inner=np.clip(p,-h+r,h-r);n=p-inner;n/=np.linalg.norm(n);p=inner+n*r
     else:n=np.eye(3)[axis]*sign
     vs.append(R@p+c);ns.append(R@n);us.append((u*2,v*2))
   fs=[];ne=len(ev)
   for i in range(len(bv)-1):
    for j in range(ne-1):
     a=i*ne+j;f=[(a,a+ne,a+ne+1),(a,a+ne+1,a+1)];fs.extend(f if sign>0 else [tuple(reversed(x)) for x in f])
   m.add(vs,fs,ma,ns,us)
def quad(m,vs,ma,uv=None):m.add(vs,[(0,1,2),(0,2,3)],ma,uv=uv or [(0,1),(1,1),(1,0),(0,0)])
def cyl(m,a,b,r,ma,n=12,r2=None):
 a=np.array(a);b=np.array(b);d=b-a;d/=np.linalg.norm(d);u=np.cross(d,[1,0,0] if abs(d[0])<.8 else [0,1,0]);u/=np.linalg.norm(u);v=np.cross(d,u);r2=r if r2 is None else r2
 vs=[];ns=[]
 for p,rr in [(a,r),(b,r2)]:
  for i in range(n):
   nn=u*math.cos(2*PI*i/n)+v*math.sin(2*PI*i/n);vs.append(p+rr*nn);ns.append(nn)
 fs=[]
 for i in range(n):j=(i+1)%n;fs.extend([(i,j,j+n)] if r2==0 else [(i,j,j+n),(i,j+n,i+n)])
 m.add(vs,fs,ma,ns)
 m.add([a]+vs[:n],[(0,i+2,i+1) for i in range(n-1)]+[(0,1,n)],ma)
 if r2>0:m.add([b]+vs[n:],[(0,i+1,i+2) for i in range(n-1)]+[(0,n,1)],ma)
def path(m,points,r,ma):
 for a,b in zip(points,points[1:]):cyl(m,a,b,r,ma)
def obj(name,idx,loc=(0,0,0),angle=0,group='Mobiliario'):
 objects.append({'name':name,'mesh':idx,'loc':list(loc),'angle':angle,'group':group})
def done(m,group,loc=(0,0,0)):obj(m.name,m.finish(),loc,group=group)

# One complete, reusable upholstered auditorium seat, facing -Y.
m=Mesh('Poltrona_azul')
for x in [-.245,.245]:
 box(m,(x,0,.024),(.07,.64,.048),metal,.008)
 box(m,(x,.09,.21),(.052,.055,.38),metal,.006)
 box(m,(x,-.015,.40),(.065,.47,.04),metal,.005)
box(m,(0,-.06,.465),(.48,.45,.125),cloth,.045)
backR=Rx(math.radians(-10))
box(m,(0,.197,.80),(.51,.125,.62),black,.039,backR)
box(m,(0,.126,.81),(.465,.10,.56),cloth,.038,backR)
for z in np.linspace(.60,1.01,11):
 yy=.197+math.sin(math.radians(10))*(z-.80)+.071
 box(m,(0,yy,z),(.42,.013,.009),black,.003,backR)
for x in [-.292,.292]:
 box(m,(x,-.015,.43),(.065,.54,.45),cloth,.021)
 box(m,(x,-.015,.68),(.077,.555,.05),black,.012)
 # Side panel frame.
 box(m,(x,-.283,.43),(.074,.022,.45),black,.006)
chair=m.finish()
# 12 estimated rows, 8 seats per block.
for row in range(12):
 y=6.3+row*1.07;z=.10+row*.10
 for side in [-1,1]:
  for seat in range(8):obj(f'Poltrona_{"E" if side<0 else "D"}_{row+1:02}_{seat+1:02}',chair,(side*(1.15+seat*.67),y,z),group='04_Poltronas')
for i,x in enumerate([-5.8,-3.25,-1.05]):obj(f'Poltrona_frontal_{i+1}',chair,(x,4.86,0),group='04_Poltronas')
# Curved perforated lectern body.
m=Mesh('Pulpito_curvo')
box(m,(0,0,.08),(.76,.62,.045),black,.01)
for x in [-.285,.285]:
 for y in [-.21,.21]:cyl(m,(x-.027,y,.043),(x+.027,y,.043),.04,black,16)
def fy(t):return .16+.12*math.sin(PI*t)-.015*t
def pfront(x,t,off=0):return (x,fy(t)+off,.115+1.10*t)
# Solid curved side shells, open at the operator's rear.
for side in [-1,1]:
 for i in range(32):
  t=i/32;t1=(i+1)/32;x=side*.278
  quad(m,[(x,-.20,.115+1.1*t),(x,fy(t)+.012,.115+1.1*t),(x,fy(t1)+.012,.115+1.1*t1),(x,-.20,.115+1.1*t1)],black)
  quad(m,[(x-side*.024,-.20,.115+1.1*t),(x-side*.024,-.20,.115+1.1*t1),(x-side*.024,fy(t1)+.012,.115+1.1*t1),(x-side*.024,fy(t)+.012,.115+1.1*t)],black)
 for i in range(32):path(m,[pfront(x,i/32,.018),pfront(x,(i+1)/32,.018)],.012,metal)
# Actual perforations: rectangular cells with octagonal holes and inner walls.
cols=14;rows=32;xmin=-.25;wid=.5;tmin=.025;th=.95
for j in range(rows):
 for i in range(cols):
  cx=xmin+wid*(i+.5)/cols;ct=tmin+th*(j+.5)/rows;hx=wid/cols/2;ht=th/rows/2;rad=.0065
  outer=[(-hx,-ht),(0,-ht),(hx,-ht),(hx,0),(hx,ht),(0,ht),(-hx,ht),(-hx,0)]
  inner=[(-rad*.707,-rad*.707/1.1),(0,-rad/1.1),(rad*.707,-rad*.707/1.1),(rad,0),(rad*.707,rad*.707/1.1),(0,rad/1.1),(-rad*.707,rad*.707/1.1),(-rad,0)]
  for k in range(8):
   k1=(k+1)%8
   a,b=outer[k],outer[k1];c,d=inner[k1],inner[k]
   quad(m,[pfront(cx+a[0],ct+a[1]),pfront(cx+b[0],ct+b[1]),pfront(cx+c[0],ct+c[1]),pfront(cx+d[0],ct+d[1])],metal)
   quad(m,[pfront(cx+d[0],ct+d[1]),pfront(cx+c[0],ct+c[1]),pfront(cx+c[0],ct+c[1],-.007),pfront(cx+d[0],ct+d[1],-.007)],black)
box(m,(0,-.16,.66),(.46,.04,.05),black)
box(m,(0,-.05,1.235),(.76,.60,.043),wood,.009,Rx(math.radians(10)))
box(m,(0,-.057,1.201),(.69,.535,.028),wood,.007,Rx(math.radians(10)))
box(m,(0,-.325,1.20),(.67,.017,.023),wood,.003)
quad(m,[(-.19,fy(.82)+.022,1.00),(.19,fy(.82)+.022,1.00),(.19,fy(.82)+.01,1.115),(-.19,fy(.82)+.01,1.115)],logo)
podium=m.finish();obj('Pulpito_curvo_perfurado',podium,(-3.2,1.95,.55),group='05_Pulpito')

# Ground, raised stage, carpeted audience terraces and central ramp.
m=Mesh('Piso_base');box(m,(0,10.4,-.09),(14.6,20.8,.18),carpet);done(m,'01_Arquitetura')
m=Mesh('Palco');box(m,(0,1.9,.275),(12.7,3.5,.55),wood,.015);box(m,(0,1.9,.556),(12.72,3.52,.022),carpet)
for i in range(8):box(m,(0,3.66,.04+i*.068),(12.76,.055,.047),wood,.004)
done(m,'02_Palco')
m=Mesh('Arquibancada')
for row in range(12):
 z=.10+row*.10;y=6.3+row*1.07
 for side in [-1,1]:box(m,(side*3.92,y,(z-.025)/2),(6.14,1.07,z+.025),carpet)
# Smooth central circulation slope, matches terrace centers.
quad(m,[(-.86,5.76,.05),(.86,5.76,.05),(.86,18.66,1.255),(-.86,18.66,1.255)],carpet,[(0,0),(3,0),(3,24),(0,24)])
box(m,(0,19.73,.625),(14.6,2.14,1.25),carpet)
# Accessible side ramp rising to stage at y=0.6.
quad(m,[(6.4,.5,.56),(7.14,.5,.56),(7.14,6,0),(6.4,6,0)],carpet)
m.add([(6.4,.5,0),(6.4,6,0),(6.4,.5,.56)],[(0,1,2)],wood)
for side in [-1,1]:
 for i in range(23):box(m,(side*(.9+i*.265),5.774,.105),(.15,.095,.013),yellow if i%2==0 else black)
done(m,'03_Plateia_pisos')
# Accessible floor boxes (front left, matching reverse stage photograph).
m=Mesh('Vagas_acessiveis')
for x in [-4.5,-2.1]:
 box(m,(x,4.85,.008),(.91,1.28,.012),blue)
 for xx in [-.43,.43]:box(m,(x+xx,4.85,.018),(.02,1.22,.008),white)
 for yy in [-.59,.59]:box(m,(x,4.85+yy,.018),(.88,.02,.008),white)
 # Geometric wheelchair pictogram.
 pts=[(x+.18*math.cos(t),4.94+.18*math.sin(t),.027) for t in np.linspace(0,2*PI,33)];path(m,pts,.013,white)
 cyl(m,(x-.05,4.54,.027),(x-.05,4.54,.033),.056,white,16)
 path(m,[(x-.05,4.63,.03),(x-.05,4.89,.03),(x+.15,4.89,.03),(x+.29,5.10,.03),(x+.37,5.10,.03)],.015,white)
done(m,'03_Plateia_pisos')
# Architectural envelope and wood baseboards; backside and ceiling separately hideable.
m=Mesh('Paredes_laterais');
for side in [-1,1]:
 box(m,(side*7.39,10.4,2.1),(.18,20.8,4.2),wall)
 box(m,(side*7.275,10.4,.075),(.04,20.8,.15),wood)
done(m,'01_Arquitetura')
m=Mesh('Parede_palco');box(m,(0,-.1,2.1),(14.96,.2,4.2),wall);done(m,'01_Arquitetura')
m=Mesh('Parede_fundos');box(m,(0,20.91,2.1),(14.96,.18,4.2),wall);done(m,'08_Fundos')
# Screen and slatted back wall.
m=Mesh('Painel_ripado_e_tela')
for i in range(28):box(m,(0,.13,.62+i*.075),(7.95,.065,.054),wood,.003)
box(m,(0,.235,2.60),(3.95,.075,2.32),black,.006)
quad(m,[(-1.93,.284,1.48),(1.93,.284,1.48),(1.93,.284,3.72),(-1.93,.284,3.72)],screen)
cyl(m,(-2.1,.22,3.86),(2.1,.22,3.86),.075,screen,16)
for x in [-3.01,3.01]:
 box(m,(x,.305,1.71),(1.65,.07,2.30),blue,.005)
 quad(m,[(x-.825,.346,.56),(x+.825,.346,.56),(x+.825,.346,2.86),(x-.825,.346,2.86)],banmat)
done(m,'02_Palco')
# Doors with horizontal panic handles and exit signs.
m=Mesh('Portas_e_sinalizacao')
for x,y,z,w in [(-5.45,.035,.56,1.70),(0,20.78,1.25,1.75)]:
 face=1 if y<1 else -1
 box(m,(x,y,z+1.06),(w+.13,.10,2.18),wood,.005)
 for side in [-1,1]:
  xx=x+side*w/4;box(m,(xx,y+face*.062,z+1.035),(w/2-.025,.07,2.07),wood,.006)
  cyl(m,(xx-w*.19,y+face*.13,z+.9),(xx+w*.19,y+face*.13,z+.9),.021,chrome)
 box(m,(x,y+face*.073,z+2.34),(.32,.022,.13),green)
 for i in range(3):box(m,(x-.09+i*.07,y+face*.09,z+2.34),(.035,.01,.065),white)
done(m,'01_Arquitetura')
# Rails around center aisle and stage.
m=Mesh('Corrimaos')
for side in [-1,1]:
 x=side*.88
 for row in range(1,12,2):
  y=6.3+row*1.07;z=.1+row*.1
  cyl(m,(x,y,z),(x,y,z+.81),.019,metal)
  box(m,(x,y,z+.008),(.1,.13,.016),metal,.005)
 path(m,[(x,6.8,.98),(x,17.95,2.022)],.021,metal)
path(m,[(-6.22,2.90,.56),(-6.22,2.90,1.39),(-6.22,1.43,1.39),(-6.22,1.43,.56)],.025,metal)
for y in [1,3,5]:cyl(m,(7.1,y,.55-(y-.5)*.1),(7.1,y,1.40-(y-.5)*.1),.022,metal)
path(m,[(7.1,.6,1.45),(7.1,5.6,.95)],.025,metal)
done(m,'06_Detalhes')
# Black front conference desk with honey wood top.
m=Mesh('Mesa_diretora')
box(m,(4.43,2.02,.97),(3.12,.67,.80),black,.018)
for i in range(6):box(m,(4.43,2.37,.63+i*.125),(3.15,.075,.101),black,.015)
box(m,(4.43,2.00,1.399),(3.28,.83,.046),wood,.009)
for x in [3.64,5.10]:
 cyl(m,(x,1.35,.60),(x,1.35,.99),.03,metal)
 box(m,(x,1.35,1.01),(.48,.44,.09),cloth,.04)
 box(m,(x,1.13,1.29),(.48,.10,.49),cloth,.045)
box(m,(5.25,2.05,1.431),(.37,.25,.021),black,.008)
box(m,(5.25,1.94,1.575),(.37,.018,.28),black,.008,Rx(math.radians(-15)))
done(m,'07_Mesa_e_bandeiras')
# Draped flags; fabric geometry has real folds.
m=Mesh('Bandeiras')
for i,x in enumerate([4.08,4.67,5.26]):
 cyl(m,(x,.85,.56),(x,.85,.59),.16,black,20)
 cyl(m,(x,.85,.58),(x,.85,2.82),.014,chrome)
 cyl(m,(x,.85,2.82),(x,.85,2.93),.026,gold,12,r2=0)
 vs=[];uv=[];fs=[];nx=12;nz=24
 for j in range(nz+1):
  v=j/nz
  for k in range(nx+1):
   u=k/nx;vs.append((x+u*.41,.87+.048*math.sin(u*PI*4+v*1.5)*u,2.75-v*1.37-.12*u));uv.append((u,v))
 for j in range(nz):
  for k in range(nx):a=j*(nx+1)+k;fs.extend([(a,a+1,a+nx+2),(a,a+nx+2,a+nx+1)])
 m.add(vs,fs,flagmats[i],uv=uv)
done(m,'07_Mesa_e_bandeiras')
# Fire extinguishers and door-side signs.
m=Mesh('Seguranca')
for x,y,z in [(7.17,4.0,0),(-7.17,17.8,1.2)]:
 cyl(m,(x,y,z+.16),(x,y,z+.58),.085,red,16)
 cyl(m,(x,y,z+.58),(x,y,z+.67),.035,black,12)
 box(m,(x,y,z+.70),(.055,.15,.025),black,.005)
 path(m,[(x,y,z+.64),(x-.03,y+.17,z+.71),(x-.06,y+.21,z+.47)],.014,black)
 box(m,(x,y,z+.38),(.16,.04,.16),white)
done(m,'06_Detalhes')
# Removable ceiling with suspended square tiles, light grilles and ventilation.
m=Mesh('Forro_modular')
box(m,(0,10.4,4.25),(14.78,21,.10),wall)
for x in np.arange(-7.2,7.3,.6):box(m,(x,12.3,4.194),(.012,16.6,.009),screen)
for y in np.arange(4.0,20.8,.6):box(m,(0,y,4.194),(14.6,.012,.009),screen)
done(m,'09_Teto')
m=Mesh('Luminarias_e_ar')
for y in [1.8,5.7,9.8,13.9,18.0]:
 for x in [-5.4,-1.8,1.8,5.4]:
  box(m,(x,y,4.175),(.64,1.24,.035),chrome,.008)
  box(m,(x,y,4.148),(.57,1.17,.013),lightmat)
  for k in range(9):box(m,(x,y-.53+k*.132,4.13),(.58,.012,.024),chrome)
 for x in [-3.6,0,3.6]:
  box(m,(x,y,4.17),(.49,.49,.022),black)
  for k in range(7):
   s=.48-k*.058
   for xx in [-s/2,s/2]:box(m,(x+xx,y,4.14),(.012,s,.012),chrome)
   for yy in [-s/2,s/2]:box(m,(x,y+yy,4.14),(s,.012,.012),chrome)
done(m,'09_Teto')
# Export self-contained glTF 2.0 with instanced furniture and packed images.
def export_glb(filename,selection,recenter=False):
 b=bytearray();views=[];acc=[]
 def add_blob(data,target=None):
  while len(b)%4:b.extend(b'\0')
  v={'buffer':0,'byteOffset':len(b),'byteLength':len(data)}
  if target:v['target']=target
  views.append(v);b.extend(data);return len(views)-1
 def accessor(a,typ,component=5126):
  arr=np.array(a,dtype='<f4' if component==5126 else '<u4');vw=add_blob(arr.tobytes(),34963 if component==5125 else 34962)
  z={'bufferView':vw,'componentType':component,'count':len(arr),'type':typ}
  if typ=='VEC3':z['min']=arr.min(axis=0).tolist();z['max']=arr.max(axis=0).tolist()
  acc.append(z);return len(acc)-1
 used=sorted(set(o['mesh'] for o in selection));meshmap={};gm=[]
 for mi in used:
  m=meshes[mi];pr=[]
  for ma,p in m.parts.items():
   pos=accessor(np.array(p[0])*[-1,1,1],'VEC3');nor=accessor(np.array(p[1])*[-1,1,1],'VEC3');uv=accessor(p[2],'VEC2');ind=accessor(np.array(p[3])[:,::-1].ravel(),'SCALAR',5125)
   pr.append({'attributes':{'POSITION':pos,'NORMAL':nor,'TEXCOORD_0':uv},'indices':ind,'material':ma})
  meshmap[mi]=len(gm);gm.append({'name':m.name,'primitives':pr})
 imgs=[{'name':n,'bufferView':add_blob(data),'mimeType':'image/png'} for n,data in textures]
 nodes=[{'name':'Auditorio_AP1','rotation':[-math.sqrt(.5),0,0,math.sqrt(.5)],'children':[],'extras':{'unidades':'metros','referencia':'4 fotografias fornecidas','medidas':'estimadas; nao levantamento arquitetonico'}}]
 groups={}
 for o in selection:
  g=o['group']
  if g not in groups:groups[g]=len(nodes);nodes[0]['children'].append(len(nodes));nodes.append({'name':g,'children':[]})
  a=o['angle'];n={'name':o['name'],'mesh':meshmap[o['mesh']],'translation':[0,0,0] if recenter else [-o['loc'][0],o['loc'][1],o['loc'][2]],'rotation':[0,0,math.sin(a/2),math.cos(a/2)]}
  nodes[groups[g]]['children'].append(len(nodes));nodes.append(n)
 doc={'asset':{'version':'2.0','generator':'Auditorio AP1 - reconstrucao geometrica por referencia fotografica'},'scene':0,'scenes':[{'name':'Auditorio_AP1','nodes':[0]}],'nodes':nodes,'meshes':gm,'materials':materials,'textures':[{'source':i,'sampler':0} for i in range(len(imgs))],'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}],'images':imgs,'accessors':acc,'bufferViews':views,'buffers':[{'byteLength':len(b)}]}
 js=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();js+=b' '*((-len(js))%4);b+=b'\0'*((-len(b))%4)
 data=struct.pack('<III',0x46546c67,2,28+len(js)+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b
 open(OUT+'/'+filename,'wb').write(data)
export_glb('Auditorio_AP1.glb',objects)
export_glb('Poltrona_Azul.glb',[{'name':'Poltrona_azul','mesh':chair,'loc':[0,0,0],'angle':0,'group':'Poltrona'}],True)
export_glb('Pulpito_Curvo.glb',[{'name':'Pulpito_curvo','mesh':podium,'loc':[0,0,0],'angle':0,'group':'Pulpito'}],True)
export_glb('Palco_Completo.glb',[o for o in objects if o['group'] in ['02_Palco','05_Pulpito','07_Mesa_e_bandeiras']])
# Keep the geometric scene for independent previews / verification.

report={'unidade':'m','largura_interna_estimada':14.6,'comprimento_interno_estimado':20.8,'altura_forro_estimada':4.2,'altura_palco':.55,'fileiras_estimadas':12,'assentos_por_fileira':16,'assentos_frontais':3,'total_poltronas_modeladas':195,'objetos':len(objects),'malhas_unicas':len(meshes),'triangulos_geometria_unica':sum(len(p[3]) for m in meshes for p in m.parts.values()),'triangulos_instanciados':sum(sum(len(p[3]) for p in meshes[o['mesh']].parts.values()) for o in objects),'limites':'Dimensoes, contagem de assentos, detalhes ocultos e emblemas de bandeiras sao aproximados.'}
open(OUT+'/Especificacoes.json','w').write(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps(report,indent=2))
