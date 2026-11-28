
import cv2
import base64


class VideoService:

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None

    def start_camera(self):
        self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            raise RuntimeError("Impossible d'ouvrir la camera")

        return True

    def capture_frame(self):

        if self.camera is None or not self.camera.isOpened():
            raise RuntimeError("Camera non demarree")

        success, frame = self.camera.read()

        if not success:
            raise RuntimeError("Impossible de capturer une image")

        return frame

    def frame_to_base64(self, frame):

        success, buffer = cv2.imencode(".jpg", cv2.resize(frame, (480, 360)), [int(cv2.IMWRITE_JPEG_QUALITY), 70])

        if not success:
            raise RuntimeError("Erreur encodage image")

        image_base64 = base64.b64encode(
            buffer.tobytes()
        ).decode("utf-8")

        return image_base64

    def stop_camera(self):

        if self.camera is not None:
            self.camera.release()
            self.camera = None
