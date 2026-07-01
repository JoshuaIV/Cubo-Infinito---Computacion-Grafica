from OpenGL.GL import *
from OpenGL.GLU import *
import math
import pygame

VERTEX_POINT_SIZE = 10
VERTEX_COLOR_NORMAL   = (1.0, 0.0, 0.0)
VERTEX_COLOR_SELECTED = (1.0, 1.0, 0.0)
ACTIVE_EDGE_COLOR = (1.0, 0.86, 0.15)
INACTIVE_EDGE_COLOR = (0.55, 0.55, 0.55)
MIRROR_SHAPES = ("quad", "triangle", "diamond", "hexagon", "circle", "star")
_TEXT_CACHE = {}

def setup_2d(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def draw_face(face, is_active=True, time_seconds=0.0):
    verts = face.vertices
    if face.texture_id is not None:
        _draw_textured_face(verts, _resolve_texture_id(face.texture_id, time_seconds))
    else:
        _draw_colored_face(verts, face.color)
    _draw_edges(verts, is_active)
    _draw_vertices(verts, face.selected_vertex, is_active)

def draw_infinite_mirror_face(
    face,
    time_seconds,
    depth=18,
    pulse=1.0,
    show_controls=True,
    is_active=True,
    shape="quad",
):
    verts = face.vertices
    base = face.color
    glDisable(GL_TEXTURE_2D)

    _draw_colored_face(verts, tuple(c * 0.12 for c in base))

    center_uv = _animated_vanishing_uv(time_seconds, pulse)
    vanishing = _quad_point(verts, center_uv[0], center_uv[1])
    rings = _build_full_face_rings(verts, shape, center_uv, depth)

    for i, ring in enumerate(rings):
        t = i / max(depth - 1, 1)
        wave = 0.5 + 0.5 * math.sin(time_seconds * 3.2 - i * 0.7)
        intensity = (1.0 - t) * 0.75 + wave * 0.25
        color = _mix_color(base, (1.0, 1.0, 1.0), 0.18 + wave * 0.18)
        glLineWidth(max(1.0, 4.0 * (1.0 - t)))
        glColor3f(*(c * intensity for c in color))
        glBegin(GL_LINE_LOOP)
        for v in ring:
            glVertex2f(*v)
        glEnd()

    glLineWidth(1.4)
    spoke_count = len(rings[0])
    for corner in range(spoke_count):
        glColor3f(*(c * 0.65 for c in _mix_color(base, (1.0, 1.0, 1.0), 0.25)))
        glBegin(GL_LINES)
        glVertex2f(*rings[0][corner])
        glVertex2f(*rings[-1][corner])
        glEnd()

    spark_index = int((time_seconds * 8) % max(depth, 1))
    if rings:
        _draw_glow_quad(rings[spark_index], base)

    _draw_edges(verts, is_active)
    if show_controls:
        _draw_vertices(verts, face.selected_vertex, is_active)

def draw_controls_overlay(
    width,
    height,
    active_face,
    face_count,
    mirror_enabled,
    mirror_shape,
    mirror_depth,
):
    lines = [
        "CONTROLES",
        f"Cara activa: {active_face + 1}/{face_count}",
        f"Infinito: {'ON' if mirror_enabled else 'OFF'}",
        f"Figura: {mirror_shape}",
        f"Profundidad: {mirror_depth}",
        "",
        "TAB: cambiar cara",
        "Mouse: mover vertices",
        "1-9/0: colores",
        "Q W E R Y U I O P: mas colores",
        "T / Shift+T: texturas",
        "M: cubo infinito",
        "F: figura infinito",
        "+ / -: profundidad",
        "G: acomodar como cubo",
        "ESC: pantalla completa",
        "H: ocultar controles",
    ]

    line_height = 20
    panel_width = 318
    panel_height = 22 + line_height * len(lines)
    x = width - panel_width + 8
    y = 18

    _draw_overlay_panel(x - 10, y - 10, panel_width, panel_height)
    for index, line in enumerate(lines):
        if line:
            color = (255, 232, 90, 255) if index == 0 else (235, 245, 255, 255)
            _draw_text(line, x, y + index * line_height, color=color, size=20)

def _draw_colored_face(verts, color):
    glDisable(GL_TEXTURE_2D)
    glColor3f(*color)
    glBegin(GL_QUADS)
    for v in verts:
        glVertex2f(*v)
    glEnd()

def _draw_textured_face(verts, texture_id):
    if texture_id is None:
        return

    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor3f(1, 1, 1)
    glBegin(GL_QUADS)
    uv = [(0, 0), (1, 0), (1, 1), (0, 1)]
    for (u, v_coord), vertex in zip(uv, verts):
        glTexCoord2f(u, v_coord)
        glVertex2f(*vertex)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def _draw_edges(verts, is_active=True):
    glLineWidth(4 if is_active else 1.5)
    glColor3f(*(ACTIVE_EDGE_COLOR if is_active else INACTIVE_EDGE_COLOR))
    glBegin(GL_LINE_LOOP)
    for v in verts:
        glVertex2f(*v)
    glEnd()

def _draw_overlay_panel(x, y, width, height):
    glDisable(GL_TEXTURE_2D)
    glColor4f(0.02, 0.025, 0.035, 0.46)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

    glLineWidth(2)
    glColor4f(1.0, 0.86, 0.15, 0.62)
    glBegin(GL_LINE_LOOP)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def _draw_text(text, x, y, color=(255, 255, 255, 255), size=20):
    texture_id, width, height = _get_text_texture(text, color, size)
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor4f(1, 1, 1, 1)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)
    glVertex2f(x, y)
    glTexCoord2f(1, 0)
    glVertex2f(x + width, y)
    glTexCoord2f(1, 1)
    glVertex2f(x + width, y + height)
    glTexCoord2f(0, 1)
    glVertex2f(x, y + height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

def _get_text_texture(text, color, size):
    key = (text, color, size)
    if key in _TEXT_CACHE:
        return _TEXT_CACHE[key]

    font = pygame.font.Font(None, size)
    surface = font.render(text, True, color)
    surface = surface.convert_alpha()
    data = pygame.image.tostring(surface, "RGBA", False)
    width, height = surface.get_size()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)

    _TEXT_CACHE[key] = (texture_id, width, height)
    return _TEXT_CACHE[key]

