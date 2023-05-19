import numpy as np
import os
import cv2
from PIL import Image

def load_img_from_path(img_dir_path):
    if img_dir_path is None:
        return False, False, "Please provide path to image directory"
    if not os.path.exists(img_dir_path):
        return False, False, "image directory dosen't exist!"

    img_list = []
    filename_list = []
    # append all the img in the img_path to the list
    for filename in os.listdir(img_dir_path):
        desired_ext = [".jpg", ".png", ".jpeg",  ".JPG", ".PNG", ".JPEG"]
        if any(filename.endswith(ext) for ext in desired_ext):
            filename_list.append(filename)
            img_path = os.path.join(img_dir_path, filename)
            # open filename image as numpy
            img = Image.open(img_path)
            img_list.append(img)
    return img_list, filename_list, None


def move_masked_add_background(
    file_name, 
    save_dir, 
    img_np,
    background_list, 
    merged_masks, 
    save_image
):
    image = Image.fromarray(img_np)
    width, height = image.size
    size = max(width, height)
    # only take the first mask
    mask = merged_masks
    print(f" mask shape: {mask.shape}")
    processed_images = []
    for idx, background in enumerate(background_list):

        # find the mask width and height
        mask_height = np.sum(mask, axis=0).max()
        mask_width = np.sum(mask, axis=1).max()
        mask_median_hpos = np.mean(np.median(np.where(mask), axis=1)).astype(int)
        mask_median_vpos = np.mean(np.median(np.where(mask), axis=0)).astype(int)

        hshift = width // 2 - mask_median_hpos
        mask_shifted = np.roll(mask, hshift, axis=1)
        # Since np.roll wraps the values around, we want to zero out the wrapped values on the side
        mask_shifted[:, :hshift] = 0

        background = background.resize((size, size))
        background_np = np.array(background)
        background_np = background_np[:height, :width, :]

        background_np[mask_shifted] = np.zeros(len(background_np.shape))
        img_processed = Image.fromarray(background_np)
        if save_image:
            img_processed.save(os.path.join(save_dir, f"{file_name}_processed_{idx}.png"))

        processed_images.append(img_processed)
    return processed_images, None


def load_background_from_path(background_dir):
    if background_dir is None:
        return None, "Please provide path to background directory"
    if not os.path.exists(background_dir):
        return None, "background directory dosen't exist!"
    
    background_list = []
    # append all the img in the img_path to the list
    for filename in os.listdir(background_dir):
        desired_ext = [".jpg", ".png", ".jpeg",  ".JPG", ".PNG", ".JPEG"]
        if any(filename.endswith(ext) for ext in desired_ext):
            background_path = os.path.join(background_dir, filename)
            # open filename image as numpy
            background = Image.open(background_path)
            background_list.append(background)
    return background_list, None


def generate_pure_background(width, height, save_dir):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)

    colors = {
        'black': [0, 0, 0],
        'white': [255, 255, 255],
        'red': [255, 0, 0],
        'green': [0, 255, 0],
        'blue': [0, 0, 255],
    }

    # Generate images for each color
    for color, rgb in colors.items():
        array = np.full((1024, 1024, 3), rgb, dtype=np.uint8)
        img = Image.fromarray(array)
        img.save(os.path.join(save_dir, f'{color}_image.png'))


if __name__ == "__main__":
    # generate_pure_background(1024, 1024, save_dir="/root/fstudio/backgrounds")
    background_list, msg = load_background_from_path("/root/fstudio/backgrounds")
    if background_list is None:
        print(msg)
    
    
    
    