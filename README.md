# Projection Mapping - Cubo Infinito

Proyecto de Computacion Grafica para hacer projection mapping sobre las tres caras visibles de un cubo usando Python, Pygame y OpenGL.

La aplicacion permite calibrar las caras con el mouse, asignar colores, cargar texturas estaticas, cargar GIFs animados y activar un efecto de cubo infinito tipo espejo.

## Requisitos

- Python 3.10 o superior
- Windows, Linux o macOS
- Un proyector o pantalla secundaria para presentar

## Instalacion En Otro PC

1. Copia la carpeta completa del proyecto al otro computador.

2. Abre una terminal dentro de la carpeta del proyecto.

3. Crea un entorno virtual:

```powershell
python -m venv venv
```

4. Activa el entorno virtual.

En Windows PowerShell:

```powershell
.\venv\Scripts\activate
```

En Linux o macOS:

```bash
source venv/bin/activate
```

5. Instala las dependencias:

```powershell
pip install -r requirements.txt
```

## Ejecucion

Con el entorno virtual activado:

```powershell
python main.py
```

En Windows tambien puedes ejecutar directamente:

```powershell
.\venv\Scripts\python.exe main.py
```

## Controles

- `TAB`: cambiar la cara activa.
- Mouse: arrastrar vertices de la cara activa.
- `1-9` y `0`: cambiar color de la cara activa.
- `Q W E R Y U I O P`: cambiar a colores adicionales.
- `T`: cargar la siguiente textura en la cara activa.
- `Shift + T`: cargar la textura anterior.
- `M`: activar o desactivar el efecto de cubo infinito.
- `F`: cambiar la figura del efecto infinito.
- `+`: aumentar profundidad del cubo infinito.
- `-`: disminuir profundidad del cubo infinito.
- `ESC`: alternar pantalla completa.
- `H`: mostrar u ocultar los controles en pantalla.
- `G`: mostrar u ocultar la guia visual para armar las caras como cubo.

Los controles tambien aparecen dentro de la ventana OpenGL al ejecutar el programa, en un panel semitransparente. La guia de cubo muestra un cubo de referencia y ayuda a ubicar cara frontal, lateral y superior.

## Texturas

Las texturas deben estar dentro de la carpeta `assets/`.

Formatos soportados:

- `.png`
- `.jpg`
- `.jpeg`
- `.bmp`
- `.webp`
- `.gif`

Al iniciar, el programa detecta automaticamente las texturas disponibles en `assets/`. Para asignarlas, selecciona una cara con `TAB` y usa `T`.

Los archivos `.gif` se cargan como texturas animadas. Cada frame se reproduce usando la duracion definida por el propio GIF.

## Uso Con Proyector

1. Conecta el proyector al computador.
2. Ejecuta el programa.
3. Usa `ESC` para ponerlo en pantalla completa.
4. Selecciona cada cara con `TAB`.
5. Arrastra sus vertices con el mouse hasta que calcen con las caras reales del cubo.
6. Asigna colores o texturas.
7. Presiona `M` para activar el efecto de cubo infinito cuando la calibracion este lista.

## Archivos Principales

- `main.py`: inicializa la ventana, crea las caras y controla el loop principal.
- `faces.py`: define la clase `Face` y sus vertices.
- `renderer.py`: dibuja caras, texturas, vertices y el efecto de cubo infinito.
- `input_handler.py`: maneja teclado, mouse, colores y texturas.
- `texture_loader.py`: carga imagenes como texturas OpenGL.
- `assets/`: carpeta para imagenes/texturas.

## Solucion De Problemas

Si `python` no es reconocido en Windows, instala Python desde:

```text
https://www.python.org/downloads/
```

Durante la instalacion, activa la opcion `Add Python to PATH`.

Si falla la instalacion de `PyOpenGL_accelerate`, puedes intentar:

```powershell
pip install pygame PyOpenGL pillow numpy
```

El proyecto puede funcionar sin `PyOpenGL_accelerate`; esa dependencia solo ayuda con rendimiento.
