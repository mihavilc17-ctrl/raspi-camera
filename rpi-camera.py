from picamera2 import Picamera2
import numpy as np

# === PARAMETRI ===
FPS = 100
EXPOSURE_US = 5000
N_FRAMES = 100
ROI_X, ROI_Y = 1522, 1140      # začetek izreza (sredina senzorja)
ROI_W, ROI_H = 1332, 990       # velikost izreza
RESOLUTION = (ROI_W, ROI_H)    # resolucija = ROI, brez skaliranja

# === IZRAČUN ===
FRAME_DURATION = int(1e6 / FPS)

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": RESOLUTION, "format": "RGB888"},
    buffer_count=8
)

picam2.configure(config)

picam2.set_controls({
    "ExposureTime": EXPOSURE_US,
    "FrameDurationLimits": (FRAME_DURATION, FRAME_DURATION),
    "AeEnable": False,
    "AwbEnable": False,
    "AnalogueGain": 1.0,
    "ScalerCrop": (696, 528, 2664, 1980),
})

# Počakaj da se nastavitve stabilizirajo
for _ in range(10):
    request = picam2.capture_request()
    request.release()

import time

picam2.start()

# Stabilizacija
for _ in range(10):
    picam2.capture_array("main")

# === ZAJEM — brez capture_request overhead ===
frames = np.empty((N_FRAMES, ROI_H, ROI_W, 3), dtype=np.uint8) #? 8bit
timestamps = np.empty(N_FRAMES, dtype=np.int64)

t_start = time.time()

for i in range(N_FRAMES):
    request = picam2.capture_request()
    if request is None:
        print(f"Timeout pri frame {i}!")
        break
    np.copyto(frames[i], request.make_array("main"))  # direktna kopija brez alokacije
    timestamps[i] = request.get_metadata()["SensorTimestamp"]
    request.release()

    if i % 10 == 0:
        elapsed = time.time() - t_start
        print(f"Frame {i}/{N_FRAMES} — {elapsed:.2f}s — trenutni FPS: {i/elapsed:.1f}")

picam2.stop()

# === ANALIZA NATANČNOSTI ===
diffs = np.diff(timestamps) / 1e6
print(f"Zajeto: {N_FRAMES} slik")
print(f"Povprečni interval: {diffs.mean():.3f} ms (cilj: {1000/FPS:.3f} ms)")
print(f"Std deviacija: {diffs.std():.3f} ms")
print(f"Frames shape: {frames.shape}")