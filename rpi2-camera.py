# ----- ohranitev vseh 10ih bitov ----
config = picam2.create_video_configuration(
    main={"size": RESOLUTION, "format": "RGB888"},
    raw={"format": "SBGGR10_CSI2P"}  # raw stream ohrani 10-bit
)

request = picam2.capture_request()
raw_array = request.make_array("raw")  # 10-bit podatki
rgb_array = request.make_array("main")  # 8-bit za prikaz

frames = np.empty((N_FRAMES, *RESOLUTION[::-1]), dtype=np.uint16)