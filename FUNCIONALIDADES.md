# Explicacion Tecnica De Funcionalidades

Este documento explica las funcionalidades principales del proyecto y muestra los fragmentos de codigo esenciales para entender como se implementaron con Pygame, OpenGL y Pillow.

La explicacion esta pensada para alguien que conoce OpenGL y quiere entender la arquitectura y las decisiones tecnicas del proyecto.

## 1. Estructura General

El proyecto esta dividido por responsabilidades:

- `main.py`: crea la ventana, inicializa OpenGL, mantiene el loop principal y los estados globales.
- `faces.py`: define la estructura de una cara editable.
- `input_handler.py`: maneja teclado, mouse, colores y seleccion de texturas.
- `renderer.py`: contiene todo el dibujo OpenGL.
- `texture_loader.py`: carga imagenes estaticas y GIFs animados como texturas OpenGL.

El loop principal vive en `main.py` y en cada frame realiza:

```python
for event in pygame.event.get():
    # procesar teclado/mouse

glClear(GL_COLOR_BUFFER_BIT)

for index, face in enumerate(faces):
    # dibujar cara normal o efecto infinito

pygame.display.flip()
clock.tick(60)
```

La idea base es simple: se dibujan tres cuadrilateros 2D deformables, cada uno representando una cara visible del cubo real.

## 2. Ventana OpenGL Con Pygame

La ventana se crea con Pygame usando doble buffer y contexto OpenGL:

```python
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
```

Luego se activa blending para poder usar transparencias en overlays, paneles y efectos:

```python
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
```

Esto es importante porque el proyecto dibuja:

- caras con color,
- texturas,
- vertices de control,
- lineas del efecto infinito,
- panel de controles semitransparente.

## 3. Sistema De Coordenadas 2D

Aunque se usa OpenGL, el proyecto trabaja en una proyeccion ortografica 2D. La configuracion esta en `setup_2d(...)`:

```python
def setup_2d(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
```

La llamada clave es:

```python
glOrtho(0, width, height, 0, -1, 1)
```

Con esto:

- `(0, 0)` queda arriba a la izquierda.
- `x` crece hacia la derecha.
- `y` crece hacia abajo.

Esto coincide con las coordenadas de mouse de Pygame, por lo que se pueden usar directamente `event.pos` para mover vertices.

## 4. Representacion De Una Cara

Cada cara se modela con la clase `Face` en `faces.py`:

```python
class Face:
    def __init__(self, vertices=None, color=(1.0, 1.0, 1.0), texture_id=None):
        self.vertices = [list(v) for v in vertices]
        self.color = color
        self.texture_id = texture_id
        self.selected_vertex = None
```

Lo importante es que `vertices` contiene cuatro puntos 2D:

```python
[[x0, y0], [x1, y1], [x2, y2], [x3, y3]]
```

Esos cuatro puntos se dibujan como un `GL_QUADS`. Como el usuario puede moverlos, el cuadrilatero puede deformarse para calzar con la perspectiva del cubo fisico.

## 5. Dibujar Una Cara Normal

El dibujo de una cara se realiza en `renderer.py`:

```python
def draw_face(face, is_active=True, time_seconds=0.0):
    verts = face.vertices
    if face.texture_id is not None:
        _draw_textured_face(verts, _resolve_texture_id(face.texture_id, time_seconds))
    else:
        _draw_colored_face(verts, face.color)

    _draw_edges(verts, is_active)
    _draw_vertices(verts, face.selected_vertex, is_active)
```

Si la cara tiene textura, se dibuja texturizada. Si no tiene textura, se dibuja con color plano.

El color plano usa:

```python
glDisable(GL_TEXTURE_2D)
glColor3f(*color)
glBegin(GL_QUADS)
for v in verts:
    glVertex2f(*v)
glEnd()
```

La cara texturizada usa coordenadas UV basicas:

```python
uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
for (u, v_coord), vertex in zip(uv, verts):
    glTexCoord2f(u, v_coord)
    glVertex2f(*vertex)
```

Esto asigna la imagen completa a la cara, deformandola segun la posicion de los vertices.

## 6. Calibracion Con Mouse

La calibracion se realiza moviendo los vertices de la cara activa.

Primero se detecta si el click esta cerca de un vertice:

