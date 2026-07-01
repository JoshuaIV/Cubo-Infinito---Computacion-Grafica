from OpenGL.GL import *
from PIL import Image, ImageSequence
import numpy as np


class AnimatedTexture:
    def __init__(self, texture_ids, frame_durations):
        self.texture_ids = texture_ids
        self.frame_durations = frame_durations
        self.total_duration = sum(frame_durations)

    def get_texture_id(self, time_seconds):
        if not self.texture_ids:
            return None

        if self.total_duration <= 0:
            return self.texture_ids[0]

        elapsed_ms = (time_seconds * 1000.0) % self.total_duration
        accumulated = 0
        for texture_id, duration in zip(self.texture_ids, self.frame_durations):
            accumulated += duration
            if elapsed_ms <= accumulated:
                return texture_id
        return self.texture_ids[-1]


def load_texture(filepath):
    """Carga una imagen estatica y la sube a la GPU. Retorna el texture_id."""
    img = Image.open(filepath).convert("RGBA")
    return _create_texture_from_image(img)


def load_texture_asset(filepath):
    """Carga una imagen estatica o GIF animado como textura OpenGL."""
    img = Image.open(filepath)
    if getattr(img, "is_animated", False):
        return load_gif_texture(filepath)

    return load_texture(filepath)


def load_gif_texture(filepath):
    """Carga todos los frames de un GIF y retorna una textura animada."""
    img = Image.open(filepath)
    texture_ids = []
    frame_durations = []

    for frame in ImageSequence.Iterator(img):
        duration = frame.info.get("duration", img.info.get("duration", 100))
        duration = max(int(duration), 20)
        texture_ids.append(_create_texture_from_image(frame.convert("RGBA")))
        frame_durations.append(duration)

    return AnimatedTexture(texture_ids, frame_durations)


def _create_texture_from_image(img):
    img_data = np.array(img, dtype=np.uint8)

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA,
        img.width, img.height, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, img_data
    )
    return texture_id

def load_video_frame(cap):
    """
    Carga un frame de OpenCV como textura.
    cap = cv2.VideoCapture('video.mp4')
    Llama esto cada frame para animación.
    """
    import cv2
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # reinicia el video
        ret, frame = cap.read()

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    frame = cv2.flip(frame, 0)
    h, w = frame.shape[:2]

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0,
                 GL_RGBA, GL_UNSIGNED_BYTE, frame)
    return texture_id
