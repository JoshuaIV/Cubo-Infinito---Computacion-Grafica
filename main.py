import pygame
from pygame.locals import *
from OpenGL.GL import *

from faces import Face
from renderer import (
    MIRROR_SHAPES,
    setup_2d,
    draw_face,
    draw_infinite_mirror_face,
    draw_controls_overlay,
)
from input_handler import InputHandler


def main():
    pygame.init()
    pygame.font.init()

    width, height = 1280, 720
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Projection Mapping - Cubo Infinito INF451")

    setup_2d(width, height)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Tres caras iniciales. En modo edicion se ajustan con TAB + mouse.
    face_frontal = Face(
        vertices=[[470, 210], [760, 210], [760, 500], [470, 500]],
        color=(0.08, 0.58, 0.98),
    )
    face_lateral = Face(
        vertices=[[130, 260], [370, 190], [370, 520], [130, 470]],
        color=(0.02, 0.86, 0.56),
    )
    face_superior = Face(
        vertices=[[360, 60], [820, 80], [760, 190], [400, 170]],
        color=(1.00, 0.35, 0.24),
    )
    faces = [face_frontal, face_lateral, face_superior]

    handler = InputHandler(faces)
    mirror_enabled = False
    mirror_depth = 18
    mirror_pulse = 1.0
    mirror_shape_index = 0
    show_overlay = True

    clock = pygame.time.Clock()

    print("Controles:")
    print("  M      -> activar/desactivar cubo infinito")
    print("  F      -> cambiar figura del cubo infinito")
    print("  +/-    -> cambiar profundidad del espejo")
    print("  TAB    -> cambiar cara activa (edicion)")
    print("  1-9/0  -> cambiar color de la cara activa")
    print("  Q/W/E/R/Y/U/I/O/P -> mas colores")
    print("  T      -> siguiente textura en la cara activa")
    print("  SHIFT+T -> textura anterior en la cara activa")
    print("  ESC    -> fullscreen")
    print("  H      -> mostrar/ocultar controles en pantalla")
    print("  G      -> acomodar caras como cubo")

    running = True
    while running:
        time_seconds = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_m:
                    mirror_enabled = not mirror_enabled
                    print(f"Cubo infinito: {'ON' if mirror_enabled else 'OFF'}")
                if event.key == K_f:
                    mirror_shape_index = (mirror_shape_index + 1) % len(MIRROR_SHAPES)
                    print(f"Figura infinito: {MIRROR_SHAPES[mirror_shape_index]}")
                if event.key in (K_PLUS, K_EQUALS, K_KP_PLUS):
                    mirror_depth = min(mirror_depth + 2, 40)
                    print(f"Profundidad espejo: {mirror_depth}")
                if event.key in (K_MINUS, K_KP_MINUS):
                    mirror_depth = max(mirror_depth - 2, 6)
                    print(f"Profundidad espejo: {mirror_depth}")
                if event.key == K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                if event.key == K_h:
                    show_overlay = not show_overlay
                if event.key == K_g:
                    arrange_faces_as_cube(faces, width, height)
                    print("Caras acomodadas como cubo")

            running = handler.handle_event(event)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)

        for index, face in enumerate(faces):
            is_active = index == handler.active_face
            if mirror_enabled:
                draw_infinite_mirror_face(
                    face,
                    time_seconds,
                    depth=mirror_depth,
                    pulse=mirror_pulse,
                    show_controls=True,
                    is_active=is_active,
                    shape=MIRROR_SHAPES[mirror_shape_index],
                )
            else:
                draw_face(face, is_active=is_active, time_seconds=time_seconds)

        if show_overlay:
            draw_controls_overlay(
                width,
                height,
                handler.active_face,
                len(faces),
                mirror_enabled,
                MIRROR_SHAPES[mirror_shape_index],
                mirror_depth,
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def arrange_faces_as_cube(faces, width, height):
    cube_width = min(width * 0.22, 280)
    cube_height = cube_width
    depth_x = cube_width * 0.70
    depth_y = cube_height * 0.32
    left = width * 0.34
    top = height * 0.34
    right = left + cube_width
    bottom = top + cube_height

    faces[0].vertices = [
        [left, top],
        [right, top],
        [right, bottom],
        [left, bottom],
    ]
    faces[1].vertices = [
        [right, top],
        [right + depth_x, top - depth_y],
        [right + depth_x, bottom - depth_y],
        [right, bottom],
    ]
    faces[2].vertices = [
        [left, top],
        [left + depth_x, top - depth_y],
        [right + depth_x, top - depth_y],
        [right, top],
    ]

    for face in faces:
        face.selected_vertex = None


if __name__ == "__main__":
    main()