```python
def find_vertex_near(self, mouse_pos, radius=12):
    mx, my = mouse_pos
    for i, (vx, vy) in enumerate(self.vertices):
        if abs(mx - vx) < radius and abs(my - vy) < radius:
            return i
    return None
```

Cuando el usuario presiona el mouse:

```python
if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
    self._start_drag(event.pos)
```

Si se encontro un vertice cercano, se guarda como seleccionado:

```python
face.selected_vertex = idx
self.dragging = True
```

Mientras el mouse se mueve, se actualiza la posicion del vertice:

```python
if event.type == pygame.MOUSEMOTION and self.dragging:
    face.move_vertex(face.selected_vertex, event.pos)
```

Esta es la parte central del projection mapping manual: el usuario ajusta los vertices hasta que las caras virtuales coincidan con el cubo real.

## 7. Seleccion De Cara Activa

La cara activa se cambia con `TAB`:

```python
if key == pygame.K_TAB:
    self.active_face = (self.active_face + 1) % len(self.faces)
```

Luego en `main.py`, al dibujar, se calcula:

```python
is_active = index == handler.active_face
```

Y se pasa al renderer:

```python
draw_face(face, is_active=is_active, time_seconds=time_seconds)
```

El renderer usa ese estado para cambiar borde y vertices:

```python
glLineWidth(4 if is_active else 1.5)
glColor3f(*(ACTIVE_EDGE_COLOR if is_active else INACTIVE_EDGE_COLOR))
```

Esto permite saber visualmente que cara se esta editando.

## 8. Paleta De Colores

La paleta esta definida en `input_handler.py`:

```python
COLOR_PALETTE = {
    pygame.K_1: (0.95, 0.10, 0.18),
    pygame.K_2: (1.00, 0.35, 0.08),
    pygame.K_3: (1.00, 0.78, 0.12),
    # ...
}
```

Cuando el usuario presiona una tecla de color:

```python
if key in COLOR_PALETTE:
    self.faces[self.active_face].color = COLOR_PALETTE[key]
    self.faces[self.active_face].texture_id = None
```

Se elimina la textura para que el color plano sea visible inmediatamente.

## 9. Carga De Texturas

Las texturas se buscan automaticamente dentro de `assets/`:

```python
TEXTURE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}
```

El escaneo se realiza con `Path.iterdir()`:

```python
paths = [
    path
    for path in folder.iterdir()
    if path.is_file() and path.suffix.lower() in TEXTURE_EXTENSIONS
]
```

Con `T` se avanza en la lista, y con `Shift + T` se retrocede:

```python
step = -1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
self._cycle_texture(step)
```

Para no cargar la misma textura muchas veces, se usa cache:

```python
if path not in self.texture_cache:
    self.texture_cache[path] = load_texture_asset(str(path))
```

## 10. Subir Una Imagen A OpenGL

La carga de una imagen estatica esta en `texture_loader.py`:

```python
img = Image.open(filepath).convert("RGBA")
img_data = np.array(img, dtype=np.uint8)
```

Luego se genera y configura la textura:

```python
texture_id = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture_id)
glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
```

Finalmente se suben los pixeles:

```python
glTexImage2D(
    GL_TEXTURE_2D, 0, GL_RGBA,
    img.width, img.height, 0,
    GL_RGBA, GL_UNSIGNED_BYTE, img_data
)
```

Se usa `GL_CLAMP_TO_EDGE` para evitar bordes repetidos o artefactos en las esquinas.

## 11. GIFs Animados

Los GIFs se cargan como varias texturas, una por frame.

La clase `AnimatedTexture` guarda:

- lista de `texture_ids`,
- duracion de cada frame,
- duracion total.

```python
class AnimatedTexture:
    def __init__(self, texture_ids, frame_durations):
        self.texture_ids = texture_ids
        self.frame_durations = frame_durations
        self.total_duration = sum(frame_durations)
```

Los frames se extraen con Pillow:

```python
for frame in ImageSequence.Iterator(img):
    duration = frame.info.get("duration", img.info.get("duration", 100))
    texture_ids.append(_create_texture_from_image(frame.convert("RGBA")))
    frame_durations.append(duration)
```

Durante el render se elige el frame segun el tiempo:

