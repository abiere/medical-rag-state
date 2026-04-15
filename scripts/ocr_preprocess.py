#!/usr/bin/env python3
"""
ocr_preprocess.py — OpenCV-based image preprocessing for OCR.

Functions:
  preprocess_page(pil_image) -> PIL.Image
      Deskew, denoise, CLAHE contrast enhancement, Otsu binarization.
  detect_adaptive_dpi(pil_image) -> int
      Suggest DPI for re-rendering (150 / 200 / 300) based on text density.
  is_mostly_image(pil_image) -> bool
      True when the page is mostly a diagram/photo with < 5% text coverage.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def preprocess_page(pil_image):
    """
    Apply deskew → denoise → CLAHE → Otsu binarization.
    Returns a PIL.Image ready for OCR.
    Falls back to the original image on any error.
    """
    try:
        import cv2
        import numpy as np
        from PIL import Image as _PIL

        img  = np.array(pil_image.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        # 1. Deskew
        gray = _deskew(gray)

        # 2. Denoise
        gray = cv2.fastNlMeansDenoising(gray, h=15,
                                         templateWindowSize=7,
                                         searchWindowSize=21)

        # 3. CLAHE contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray  = clahe.apply(gray)

        # 4. Otsu binarization
        _, binary = cv2.threshold(gray, 0, 255,
                                  cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return _PIL.fromarray(binary)

    except Exception as e:
        logger.warning("preprocess_page failed (%s) — using original", e)
        return pil_image


def _deskew(gray):
    """
    Estimate skew angle via minAreaRect on dark-pixel coords and rotate.
    Returns corrected grayscale ndarray.  Skips if angle < 0.5 degrees.
    """
    import cv2
    import numpy as np

    _, thresh = cv2.threshold(gray, 0, 255,
                               cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    coords = np.column_stack(np.where(thresh > 0))

    if len(coords) < 100:
        return gray

    angle = cv2.minAreaRect(coords)[-1]
    # minAreaRect returns angles in [-90, 0); correct the range
    if angle < -45:
        angle = 90 + angle

    if abs(angle) < 0.5:
        return gray

    h, w   = gray.shape
    center = (w // 2, h // 2)
    M      = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(gray, M, (w, h),
                              flags=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REPLICATE)
    logger.debug("Deskewed %.2f°", angle)
    return rotated


def detect_adaptive_dpi(pil_image) -> int:
    """
    Estimate needed DPI from average character-blob height.

    Returns:
        150 — characters are large (high-res scan or large font)
        200 — medium characters
        300 — small characters (need more resolution for OCR)
    """
    try:
        import cv2
        import numpy as np

        img = np.array(pil_image.convert("L"))
        _, binary = cv2.threshold(img, 0, 255,
                                   cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        num_labels, stats, _, _ = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        if num_labels < 10:
            return 300

        heights = [
            stats[i, cv2.CC_STAT_HEIGHT]
            for i in range(1, num_labels)
            if 3 < stats[i, cv2.CC_STAT_HEIGHT] < 200
            and stats[i, cv2.CC_STAT_WIDTH] > 2
        ]

        if not heights:
            return 300

        avg_h = sum(heights) / len(heights)
        if avg_h < 15:
            return 300
        if avg_h < 25:
            return 200
        return 150

    except Exception as e:
        logger.debug("detect_adaptive_dpi failed (%s) — returning 300", e)
        return 300


def is_mostly_image(pil_image, text_threshold: float = 0.05) -> bool:
    """
    Return True when < text_threshold fraction of the page appears to contain
    text-like connected components.  Used to skip OCR on pure diagram pages.
    """
    try:
        import cv2
        import numpy as np

        img = np.array(pil_image.convert("L"))
        _, binary = cv2.threshold(img, 0, 255,
                                   cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        num_labels, stats, _, _ = cv2.connectedComponentsWithStats(
            binary, connectivity=8
        )

        page_area = img.shape[0] * img.shape[1]
        text_area = sum(
            stats[i, cv2.CC_STAT_AREA]
            for i in range(1, num_labels)
            if 3 < stats[i, cv2.CC_STAT_HEIGHT] < 50
            and 2 < stats[i, cv2.CC_STAT_WIDTH] < 200
        )

        ratio = text_area / page_area if page_area > 0 else 0
        return ratio < text_threshold

    except Exception as e:
        logger.debug("is_mostly_image failed (%s) — assuming text page", e)
        return False
