import numpy as np
from PIL import Image

def image_anomalies(img: Image.Image) -> list:
    arr = np.asarray(img.convert("L"))
    anomalies = []

    std = float(arr.std())
    if std > 70:
        anomalies.append("High contrast: possible overwriting.")

    hist, _ = np.histogram(arr, bins=16, range=(0, 255))
    if (hist.max() / (hist.mean() + 1e-6)) > 6:
        anomalies.append("Histogram anomaly: possible font/ink inconsistency.")

    return anomalies