def _draw_vertices(verts, selected_index, is_active=True):
    glPointSize(VERTEX_POINT_SIZE if is_active else 6)
    glBegin(GL_POINTS)
    for i, v in enumerate(verts):
        if i == selected_index:
            glColor3f(*VERTEX_COLOR_SELECTED)
        elif is_active:
            glColor3f(*VERTEX_COLOR_NORMAL)
        else:
            glColor3f(*INACTIVE_EDGE_COLOR)
        glVertex2f(*v)
    glEnd()

def _face_center(verts):
    return (
        sum(v[0] for v in verts) / len(verts),
        sum(v[1] for v in verts) / len(verts),
    )

def _animated_vanishing_point(verts, center, time_seconds, pulse):
    width_hint = max(v[0] for v in verts) - min(v[0] for v in verts)
    height_hint = max(v[1] for v in verts) - min(v[1] for v in verts)
    wobble_x = math.sin(time_seconds * 0.9) * width_hint * 0.06 * pulse
    wobble_y = math.cos(time_seconds * 1.1) * height_hint * 0.06 * pulse
    return (center[0] + wobble_x, center[1] + wobble_y)

def _animated_vanishing_uv(time_seconds, pulse):
    return (
        0.5 + math.sin(time_seconds * 0.9) * 0.055 * pulse,
        0.5 + math.cos(time_seconds * 1.1) * 0.055 * pulse,
    )

def _mix_color(a, b, amount):
    return tuple(a[i] * (1.0 - amount) + b[i] * amount for i in range(3))

def _build_full_face_rings(verts, shape, center_uv, depth):
    sample_count = 96 if shape in ("circle", "star") else 72
    rings = []
    for i in range(depth):
        t = i / max(depth - 1, 1)
        scale = 1.0 - t * 0.92
        shape_strength = t * 0.78
        ring = []

        for sample in range(sample_count):
            angle = -math.pi / 2 + sample * math.tau / sample_count
            boundary_radius = _square_boundary_radius(center_uv, angle)
            shape_factor = _shape_radius_factor(shape, angle, center_uv, boundary_radius)
            radius = boundary_radius * scale * (1.0 - shape_strength * (1.0 - shape_factor))
            u = center_uv[0] + math.cos(angle) * radius
            v = center_uv[1] + math.sin(angle) * radius
            ring.append(_quad_point(verts, u, v))

        rings.append(ring)
    return rings

def _square_boundary_radius(center_uv, angle):
    cx, cy = center_uv
    dx = math.cos(angle)
    dy = math.sin(angle)
    distances = []

    if dx > 0:
        distances.append((1.0 - cx) / dx)
    elif dx < 0:
        distances.append((0.0 - cx) / dx)

    if dy > 0:
        distances.append((1.0 - cy) / dy)
    elif dy < 0:
        distances.append((0.0 - cy) / dy)

    positive = [distance for distance in distances if distance > 0]
    return min(positive) if positive else 0.5

