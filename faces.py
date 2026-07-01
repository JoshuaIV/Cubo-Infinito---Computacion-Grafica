import numpy as np

class Face:
    def __init__(self, vertices=None, color=(1.0, 1.0, 1.0), texture_id=None):
        # 4 vértices (x, y) en pantalla
        if vertices is None:
            self.vertices = [
                [200, 150],
                [400, 150],
                [400, 350],
                [200, 350],
            ]
        else:
            self.vertices = [list(v) for v in vertices]

        self.color = color          # (r, g, b) con valores 0.0 a 1.0
        self.texture_id = texture_id
        self.selected_vertex = None # índice del vértice agarrado con mouse

    def move_vertex(self, index, new_pos):
        self.vertices[index] = list(new_pos)

    def find_vertex_near(self, mouse_pos, radius=12):
        mx, my = mouse_pos
        for i, (vx, vy) in enumerate(self.vertices):
            if abs(mx - vx) < radius and abs(my - vy) < radius:
                return i
        return None