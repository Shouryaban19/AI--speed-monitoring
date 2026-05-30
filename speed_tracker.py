import cv2
import numpy as np
import time
from ultralytics import YOLO
from sort import *

CALIBRATION_DISTANCE = 5
CALIBRATION_PIXELS = 200
PIXEL_TO_METER = CALIBRATION_DISTANCE / CALIBRATION_PIXELS
FRAME_RATE = 30

model = YOLO('yolov8n.pt')

with open("classes.txt") as f:
    classnames = f.read().splitlines()


def generate_frames(video_path, log_callback):
    cap = cv2.VideoCapture(video_path)
    tracker = Sort(max_age=30)

    prev_positions = {}
    max_speeds = {}

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (800, 450))
        detections = np.empty((0, 5))

        results = model(frame, stream=True)

        for info in results:
            for box in info.boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                conf = box.conf[0]
                cls = int(box.cls[0])

                label = classnames[cls]

                if label in ['car', 'truck', 'bus'] and conf > 0.6:
                    x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))
                    detections = np.vstack((detections, [x1, y1, x2, y2, conf]))

        track_results = tracker.update(detections)
        
        
        for res in track_results:
            x1, y1, x2, y2, obj_id = map(int, res)

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if obj_id in prev_positions:
                px, py, _ = prev_positions[obj_id]
                dist = np.sqrt((cx - px)**2 + (cy - py)**2)
                speed = (dist * PIXEL_TO_METER) * FRAME_RATE * 3.6
            else:
                speed = 0

            prev_positions[obj_id] = (cx, cy, time.time())

            if obj_id not in max_speeds:
                max_speeds[obj_id] = speed
                log_callback(f"ID: {obj_id} | Max Speed: {speed:.2f} km/h")
            elif speed > max_speeds[obj_id]:
                max_speeds[obj_id] = speed
                log_callback(f"ID: {obj_id} | Max Speed: {speed:.2f} km/h")


            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f'ID {obj_id} | {speed:.1f} km/h',
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)

            

        # Convert to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes + b'\r\n')

    cap.release()