import time
import cv2
import base64


class VideoService:

    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None

    def start_camera(self):
        if self.camera is not None and self.camera.isOpened():
            return True

        # CAP_DSHOW accelere enormement la webcam sous Windows 11
        self.camera = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.camera.isOpened():
            self.camera = cv2.VideoCapture(self.camera_index)

        if not self.camera.isOpened():
            raise RuntimeError("Impossible d'ouvrir la camera")

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return True

    def capture_frame(self):
        if self.camera is None or not self.camera.isOpened():
            raise RuntimeError("Camera non demarree")

        # Vider l'eventuelle ancienne image en memoire tampon
        self.camera.grab()
        success, frame = self.camera.retrieve()
        if not success or frame is None:
            success, frame = self.camera.read()

        if not success or frame is None:
            raise RuntimeError("Impossible de capturer une image")

        return frame

    def frame_to_base64(self, frame):
        small = cv2.resize(frame, (400, 300))
        success, buffer = cv2.imencode(".jpg", small, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
        if not success:
            raise RuntimeError("Erreur encodage image")
        return base64.b64encode(buffer.tobytes()).decode("utf-8")

    def generate_mjpeg(self):
        while self.camera is not None and self.camera.isOpened():
            try:
                frame = self.capture_frame()
                small = cv2.resize(frame, (480, 360))
                ok, buf = cv2.imencode(".jpg", small, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                if ok:
                    yield (b"--frame\r\n"
                           b"Content-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")
                time.sleep(0.04)  # ~25 images/sec
            except Exception:
                time.sleep(0.1)

    def stop_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None
