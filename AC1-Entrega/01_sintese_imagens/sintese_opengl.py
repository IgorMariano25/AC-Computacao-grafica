# -*- coding: utf-8 -*-
"""
AREA 1 - SINTESE DE IMAGENS (Computacao Grafica)
=================================================
Fluxo caracteristico da area:   MODELO / DADOS GEOMETRICOS  ->  IMAGEM

Aplicacao executada: pipeline de rasterizacao OpenGL 3.3 Core, dirigido pela
biblioteca ModernGL (repositorio publico: https://github.com/moderngl/moderngl),
renderizando o modelo "dragao.obj" fornecido na aula 08 da disciplina.

O programa percorre explicitamente as etapas do pipeline grafico vistas em aula:
  (1) MODELAGEM      - leitura da malha Wavefront .obj (vertices + faces)
  (2) POLIGONIZACAO  - malha ja triangularizada; calculo das normais por vertice
  (3) TRANSFORMACOES - matrizes Model, View e Projection montadas "na mao"
  (4) RASTERIZACAO   - conversao vetorial -> matricial feita pela GPU
  (5) SHADING        - modelo de iluminacao de Phong no fragment shader (GLSL)
  (6) VISIBILIDADE   - remocao de superficies ocultas via z-buffer
  (7) FRAME BUFFER   - leitura do buffer de cor e gravacao em PNG

Saida: 4 imagens que mostram o mesmo modelo em estagios diferentes do pipeline,
mais uma montagem comparativa.
"""

import json
import time
from pathlib import Path

import numpy as np
import moderngl
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Configuracao
# --------------------------------------------------------------------------
AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent                     # raiz do repositorio da disciplina
OBJ = RAIZ / "aula08" / "objetos" / "dragao.obj"
SAIDA = AQUI / "saida"
SAIDA.mkdir(exist_ok=True)

LARGURA, ALTURA = 900, 900
AMOSTRAS_MSAA = 4


# --------------------------------------------------------------------------
# (1) MODELAGEM - leitura do arquivo Wavefront OBJ
# --------------------------------------------------------------------------
def carregar_obj(caminho: Path):
    """Le apenas 'v' (vertices) e 'f' (faces). A malha do dragao ja e triangular."""
    vertices, faces = [], []
    with open(caminho, "r", encoding="utf-8", errors="ignore") as fp:
        for linha in fp:
            if linha.startswith("v "):
                _, x, y, z = linha.split()[:4]
                vertices.append((float(x), float(y), float(z)))
            elif linha.startswith("f "):
                # formato "f v/vt v/vt v/vt" -> aproveitamos so o indice do vertice
                idx = [int(campo.split("/")[0]) - 1 for campo in linha.split()[1:]]
                for k in range(1, len(idx) - 1):          # leque, caso venha quad
                    faces.append((idx[0], idx[k], idx[k + 1]))
    return np.array(vertices, dtype="f4"), np.array(faces, dtype="i4")


# --------------------------------------------------------------------------
# (2) POLIGONIZACAO - normais por vertice (media das normais das faces)
# --------------------------------------------------------------------------
def calcular_normais(V, F):
    n_face = np.cross(V[F[:, 1]] - V[F[:, 0]], V[F[:, 2]] - V[F[:, 0]])
    N = np.zeros_like(V)
    for c in range(3):                       # acumula em cada vertice da face
        np.add.at(N, F[:, c], n_face)
    comp = np.linalg.norm(N, axis=1, keepdims=True)
    comp[comp == 0] = 1.0
    return (N / comp).astype("f4")


# --------------------------------------------------------------------------
# (3) TRANSFORMACOES GEOMETRICAS - matrizes 4x4 homogeneas (aulas 04/07/08)
# --------------------------------------------------------------------------
def normalizar(v):
    return v / np.linalg.norm(v)


def matriz_model(escala, rot_y_graus, translacao):
    """Model = Translacao . Rotacao_y . Escala (aplicada da direita p/ a esquerda)."""
    s = np.diag([escala, escala, escala, 1.0]).astype("f4")
    a = np.radians(rot_y_graus)
    r = np.array([[np.cos(a), 0, np.sin(a), 0],
                  [0, 1, 0, 0],
                  [-np.sin(a), 0, np.cos(a), 0],
                  [0, 0, 0, 1]], dtype="f4")
    t = np.eye(4, dtype="f4")
    t[:3, 3] = translacao
    return t @ r @ s