def _shape_radius_factor(shape, angle, center_uv, boundary_radius):
    if boundary_radius <= 0:
        return 1.0

    if shape == "quad":
        return 1.0

    if shape == "circle":
        target_radius = min(center_uv[0], 1.0 - center_uv[0], center_uv[1], 1.0 - center_uv[1])
    elif shape == "diamond":
        dx = abs(math.cos(angle))
        dy = abs(math.sin(angle))
        target_radius = 0.5 / max(dx + dy, 0.001)
    elif shape == "triangle":
        target_radius = _polygon_radius(angle, _triangle_points())
    elif shape == "hexagon":
        target_radius = _polygon_radius(angle, _regular_local_points(6, 0.5, math.pi / 6))
    elif shape == "star":
        target_radius = 0.33 + 0.17 * (0.5 + 0.5 * math.cos(5 * (angle + math.pi / 2)))
    else:
        target_radius = boundary_radius

    return max(0.25, min(target_radius / boundary_radius, 1.0))

def _triangle_points():
    return [
        (math.cos(-math.pi / 2 + i * math.tau / 3) * 0.5,
         math.sin(-math.pi / 2 + i * math.tau / 3) * 0.5)
        for i in range(3)
    ]

def _regular_local_points(count, radius, rotation=-math.pi / 2):
    return [
        (
            math.cos(rotation + i * math.tau / count) * radius,
            math.sin(rotation + i * math.tau / count) * radius,
        )
        for i in range(count)
    ]

def _polygon_radius(angle, points):
    dx = math.cos(angle)
    dy = math.sin(angle)
    best = None
    for i, point in enumerate(points):
        next_point = points[(i + 1) % len(points)]
        edge = (next_point[0] - point[0], next_point[1] - point[1])
        denom = _cross((dx, dy), edge)
        if abs(denom) < 0.000001:
            continue

        ray_distance = _cross(point, edge) / denom
        edge_amount = _cross(point, (dx, dy)) / denom
        if ray_distance > 0 and 0.0 <= edge_amount <= 1.0:
            if best is None or ray_distance < best:
                best = ray_distance

    return best if best is not None else 0.5

def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]

def _build_base_shape(verts, shape):
    if shape == "triangle":
        uv_points = [(0.5, 0.0), (1.0, 1.0), (0.0, 1.0)]
    elif shape == "diamond":
        uv_points = [(0.5, 0.0), (1.0, 0.5), (0.5, 1.0), (0.0, 0.5)]
    elif shape == "hexagon":
        uv_points = _regular_uv_points(6, radius=0.50, rotation=math.pi / 6)
    elif shape == "circle":
        uv_points = _regular_uv_points(36, radius=0.50)
    elif shape == "star":
        uv_points = _star_uv_points(5, outer_radius=0.50, inner_radius=0.22)
    else:
        uv_points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

    return [_quad_point(verts, u, v) for u, v in uv_points]

def _regular_uv_points(count, radius=0.5, rotation=-math.pi / 2):
    return [
        (
            0.5 + math.cos(rotation + i * math.tau / count) * radius,
            0.5 + math.sin(rotation + i * math.tau / count) * radius,
        )
        for i in range(count)
    ]

def _star_uv_points(points, outer_radius=0.5, inner_radius=0.25):
    uv_points = []
    count = points * 2
    for i in range(count):
        radius = outer_radius if i % 2 == 0 else inner_radius
        angle = -math.pi / 2 + i * math.tau / count
        uv_points.append((0.5 + math.cos(angle) * radius, 0.5 + math.sin(angle) * radius))
    return uv_points

def _quad_point(verts, u, v):
    top_x = verts[0][0] * (1.0 - u) + verts[1][0] * u
    top_y = verts[0][1] * (1.0 - u) + verts[1][1] * u
    bottom_x = verts[3][0] * (1.0 - u) + verts[2][0] * u
    bottom_y = verts[3][1] * (1.0 - u) + verts[2][1] * u
    return (
        top_x * (1.0 - v) + bottom_x * v,
        top_y * (1.0 - v) + bottom_y * v,
    )

def _draw_glow_quad(verts, base_color):
    glLineWidth(3)
    glColor3f(*_mix_color(base_color, (1.0, 1.0, 1.0), 0.55))
    glBegin(GL_LINE_LOOP)
    for v in verts:
        glVertex2f(*v)
    glEnd()

def _resolve_texture_id(texture, time_seconds):
    if hasattr(texture, "get_texture_id"):
        return texture.get_texture_id(time_seconds)
    return texture
