from picamera2 import Picamera2
import numpy as np

ROI_W, ROI_H = 1332, 990
FPS = 50  # realno za Pi 3B
N_FRAMES = 100
FRAME_DURATION = int(1e6 / FPS)

picam2 = Picamera2()

config = picam2.create_video_configuration(
    main={"size": (ROI_W, ROI_H), "format": "RGB888"},
    buffer_count=4  # manj bufferjev = manj RAM
)
picam2.configure(config)

picam2.set_controls({
    "ExposureTime": FRAME_DURATION - 100,
    "FrameDurationLimits": (FRAME_DURATION, FRAME_DURATION),
    "AeEnable": False,
    "AwbEnable": False,
    "AnalogueGain": 1.0,
    "ScalerCrop": (696, 528, 2664, 1980),
})

picam2.start()

# Stabilizacija
for _ in range(10):
    picam2.capture_array("main")

# Shrani sproti na disk — ne drži vsega v RAM
timestamps = np.empty(N_FRAMES, dtype=np.int64)

with open("frames.bin", "wb") as f:
    for i in range(N_FRAMES):
        request = picam2.capture_request(wait=2.0)
        if request is None:
            print(f"Timeout pri frame {i}")
            break
        f.write(request.make_array("main").tobytes())
        timestamps[i] = request.get_metadata()["SensorTimestamp"]
        request.release()
        
        if i % 10 == 0:
            print(f"Frame {i}/{N_FRAMES}")

picam2.stop()
np.save("timestamps.npy", timestamps)

diffs = np.diff(timestamps) / 1e6
print(f"Povprečni interval: {diffs.mean():.3f} ms (cilj: {1000/FPS:.3f} ms)")
print(f"Std deviacija: {diffs.std():.3f} ms")
print("Shranjeno: frames.bin, timestamps.npy")