def matriz_view(olho, alvo, cima):
    """View (look-at): leva o mundo para o sistema de coordenadas da camera."""
    f = normalizar(np.asarray(alvo, "f8") - np.asarray(olho, "f8"))   # frente
    s = normalizar(np.cross(f, np.asarray(cima, "f8")))               # direita
    u = np.cross(s, f)                                                # cima real
    m = np.eye(4)
    m[0, :3], m[1, :3], m[2, :3] = s, u, -f
    m[:3, 3] = -m[:3, :3] @ np.asarray(olho, "f8")
    return m.astype("f4")


def matriz_projecao(fov_graus, aspecto, perto, longe):
    """Projecao perspectiva -> volume canonico [-1,1]^3 (aula 07)."""
    t = 1.0 / np.tan(np.radians(fov_graus) / 2.0)
    return np.array([
        [t / aspecto, 0, 0, 0],
        [0, t, 0, 0],
        [0, 0, (longe + perto) / (perto - longe), (2 * longe * perto) / (perto - longe)],
        [0, 0, -1, 0],
    ], dtype="f4")


def ajuste_de_enquadramento(V, mvp, ocupacao=0.90):
    """
    Enquadra o modelo na janela sem mexer na camera.

    Projeta todos os vertices, mede a caixa envolvente ja em coordenadas
    normalizadas de dispositivo (NDC) e devolve uma matriz que aplica um
    deslocamento + escala 2D no espaco de recorte. Como x_ndc = x_clip/w,
    multiplicar x_clip por k e somar -k*cx*w equivale a (x_ndc - cx)*k.
    A componente z nao e tocada, entao o z-buffer continua valido.
    """
    homog = np.hstack([V, np.ones((len(V), 1), "f4")])
    clip = homog @ mvp.T
    w = clip[:, 3:4]
    ndc = clip[:, :2] / np.where(np.abs(w) < 1e-9, 1e-9, w)
    minimo, maximo = ndc.min(0), ndc.max(0)
    centro = (minimo + maximo) / 2.0
    meia_extensao = float(np.max((maximo - minimo) / 2.0))
    k = ocupacao / max(meia_extensao, 1e-6)
    ajuste = np.eye(4, dtype="f4")
    ajuste[0, 0] = ajuste[1, 1] = k
    ajuste[0, 3] = -k * centro[0]
    ajuste[1, 3] = -k * centro[1]
    return ajuste, k


# --------------------------------------------------------------------------
# (5) SHADING - programas GLSL
# --------------------------------------------------------------------------
VERTEX_SHADER = """
#version 330 core
in  vec3 in_pos;
in  vec3 in_normal;
uniform mat4 Model, View, Projection;
uniform mat3 NormalMatrix;
out vec3 frag_pos_mundo;
out vec3 frag_normal;
void main() {
    vec4 p_mundo   = Model * vec4(in_pos, 1.0);
    frag_pos_mundo = p_mundo.xyz;
    frag_normal    = NormalMatrix * in_normal;
    gl_Position    = Projection * View * p_mundo;   // MVP
    gl_PointSize   = 2.0;
}
"""

# modo 0 = cor constante (sem iluminacao) | 1 = Phong completo
FRAGMENT_SHADER = """
#version 330 core
in  vec3 frag_pos_mundo;
in  vec3 frag_normal;
out vec4 cor_saida;

uniform vec3  pos_luz;
uniform vec3  pos_camera;
uniform vec3  cor_objeto;
uniform int   modo;

void main() {
    if (modo == 0) {                       // sem modelo de iluminacao
        cor_saida = vec4(cor_objeto, 1.0);
        return;
    }
    vec3 N = normalize(frag_normal);
    vec3 L = normalize(pos_luz - frag_pos_mundo);
    vec3 V = normalize(pos_camera - frag_pos_mundo);
    vec3 R = reflect(-L, N);

    float ka = 0.18;                                   // ambiente
    float kd = max(dot(N, L), 0.0);                    // difusa   (Lambert)
    float ks = pow(max(dot(V, R), 0.0), 48.0) * 0.55;  // especular (Phong)

    vec3 cor = cor_objeto * (ka + 0.85 * kd) + vec3(1.0) * ks;
    cor_saida = vec4(pow(cor, vec3(1.0 / 2.2)), 1.0);  // correcao gama
}
"""


