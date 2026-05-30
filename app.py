from flask import Flask, render_template, request, redirect, Response, send_file, jsonify
import os
from speed_tracker import generate_frames

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
LOG_FILE = "logs/logs.txt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs("logs", exist_ok=True)

video_path_global = None


def log_writer(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    global video_path_global

    file = request.files['video']
    if file:
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        video_path_global = path

        # clear old logs
        open(LOG_FILE, "w").close()

    return redirect('/video')


@app.route('/video')
def video():
    return render_template("video.html")


@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(video_path_global, log_writer),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/logs')
def logs():
    return render_template("logs.html")


@app.route('/get_logs')
def get_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify([])

    with open(LOG_FILE) as f:
        lines = f.readlines()

    return jsonify(lines)


@app.route('/download_logs')
def download_logs():
    return send_file(LOG_FILE, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)