import numpy as np

class Sort:
    def __init__(self, max_age=5):
        self.next_id = 1
        self.tracks = []
        self.max_age = max_age

    def update(self, detections=np.empty((0, 5))):
        updated_tracks = []

        for det in detections:
            x1, y1, x2, y2, score = det

            cx = (x1 + x2) / 2
            cy = (y1 + y2) / 2

            matched = False

            # Try to match with existing tracks
            for track in self.tracks:
                tx, ty, tid, age = track

                dist = np.sqrt((cx - tx)**2 + (cy - ty)**2)

                if dist < 50:  # threshold
                    updated_tracks.append([x1, y1, x2, y2, tid])
                    track[0], track[1] = cx, cy
                    track[3] = 0
                    matched = True
                    break

            if not matched:
                updated_tracks.append([x1, y1, x2, y2, self.next_id])
                self.tracks.append([cx, cy, self.next_id, 0])
                self.next_id += 1

        # Age tracks
        for track in self.tracks:
            track[3] += 1

        # Remove old tracks
        self.tracks = [t for t in self.tracks if t[3] <= self.max_age]

        return np.array(updated_tracks)