from flask import Flask, request, jsonify, send_file, Response
import cv2
import os
import time
import subprocess

app = Flask(__name__)

# Directories for uploaded and processed videos
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Raspberry Pi Camera Stream URL (Change this to your Pi's IP)
raspberry_pi_ip = "192.168.52.236:8080"  # Replace with your actual Raspberry Pi IP
video_url = f"http://{raspberry_pi_ip}:8080/video"  # HTTP Stream URL

# Initialize VideoCapture
cap = cv2.VideoCapture(video_url)
video_output_path = os.path.join(UPLOAD_FOLDER, "captured_video.mp4")

# Video Writer setup
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4 codec

@app.route("/download", methods=["GET"])
def download_file():
    """Allows users to download the saved video."""
    if os.path.exists(video_output_path):
        return send_file(video_output_path, as_attachment=True)
    return jsonify({"error": "No recorded video found"}), 404

def generate_frames():
    """Generates video frames for live streaming in Flask."""
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Live video stream endpoint."""
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def record_video():
    """Records the Raspberry Pi video stream for 15 seconds, then runs main.py and stops Flask."""
    global cap

    if os.path.exists(video_output_path):
        os.remove(video_output_path)  # ✅ Remove any existing video before recording

    frame_width = int(cap.get(3)) if cap.isOpened() else 640
    frame_height = int(cap.get(4)) if cap.isOpened() else 480
    fps = 20

    out = cv2.VideoWriter(video_output_path, fourcc, fps, (frame_width, frame_height))
    
    print("Recording started...")

    start_time = time.time()
    while time.time() - start_time < 15:  # ✅ Stop recording after 15s
        success, frame = cap.read()
        if not success:
            continue
        out.write(frame)  # Save frame to MP4 file

    out.release()  # Stop recording
    cap.release()
    print(f"Recording completed and saved as: {video_output_path}")

    # ✅ Run main.py AFTER recording stops
    print("Running main.py...")
    subprocess.run(["python", "main.py"])

    # ✅ Stop the Flask server AFTER main.py finishes
    print("Stopping Flask server...")
    time.sleep(1)  # Small delay to ensure clean shutdown
    from playsound import playsound

    audio_path = r"D:\College\Smart_Spectacle\audio\product_info_audio.mp3"
    playsound(audio_path)
    os._exit(0)  # Forcefully stop Flask

if __name__ == "__main__":
    # ✅ Record video immediately when server starts, NO separate thread
    record_video()
    app.run(debug=True)
