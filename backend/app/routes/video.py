from flask import Blueprint, jsonify, Response
from app.services.video_service import VideoService

video_bp = Blueprint("video", __name__)

camera = VideoService(camera_index=0)


@video_bp.route("/api/video/start", methods=["POST"])
def start_video():
    try:
        camera.start_camera()
        return jsonify({
            "success": True,
            "message": "Camera demarree"
        })
    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@video_bp.route("/api/video/stream", methods=["GET"])
def stream_video():
    return Response(
        camera.generate_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@video_bp.route("/api/video/frame", methods=["GET"])
def get_video_frame():
    try:
        frame = camera.capture_frame()
        image = camera.frame_to_base64(frame)
        return jsonify({
            "success": True,
            "image": image
        })
    except Exception as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 500


@video_bp.route("/api/video/stop", methods=["POST"])
def stop_video():
    camera.stop_camera()
    return jsonify({
        "success": True,
        "message": "Camera arretee"
    })
