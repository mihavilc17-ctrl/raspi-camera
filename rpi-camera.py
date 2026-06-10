from picamera2 import Picamera2
import numpy as np

# === PARAMETRI ===
RESOLUTION = (1920, 1080)
FPS = 30
EXPOSURE_US = 5000
N_FRAMES = 100
ROI = (400, 300, 800, 600)

# === IZRAČUN ===
FRAME_DURATION = int(1e6 / FPS)

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": RESOLUTION, "format": "RGB888"}
)
picam2.configure(config)

picam2.set_controls({
    "ExposureTime": EXPOSURE_US,
    "FrameDurationLimits": (FRAME_DURATION, FRAME_DURATION),
    "AeEnable": False,
    "AwbEnable": False,
    "AnalogueGain": 1.0,
})

if ROI is not None:
    picam2.set_controls({"ScalerCrop": ROI})

picam2.start()

# Počakaj da se nastavitve stabilizirajo
for _ in range(10):
    request = picam2.capture_request()
    request.release()

# === ZAJEM ===
frames = np.empty((N_FRAMES, *RESOLUTION[::-1], 3), dtype=np.uint8)
timestamps = np.empty(N_FRAMES, dtype=np.int64)

for i in range(N_FRAMES):
    request = picam2.capture_request()
    frames[i] = request.make_array("main")
    timestamps[i] = request.get_metadata()["SensorTimestamp"]
    request.release()

picam2.stop()

# === ANALIZA NATANČNOSTI ===
diffs = np.diff(timestamps) / 1e6
print(f"Zajeto: {N_FRAMES} slik")
print(f"Povprečni interval: {diffs.mean():.3f} ms (cilj: {1000/FPS:.3f} ms)")
print(f"Std deviacija: {diffs.std():.3f} ms")
print(f"Frames shape: {frames.shape}")