```python
elapsed_ms = (time_seconds * 1000.0) % self.total_duration
```

Luego se acumulan duraciones hasta encontrar el frame correspondiente.

En `renderer.py`, el codigo no necesita saber si la textura es estatica o animada:

```python
def _resolve_texture_id(texture, time_seconds):
    if hasattr(texture, "get_texture_id"):
        return texture.get_texture_id(time_seconds)
    return texture
```

Esto permite que `draw_face(...)` funcione igual para PNG, JPG o GIF.

## 12. Efecto De Cubo Infinito

El efecto se dibuja con `draw_infinite_mirror_face(...)`.

La idea es generar muchos anillos dentro de cada cara, desde el borde hacia el centro:

```python
rings = _build_full_face_rings(verts, shape, center_uv, depth)
```

Cada anillo se dibuja como una linea cerrada:

```python
glBegin(GL_LINE_LOOP)
for v in ring:
    glVertex2f(*v)
glEnd()
```

La profundidad se controla con `depth`. Mas profundidad significa mas anillos.

El color de cada anillo varia con una onda temporal:

```python
wave = 0.5 + 0.5 * math.sin(time_seconds * 3.2 - i * 0.7)
intensity = (1.0 - t) * 0.75 + wave * 0.25
```

Esto produce un brillo animado, como si el tunel tuviera movimiento.

## 13. Punto De Fuga Animado

El punto de fuga se calcula en coordenadas UV de la cara:

```python
def _animated_vanishing_uv(time_seconds, pulse):
    return (
        0.5 + math.sin(time_seconds * 0.9) * 0.055 * pulse,
        0.5 + math.cos(time_seconds * 1.1) * 0.055 * pulse,
    )
```

Luego ese punto UV se transforma a posicion real dentro del cuadrilatero:

```python
vanishing = _quad_point(verts, center_uv[0], center_uv[1])
```

Esto hace que el centro del tunel se mueva suavemente dentro de cada cara.

## 14. Interpolacion Dentro De Un Cuadrilatero

La funcion `_quad_point(...)` convierte coordenadas UV a coordenadas de pantalla:

```python
def _quad_point(verts, u, v):
    top_x = verts[0][0] * (1.0 - u) + verts[1][0] * u
    top_y = verts[0][1] * (1.0 - u) + verts[1][1] * u
    bottom_x = verts[3][0] * (1.0 - u) + verts[2][0] * u
    bottom_y = verts[3][1] * (1.0 - u) + verts[2][1] * u
    return (
        top_x * (1.0 - v) + bottom_x * v,
        top_y * (1.0 - v) + bottom_y * v,
    )
```

Esta es una interpolacion bilineal simple. Permite construir puntos internos aunque la cara este deformada.

Es clave para el efecto infinito, porque los anillos se calculan en UV y despues se proyectan al cuadrilatero real.

## 15. Figuras Del Infinito

Las figuras disponibles estan en `MIRROR_SHAPES`:

```python
MIRROR_SHAPES = ("quad", "triangle", "diamond", "hexagon", "circle", "star")
```

La tecla `F` cambia el indice:

```python
mirror_shape_index = (mirror_shape_index + 1) % len(MIRROR_SHAPES)
```

La funcion `_build_full_face_rings(...)` genera los anillos. Para cada angulo se calcula hasta donde llega el borde de la cara:

```python
boundary_radius = _square_boundary_radius(center_uv, angle)
```

Luego se aplica un factor segun la figura:

```python
shape_factor = _shape_radius_factor(shape, angle, center_uv, boundary_radius)
radius = boundary_radius * scale * (1.0 - shape_strength * (1.0 - shape_factor))
```

Esto permite que:

- el anillo exterior ocupe toda la cara,
- los anillos internos se deformen hacia circulo, estrella, triangulo, etc.

## 16. Lineas De Profundidad

Ademas de los anillos, el efecto dibuja lineas desde el borde hacia el centro:

```python
for corner in range(spoke_count):
    glBegin(GL_LINES)
    glVertex2f(*rings[0][corner])
    glVertex2f(*rings[-1][corner])
    glEnd()
```

Estas lineas refuerzan la sensacion de tunel o espejo infinito.

## 17. Brillo Animado

Se elige un anillo que avanza con el tiempo:

