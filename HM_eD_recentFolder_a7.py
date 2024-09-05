#히스토그램 매칭, e드라이브의 최근 생성된 폴더, a7 raw파일 jpg 변환,exif 유지
#실행 전 taget_exposure 조정
import os
import cv2
import numpy as np
import rawpy
import exifread
import piexif
from PIL import Image

def load_image(image_path):
    if image_path.lower().endswith(('.arw', '.dng')):  # '.dng' 추가
        with rawpy.imread(image_path) as raw:
            rgb = raw.postprocess()
            return cv2.cvtColor(np.array(rgb), cv2.COLOR_RGB2BGR)
    elif image_path.lower().endswith(('.png', '.jpg', '.jpeg')):
        return cv2.imread(image_path)
    else:
        raise ValueError("Unsupported image format")

def get_exif(image_path):
    with open(image_path, 'rb') as f:
        original_exif_data = piexif.load(f.read())
    exif_bytes = piexif.dump(original_exif_data)
    return exif_bytes

def adjust_exposure(image, target_exposure, max_delta=50):
    current_exposure = np.mean(image)
    delta_exposure = target_exposure - current_exposure
    delta_exposure = np.clip(delta_exposure, -max_delta, max_delta)
    adjusted_image = cv2.convertScaleAbs(image, alpha=1.0, beta=delta_exposure)
    return adjusted_image

def adjust_contrast(image, alpha=1.0):
    beta = 0
    return cv2.convertScaleAbs(image, alpha=alpha, beta=beta)

def check_contrast(image, threshold=50):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    std_dev = np.std(gray_image)
    return std_dev < threshold

def apply_clahe(image, clip_limit=1.2, tile_grid_size=(8, 8)):
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
    if len(image.shape) == 3:
        lab_image = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab_image)
        cl = clahe.apply(l_channel)
        merged_channels = cv2.merge((cl, a_channel, b_channel))
        return cv2.cvtColor(merged_channels, cv2.COLOR_LAB2BGR)
    else:
        return clahe.apply(image)

def process_image(image_path, result_folder, target_exposure):
    exif_bytes = get_exif(image_path)
    image = load_image(image_path)
    adjusted_image = adjust_exposure(image, target_exposure)
    contrast_adjusted_image = adjust_contrast(adjusted_image)
    if check_contrast(contrast_adjusted_image):
        contrast_adjusted_image = adjust_contrast(contrast_adjusted_image, alpha=1.0)
    final_adjusted_image = apply_clahe(contrast_adjusted_image)
    image_name = os.path.basename(image_path)
    image_name_without_extension = os.path.splitext(image_name)[0]
    result_image_path = os.path.join(result_folder, image_name_without_extension + '.jpg')
    final_pil_image = Image.fromarray(cv2.cvtColor(final_adjusted_image, cv2.COLOR_BGR2RGB))
    final_pil_image.save(result_image_path, 'JPEG', quality=100, exif=exif_bytes)

def get_most_recent_folder(root_folder):
    all_folders = [os.path.join(root_folder, f) for f in os.listdir(root_folder) if os.path.isdir(os.path.join(root_folder, f))]
    most_recent_folder = max(all_folders, key=os.path.getmtime)
    return most_recent_folder

recent_folder = get_most_recent_folder("E:/")

image_folder = os.path.join(recent_folder, "source/origin/raw")
result_folder = os.path.join(recent_folder, "source/photo/a7")

os.makedirs(result_folder, exist_ok=True)

target_exposure = 140  # 타겟 노출도

for image_file in os.listdir(image_folder):
    image_path = os.path.join(image_folder, image_file)
    try:
        process_image(image_path, result_folder, target_exposure)
    except ValueError as e:
        print(f"Skipping {image_file}: {e}")
