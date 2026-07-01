from pathlib import Path

import pygame


COLOR_PALETTE = {
    pygame.K_1: (0.95, 0.10, 0.18),  # rojo neon
    pygame.K_2: (1.00, 0.35, 0.08),  # coral
    pygame.K_3: (1.00, 0.78, 0.12),  # dorado
    pygame.K_4: (0.12, 0.85, 0.38),  # verde laser
    pygame.K_5: (0.00, 0.85, 0.72),  # turquesa
    pygame.K_6: (0.08, 0.58, 0.98),  # azul electrico
    pygame.K_7: (0.35, 0.32, 1.00),  # indigo
    pygame.K_8: (0.78, 0.25, 1.00),  # violeta
    pygame.K_9: (1.00, 0.22, 0.62),  # fucsia
    pygame.K_0: (1.00, 1.00, 1.00),  # blanco
    pygame.K_q: (0.08, 0.08, 0.10),  # negro suave
    pygame.K_w: (0.70, 0.95, 1.00),  # hielo
    pygame.K_e: (0.72, 1.00, 0.36),  # lima
    pygame.K_r: (1.00, 0.58, 0.22),  # ambar
    pygame.K_y: (0.98, 0.88, 0.32),  # amarillo calido
    pygame.K_u: (0.18, 0.95, 1.00),  # cyan brillante
    pygame.K_i: (0.58, 0.42, 1.00),  # lavanda
    pygame.K_o: (1.00, 0.42, 0.74),  # rosado
    pygame.K_p: (0.86, 0.96, 0.88),  # menta blanca
}
TEXTURE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".webp", ".gif"}


class InputHandler:
    def __init__(self, faces, texture_dir="assets"):
        self.faces = faces
        self.active_face = 0
        self.dragging = False
        self.texture_paths = self._find_texture_paths(texture_dir)
        self.texture_cache = {}
        self.texture_index_by_face = [-1 for _ in faces]

    def handle_event(self, event):
        """Procesa un evento de pygame. Retorna False si hay que salir."""

        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            self._handle_key(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._start_drag(event.pos)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._stop_drag()

        if event.type == pygame.MOUSEMOTION and self.dragging:
            self._do_drag(event.pos)

        return True

    def _handle_key(self, key):
        if key == pygame.K_TAB:
            self.active_face = (self.active_face + 1) % len(self.faces)
            print(f"Cara activa: {self.active_face}")

        if key in COLOR_PALETTE:
            self.faces[self.active_face].color = COLOR_PALETTE[key]
            self.faces[self.active_face].texture_id = None
            self.texture_index_by_face[self.active_face] = -1

        if key == pygame.K_t:
            step = -1 if pygame.key.get_mods() & pygame.KMOD_SHIFT else 1
            self._cycle_texture(step)

    def _start_drag(self, pos):
        face = self.faces[self.active_face]
        idx = face.find_vertex_near(pos)
        if idx is not None:
            face.selected_vertex = idx
            self.dragging = True

    def _stop_drag(self):
        self.faces[self.active_face].selected_vertex = None
        self.dragging = False

    def _do_drag(self, pos):
        face = self.faces[self.active_face]
        if face.selected_vertex is not None:
            face.move_vertex(face.selected_vertex, pos)

    def _find_texture_paths(self, texture_dir):
        folder = Path(texture_dir)
        if not folder.exists():
            print(f"No existe la carpeta de texturas: {texture_dir}")
            return []

        paths = [
            path
            for path in folder.iterdir()
            if path.is_file() and path.suffix.lower() in TEXTURE_EXTENSIONS
        ]
        paths.sort(key=lambda path: path.name.lower())

        print(f"Texturas encontradas: {len(paths)}")
        for path in paths:
            print(f"  - {path.name}")
        return paths

    def _cycle_texture(self, step):
        if not self.texture_paths:
            print("No hay texturas en assets/. Agrega PNG, JPG, BMP, WEBP o GIF.")
            return

        index = self.texture_index_by_face[self.active_face]
        index = (index + step) % len(self.texture_paths)
        path = self.texture_paths[index]

        if path not in self.texture_cache:
            from texture_loader import load_texture_asset
            self.texture_cache[path] = load_texture_asset(str(path))

        face = self.faces[self.active_face]
        face.texture_id = self.texture_cache[path]
        self.texture_index_by_face[self.active_face] = index
        print(f"Cara {self.active_face}: textura {path.name}")