```python
spark_index = int((time_seconds * 8) % max(depth, 1))
```

Luego se dibuja con mayor brillo:

```python
_draw_glow_quad(rings[spark_index], base)
```

El resultado es un pulso luminoso que recorre el tunel.

## 18. Acomodar Las Caras Como Cubo

La tecla `G` llama a `arrange_faces_as_cube(...)` en `main.py`.

Esta funcion asigna coordenadas nuevas a los vertices para crear una plantilla inicial de cubo:

```python
faces[0].vertices = [
    [left, top],
    [right, top],
    [right, bottom],
    [left, bottom],
]
```

La cara lateral comparte arista con la frontal:

```python
faces[1].vertices = [
    [right, top],
    [right + depth_x, top - depth_y],
    [right + depth_x, bottom - depth_y],
    [right, bottom],
]
```

La cara superior comparte la arista superior:

```python
faces[2].vertices = [
    [left, top],
    [left + depth_x, top - depth_y],
    [right + depth_x, top - depth_y],
    [right, top],
]
```

Esto no reemplaza la calibracion fina, pero deja las caras rapidamente en una configuracion tipo cubo.

## 19. Overlay De Controles En OpenGL

El panel de controles se dibuja dentro de OpenGL con `draw_controls_overlay(...)`.

Primero se dibuja un rectangulo semitransparente:

```python
glColor4f(0.02, 0.025, 0.035, 0.46)
glBegin(GL_QUADS)
glVertex2f(x, y)
glVertex2f(x + width, y)
glVertex2f(x + width, y + height)
glVertex2f(x, y + height)
glEnd()
```

El texto se genera con Pygame y se convierte en textura OpenGL:

```python
font = pygame.font.Font(None, size)
surface = font.render(text, True, color)
data = pygame.image.tostring(surface, "RGBA", False)
```

Luego se sube con `glTexImage2D(...)` y se dibuja como un quad texturizado:

```python
glEnable(GL_TEXTURE_2D)
glBindTexture(GL_TEXTURE_2D, texture_id)
glBegin(GL_QUADS)
glTexCoord2f(0, 0); glVertex2f(x, y)
glTexCoord2f(1, 0); glVertex2f(x + width, y)
glTexCoord2f(1, 1); glVertex2f(x + width, y + height)
glTexCoord2f(0, 1); glVertex2f(x, y + height)
glEnd()
```

Para no recrear texturas de texto en cada frame, se usa cache:

```python
_TEXT_CACHE[key] = (texture_id, width, height)
```

## 20. Pantalla Completa

La tecla `ESC` alterna pantalla completa:

```python
if event.key == K_ESCAPE:
    pygame.display.toggle_fullscreen()
```

Esto permite trabajar primero en ventana y despues pasar a proyector/pantalla completa.

## 21. Control Del Estado Global

Los estados principales viven en `main.py`:

```python
mirror_enabled = False
mirror_depth = 18
mirror_pulse = 1.0
mirror_shape_index = 0
show_overlay = True
```

El teclado modifica esos estados:

```python
if event.key == K_m:
    mirror_enabled = not mirror_enabled

if event.key in (K_PLUS, K_EQUALS, K_KP_PLUS):
    mirror_depth = min(mirror_depth + 2, 40)
```

Luego el estado decide que se dibuja:

```python
if mirror_enabled:
    draw_infinite_mirror_face(...)
else:
    draw_face(...)
```

## 22. Resumen Tecnico

El proyecto funciona como un sistema de projection mapping 2D:

1. Se crean tres caras como cuadrilateros editables.
2. Se usa una proyeccion ortografica para trabajar con coordenadas de pantalla.
3. El usuario mueve vertices para calibrar las caras sobre el cubo real.
4. Cada cara puede mostrar color, textura estatica o GIF animado.
5. El efecto infinito se genera con anillos OpenGL calculados en coordenadas UV y transformados al cuadrilatero deformado.
6. La interfaz se dibuja tambien dentro de OpenGL usando quads y texto convertido a textura.

La parte mas importante para explicar el proyecto es que no se esta renderizando un cubo 3D real. Se estan renderizando tres superficies 2D deformables que, al ser proyectadas sobre un cubo fisico, producen la ilusion de estar mapeadas sobre sus caras visibles.
