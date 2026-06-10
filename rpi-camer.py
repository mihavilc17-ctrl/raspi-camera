from picamera2 import Picamera2
import numpy as np

# === PARAMETRI ===
RESOLUTION = (1920, 1080)
FPS = 30
EXPOSURE_US = 5000        # exposure v mikrosekundah
N_FRAMES = 100            # število slik
ROI = (400, 300, 800, 600)  # (x, y, width, height) — None za polno sliko

# === IZRAČUN ===
FRAME_DURATION = int(1e6 / FPS)  # v mikrosekundah

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": RESOLUTION, "format": "RGB888"}
)
picam2.configure(config)

picam2.set_controls({
    "ExposureTime": EXPOSURE_US,
    "FrameDurationLimits": (FRAME_DURATION, FRAME_DURATION),
    "AeEnable": False,
    "AwbEnable": False,   # izklopi auto white balance za konsistentnost
    "AnalogueGain": 1.0,
})

# ROI — ScalerCrop: (x, y, width, height) v pikslih senzorja
if ROI is not None:
    picam2.set_controls({"ScalerCrop": ROI})

picam2.start()

# Počakaj da se nastavitve stabilizirajo (vsaj 10 frameov)
for _ in range(10):
    picam2.wait_frame()

# === ZAJEM ===
frames = np.empty((N_FRAMES, *RESOLUTION[::-1], 3), dtype=np.uint8)
timestamps = np.empty(N_FRAMES, dtype=np.int64)

for i in range(N_FRAMES):
    request = picam2.wait_frame()
    frames[i] = request.make_array("main")
    timestamps[i] = request.get_metadata()["SensorTimestamp"]
    request.release()

picam2.stop()

# === ANALIZA NATANČNOSTI ===
diffs = np.diff(timestamps) / 1e6  # v ms
print(f"Zajeto: {N_FRAMES} slik")
print(f"Povprečni interval: {diffs.mean():.3f} ms (cilj: {1000/FPS:.3f} ms)")
print(f"Std deviacija: {diffs.std():.3f} ms")
print(f"Frames shape: {frames.shape}")

# Polna resolucija senzorja HQ kamere je 4056 x 3040
# ROI je izrez iz tega — kamera nato skalira na tvojo RESOLUTION

# Primer: sredinski izrez
sensor_w, sensor_h = 4056, 3040
roi_w, roi_h = 2028, 1520  # polovica senzorja
x = (sensor_w - roi_w) // 2
y = (sensor_h - roi_h) // 2

picam2.set_controls({"ScalerCrop": (x, y, roi_w, roi_h)})