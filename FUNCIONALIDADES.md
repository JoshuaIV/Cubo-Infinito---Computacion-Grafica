# Explicacion De Funcionalidades Principales

Este documento describe como se implementaron las funcionalidades principales del proyecto de projection mapping con OpenGL.

## Estructura General

El proyecto esta separado en varios archivos para mantener responsabilidades claras:

- `main.py`: inicializa Pygame/OpenGL, crea las caras, maneja el loop principal y los estados globales.
- `faces.py`: define la clase `Face`, que representa una cara proyectable.
- `input_handler.py`: maneja teclado, mouse, colores y seleccion de texturas.
- `renderer.py`: contiene las funciones de dibujo OpenGL.
- `texture_loader.py`: carga imagenes, texturas y GIFs animados.

## Representacion De Las Caras

Cada superficie proyectada se representa con la clase `Face`, definida en `faces.py`.

Una cara contiene:

- `vertices`: lista de 4 puntos `[x, y]` en coordenadas de pantalla.
- `color`: color RGB con valores entre `0.0` y `1.0`.
- `texture_id`: textura asociada a la cara, si existe.
- `selected_vertex`: vertice actualmente seleccionado con el mouse.

Cada cara se dibuja como un cuadrilatero OpenGL usando `GL_QUADS`. Como los vertices se pueden mover libremente, cada cara puede deformarse para calzar con una superficie real del cubo.

## Sistema De Coordenadas 2D

En `renderer.py`, la funcion `setup_2d(width, height)` configura OpenGL para trabajar en 2D:

```python
glOrtho(0, width, height, 0, -1, 1)
```

Esto hace que:

- `(0, 0)` este arriba a la izquierda.
- `x` crezca hacia la derecha.
- `y` crezca hacia abajo.

Esta configuracion facilita usar directamente las posiciones del mouse de Pygame.

## Calibracion De Caras Con Mouse

La calibracion se maneja en `input_handler.py`.

El usuario puede:

- presionar `TAB` para cambiar la cara activa,
- hacer click cerca de un vertice,
- arrastrarlo con el mouse,
- soltarlo para fijar su nueva posicion.

La deteccion del vertice se realiza con `find_vertex_near(...)` en `faces.py`. Si el mouse esta suficientemente cerca de un vertice, ese vertice queda seleccionado.

Luego, mientras el mouse se mueve, `move_vertex(...)` actualiza la posicion del vertice.

Esto permite ajustar manualmente las caras proyectadas hasta que calcen con las caras reales del cubo.

## Resaltado De La Cara Activa

En `renderer.py`, `draw_face(...)` recibe el parametro `is_active`.

Si la cara esta activa:

- se dibuja con borde amarillo mas grueso,
- sus vertices aparecen mas grandes,
- los vertices se ven rojos.

Si no esta activa:

- el borde se ve gris,
- los vertices se dibujan mas pequenos.

Esto ayuda a saber que cara se esta editando en cada momento.

## Colores

Los colores estan definidos en `COLOR_PALETTE`, dentro de `input_handler.py`.

El usuario puede cambiar el color de la cara activa usando:

- `1-9`
- `0`
- `Q W E R Y U I O P`

Cuando se asigna un color, se elimina la textura de esa cara:

```python
self.faces[self.active_face].texture_id = None
```

Asi se evita mezclar color plano y textura al mismo tiempo.

## Texturas E Imagenes

Las texturas se guardan en la carpeta `assets/`.

En `input_handler.py`, el programa busca automaticamente archivos con extensiones:

- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`
- `.webp`
- `.gif`

Con `T`, el usuario avanza a la siguiente textura disponible. Con `Shift + T`, vuelve a la anterior.

La carga de imagenes se realiza en `texture_loader.py`, usando Pillow. Cada imagen se convierte a formato `RGBA` y luego se sube a OpenGL con `glTexImage2D`.

## Soporte Para GIFs Animados

Los GIFs se manejan con la clase `AnimatedTexture`, definida en `texture_loader.py`.

Cuando el archivo cargado es un GIF animado:

1. Se recorren todos sus frames con `ImageSequence.Iterator`.
2. Cada frame se convierte a textura OpenGL.
3. Se guarda la duracion de cada frame.
4. Se crea un objeto `AnimatedTexture`.

Durante el render, `renderer.py` revisa si la textura tiene el metodo `get_texture_id(...)`.

Si lo tiene, significa que es animada:

```python
texture.get_texture_id(time_seconds)
```

Asi se obtiene el frame correcto segun el tiempo actual.

## Efecto De Cubo Infinito

El efecto infinito se implementa en `draw_infinite_mirror_face(...)`, dentro de `renderer.py`.

La idea es dibujar muchos anillos dentro de cada cara. Cada anillo representa una repeticion mas profunda del tunel visual.

El proceso general es:

1. Se calcula un punto de fuga animado.
2. Se generan varios anillos desde el borde de la cara hacia el centro.
3. Cada anillo se dibuja con `GL_LINE_LOOP`.
4. Se conectan los anillos con lineas hacia el centro para reforzar la sensacion de profundidad.
5. Se agrega un brillo animado en uno de los anillos.

La profundidad se controla con `mirror_depth`.

El usuario puede modificarla con:

- `+`: aumenta profundidad.
- `-`: disminuye profundidad.

## Figuras Del Efecto Infinito

Las figuras disponibles estan en `MIRROR_SHAPES`:

```python
("quad", "triangle", "diamond", "hexagon", "circle", "star")
```

El usuario cambia de figura con `F`.

La funcion `_build_full_face_rings(...)` genera los anillos para cada figura. Para que el efecto ocupe toda la cara, los anillos se calculan desde el borde del cuadrilatero y luego se van deformando hacia la figura seleccionada.

Por ejemplo:

- `quad`: mantiene forma rectangular.
- `circle`: se acerca a circulos concentricos.
- `star`: genera una forma de estrella hacia el centro.
- `triangle`, `diamond`, `hexagon`: producen tuneles con esas formas.

## Acomodar Las Caras Como Cubo

En `main.py`, la funcion `arrange_faces_as_cube(...)` reubica automaticamente las tres caras para formar una plantilla de cubo.

Se activa con la tecla `G`.

Esta funcion modifica los vertices de las tres caras:

- cara frontal,
- cara lateral,
- cara superior.

No cambia los colores ni las texturas. Solo actualiza posiciones.

Esto sirve como punto de partida rapido antes de realizar la calibracion fina sobre el cubo real.

## Overlay De Controles

El panel de controles se dibuja dentro de OpenGL usando `draw_controls_overlay(...)`.

El texto se genera con Pygame:

1. Se renderiza texto en una superficie de Pygame.
2. Esa superficie se convierte en bytes RGBA.
3. Se sube como textura OpenGL.
4. Se dibuja como un cuadrilatero texturizado.

Para mejorar rendimiento, las texturas de texto se guardan en cache en `_TEXT_CACHE`.

El overlay muestra:

- cara activa,
- estado del infinito,
- figura actual,
- profundidad,
- controles principales.

Se puede ocultar o mostrar con `H`.

## Pantalla Completa

La tecla `ESC` llama a:

```python
pygame.display.toggle_fullscreen()
```

Esto permite alternar entre ventana y pantalla completa, util para trabajar con un proyector.

## Loop Principal

El loop principal esta en `main.py`.

En cada frame:

1. Se leen eventos de Pygame.
2. Se actualizan estados como figura, profundidad o textura.
3. Se limpia la pantalla con `glClear`.
4. Se dibujan las caras.
5. Se dibuja el overlay de controles.
6. Se actualiza la ventana con `pygame.display.flip()`.
7. Se limita la ejecucion a 60 FPS con `clock.tick(60)`.

## Resumen

El proyecto combina:

- Pygame para ventana, input y texto.
- OpenGL para dibujar caras, texturas y efectos.
- Pillow para cargar imagenes y GIFs.
- Una estructura de caras editables para permitir projection mapping manual.

La funcionalidad central es poder deformar tres cuadrilateros en pantalla para que calcen con tres caras reales de un cubo, y luego proyectar colores, texturas, GIFs o un efecto visual de cubo infinito sobre ellas.