def main():
    relatorio = {}
    print("=" * 74)
    print("AREA 1 - SINTESE DE IMAGENS  |  ModernGL / OpenGL 3.3 Core")
    print("=" * 74)

    # ---- (1) e (2) ------------------------------------------------------
    t0 = time.perf_counter()
    V, F = carregar_obj(OBJ)
    N = calcular_normais(V, F)
    t_carga = time.perf_counter() - t0

    centro = (V.min(0) + V.max(0)) / 2.0
    raio = float(np.linalg.norm(V.max(0) - V.min(0))) / 2.0
    V = (V - centro).astype("f4")            # centraliza o modelo na origem

    print("\n[1] MODELAGEM  - arquivo .......: %s  (%.0f KB)"
          % (OBJ.name, OBJ.stat().st_size / 1024))
    print("    vertices ...................: {:,}".format(len(V)))
    print("[2] POLIGONIZACAO - triangulos .: {:,}".format(len(F)))
    print("    normais calculadas em ......: %.0f ms" % (t_carga * 1000))
    relatorio["entrada"] = {"arquivo": OBJ.name, "bytes": OBJ.stat().st_size,
                            "vertices": int(len(V)), "triangulos": int(len(F))}

    # ---- contexto OpenGL offscreen --------------------------------------
    ctx = moderngl.create_standalone_context(require=330)
    print("\n    GL_VERSION .................: " + ctx.info["GL_VERSION"])
    print("    GL_RENDERER ................: " + ctx.info["GL_RENDERER"])
    relatorio["gl"] = {"version": ctx.info["GL_VERSION"], "renderer": ctx.info["GL_RENDERER"]}

    ctx.enable(moderngl.DEPTH_TEST)          # (6) z-buffer: superficies ocultas
    ctx.enable(moderngl.PROGRAM_POINT_SIZE)

    prog = ctx.program(vertex_shader=VERTEX_SHADER, fragment_shader=FRAGMENT_SHADER)

    # VBO/VAO: os dados geometricos vao para a memoria da GPU (vertex buffer)
    dados = np.hstack([V, N]).astype("f4").tobytes()
    vbo = ctx.buffer(dados)
    ibo = ctx.buffer(F.astype("i4").tobytes())
    vao = ctx.vertex_array(prog, [(vbo, "3f 3f", "in_pos", "in_normal")], ibo)
    vao_pontos = ctx.vertex_array(prog, [(vbo, "3f 3f", "in_pos", "in_normal")])
    print("    VBO enviado a GPU ..........: %.0f KB" % (len(dados) / 1024))

    # framebuffer offscreen com anti-aliasing (MSAA) + framebuffer de leitura
    fbo_ms = ctx.framebuffer(
        color_attachments=[ctx.renderbuffer((LARGURA, ALTURA), samples=AMOSTRAS_MSAA)],
        depth_attachment=ctx.depth_renderbuffer((LARGURA, ALTURA), samples=AMOSTRAS_MSAA))
    fbo_leitura = ctx.simple_framebuffer((LARGURA, ALTURA))

    # ---- (3) camera ------------------------------------------------------
    dist = raio * 2.6
    olho = np.array([dist * 0.75, dist * 0.42, dist * 0.85])
    alvo = np.array([0.0, 0.0, 0.0])
    model = matriz_model(escala=1.0, rot_y_graus=-25.0, translacao=(0, 0, 0))
    view = matriz_view(olho, alvo, (0, 1, 0))
    proj = matriz_projecao(45.0, LARGURA / ALTURA, raio * 0.05, raio * 12.0)

    # enquadramento automatico: corrige escala/centro em coordenadas de recorte
    mvp = proj @ view @ model
    ajuste, fator = ajuste_de_enquadramento(V, mvp)
    proj = (ajuste @ proj).astype("f4")

    # NormalMatrix = transposta da inversa da parte 3x3 de Model
    normal_matrix = np.linalg.inv(model[:3, :3]).T.astype("f4")

    prog["Model"].write(np.ascontiguousarray(model.T).tobytes())   # GL e column-major
    prog["View"].write(np.ascontiguousarray(view.T).tobytes())
    prog["Projection"].write(np.ascontiguousarray(proj.T).tobytes())
    prog["NormalMatrix"].write(np.ascontiguousarray(normal_matrix.T).tobytes())
    prog["pos_luz"].value = tuple((olho * 1.15 + np.array([raio, raio * 1.4, 0.0])).tolist())
    prog["pos_camera"].value = tuple(olho.tolist())

    print("\n[3] TRANSFORMACOES - matrizes Model, View e Projection montadas (4x4)")
    print("    camera (olho) ..............: (%.2f, %.2f, %.2f)" % tuple(olho))
    print("    ajuste de enquadramento ....: fator %.2fx em coordenadas de recorte" % fator)

    # ---- (4)(5)(6)(7) renderiza os quatro estagios -----------------------
    fundo = (0.09, 0.10, 0.13, 1.0)
    estagios = [
        ("a_vertices", "1. Nuvem de vertices (modelo geometrico)",
         dict(modo=0, cor=(0.35, 0.85, 0.95), pontos=True)),
        ("b_wireframe", "2. Malha de triangulos (wireframe)",
         dict(modo=0, cor=(0.30, 0.78, 0.62), wire=True)),
        ("c_flat", "3. Rasterizacao + z-buffer (sem luz)",
         dict(modo=0, cor=(0.55, 0.57, 0.62))),
        ("d_phong", "4. Shading de Phong (amb + dif + esp)",
         dict(modo=1, cor=(0.86, 0.42, 0.22))),
    ]

    quadros, tempos = [], {}
    for nome, titulo, cfg in estagios:
        fbo_ms.use()
        ctx.clear(*fundo)
        prog["modo"].value = cfg["modo"]
        prog["cor_objeto"].value = cfg["cor"]
        ctx.wireframe = cfg.get("wire", False)

        t = time.perf_counter()
        if cfg.get("pontos"):
            vao_pontos.render(moderngl.POINTS)
        else:
            vao.render(moderngl.TRIANGLES)
        ctx.finish()
        tempos[nome] = (time.perf_counter() - t) * 1000
        ctx.wireframe = False

        ctx.copy_framebuffer(fbo_leitura, fbo_ms)      # resolve o MSAA
        px = fbo_leitura.read(components=3)            # (7) leitura do frame buffer
        img = Image.frombytes("RGB", (LARGURA, ALTURA), px).transpose(Image.FLIP_TOP_BOTTOM)
        img.save(SAIDA / (nome + ".png"))
        quadros.append((img, titulo))
        print("[4-7] %-45s %7.1f ms  -> saida/%s.png" % (titulo, tempos[nome], nome))

    # ---- montagem comparativa (com rotulos) ------------------------------
    montagem = Image.new("RGB", (LARGURA * 2, ALTURA * 2), (10, 11, 14))
    for i, (img, _) in enumerate(quadros):
        montagem.paste(img, ((i % 2) * LARGURA, (i // 2) * ALTURA))
    montagem = montagem.resize((1200, 1200), Image.LANCZOS)

    desenho = ImageDraw.Draw(montagem)
    try:
        fonte = ImageFont.truetype("arialbd.ttf", 22)
    except OSError:
        fonte = ImageFont.load_default()
    for i, (_, titulo) in enumerate(quadros):
        x, y = (i % 2) * 600 + 22, (i // 2) * 600 + 20
        desenho.text((x, y), titulo, fill=(240, 240, 245), font=fonte)
    desenho.line([(600, 0), (600, 1200)], fill=(60, 62, 70), width=2)
    desenho.line([(0, 600), (1200, 600)], fill=(60, 62, 70), width=2)
    montagem.save(SAIDA / "montagem_pipeline.png")

    relatorio["saida"] = {"resolucao": [LARGURA, ALTURA],
                          "pixels": LARGURA * ALTURA,
                          "bytes_png_phong": (SAIDA / "d_phong.png").stat().st_size,
                          "tempos_ms": {k: round(v, 2) for k, v in tempos.items()}}

    print("\n" + "-" * 74)
    print("BALANCO DA AREA (entrada -> saida)")
    print("-" * 74)
    print("  ENTRADA : descricao VETORIAL -> {:,} vertices / {:,} triangulos".format(len(V), len(F)))
    print("  SAIDA   : imagem MATRICIAL   -> {}x{} = {:,} pixels".format(
        LARGURA, ALTURA, LARGURA * ALTURA))
    print("  A conversao vetorial -> matricial e a RASTERIZACAO, executada na GPU.")
    print("  Nenhuma imagem foi lida como entrada: a imagem foi SINTETIZADA.")

    (SAIDA / "relatorio.json").write_text(json.dumps(relatorio, indent=2), encoding="utf-8")
    print("\nArquivos gerados em: " + str(SAIDA))


if __name__ == "__main__":
    main()
