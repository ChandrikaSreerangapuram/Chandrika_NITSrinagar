import cv2
import numpy as np
from PIL import Image

def to_cv(img: Image.Image):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def to_pil(img_cv):
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    return Image.fromarray(img_rgb)

def preprocess_image(img: Image.Image) -> Image.Image:
    cv = to_cv(img)
    gray = cv2.cvtColor(cv, cv2.COLOR_BGR2GRAY)

    den = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    bin_img = cv2.adaptiveThreshold(
        den, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )

    coords = np.column_stack(np.where(bin_img > 0))
    angle = 0.0
    try:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = bin_img.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        bin_img = cv2.warpAffine(bin_img, M, (w, h),
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)
    except:
        pass

    return to_pil(cv2.cvtColor(bin_img, cv2.COLOR_GRAY2BGR))
