import torch
import os
from PIL import Image
import numpy as np
import copy
import cv2
from segment_anything import SamPredictor, SamAutomaticMaskGenerator, sam_model_registry


def load_sam_model(model_path):
    if model_path is None:
        return False, "Please provide path to sam model!"
    if not os.path.exists(model_path):
        return False, "sam model dosen't exist!"
    
    model_type = '_'.join(model_path.split('_')[1:-1])
    sam = sam_model_registry[model_type](checkpoint=model_path)
    sam.to(device=device)
    sam.eval()
    return sam, None

def mask_entire_image(sam_model, image):
    predictor = SamPredictor(sam_model)
    mask_generator = SamAutomaticMaskGenerator(sam_model)
    masks = mask_generator.generate(image)
    return masks

def load_img_from_path(img_dir_path):
    if img_dir_path is None:
        return False, "Please provide path to image directory"
    if not os.path.exists(img_dir_path):
        return False, "image directory dosen't exist!"

    img_list = []
    # append all the img in the img_path to the list
    for filename in os.listdir(img_dir_path):
        desired_ext = [".jpg", ".png", ".jpeg",  ".JPG", ".PNG", ".JPEG"]
        if any(filename.endswith(ext) for ext in desired_ext):
            img_path = os.path.join(img_dir_path, filename)
            # open filename image as numpy
            img = Image.open(img_path)
            img_array = np.array(img)
            img_list.append(img_array)
    return img_list, None

def show_masks(img_np, masks, alpha=0.5):
    np.random.seed(0)
    for mask in masks:
        color = np.random.rand(3)
        img_np[mask] = img_np[mask] * (1 - alpha) + color * alpha * 255
    return img_np

def show_boxes(img_np, boxes, color=(255, 0, 0, 255), thickness=2, show_index=False):
    if boxes is None:
        return img_np

    for idx, box in enumerate(boxes):
        x, y, w, h = box
        cv2.rectangle(img_np, (x, y), (w, h), color, thickness)
        if show_index:
            font = cv2.FONT_HERSHEY_SIMPLEX
            text = str(idx)
            textsize = cv2.getTextSize(text, font, 1, 2)[0]
            cv2.putText(img_np, text, (x, y+textsize[1]), font, 1, color, thickness)
    
    return img_np

def create_mask_output(img_np, masks, box_filters):
    print("Creating mask output")

    img_masked, masks_gallery, img_matted = [], [], []
    box_filters = box_filters.astype(int) if box_filters is not None else None
    for mask in masks:
        masks_gallery.append(Image.fromarray(np.any(mask, axis=0)))

        blended_image = show_masks(show_boxes(img_np, box_filters), mask)
        img_masked.append(Image.fromarray(blended_image))

        img_np[~np.any(mask, axis=0)] = np.zeros(len(img_np.shape))
        img_matted.append(Image.fromarray(img_np))

    return (img_masked, masks_gallery, img_matted), None

def sam_only_predict(sam_model_dir, img_np, positive_points=[], negative_points=[], text_prompt=None, box_filters=None):
    print("Start SAM Processing")
    # check if sam_model_dir exists
    sam, msg = load_sam_model(sam_model_dir)
    if not sam:
        print(msg)
        return False
    
    img_np_rgb = img_np[..., :3]
    print(f"Image shape: {img_np.shape}")
    predictor = SamPredictor(sam)
    predictor.set_image(img_np_rgb)

    dino_enabled = text_prompt is not None and len(text_prompt) > 0
    if dino_enabled and box_filters.shape[0]>1:
        print(f"SAM running with {box_filters.shape[0]} boxes, discard point prompts")
        boxes_transformed = predictor.transform.apply_boxes_torch(box_filters, img_np_rgb.shape[:2])
        masks, _, _ = predictor.predict(
            point_coords=None,
            point_labels=None,
            boxes=boxes_transformed.to(device),
            multimask_output=True
            )
        masks = masks.permute(1,0,2,3).cpu().numpy()
    else:
        num_boxes = 0 if box_filters is None else box_filters.shape[0]
        num_points = len(positive_points) + len(negative_points)
        if not num_boxes and  not num_points:
            return False, "Please provide at least one point or text prompt"
        print(f"SAM running with {num_boxes} boxes, {len(positive_points)} positive points and {len(negative_points)} negative points")
        point_coords = torch.cat([positive_points, negative_points], dim=0) if num_points else None
        point_labels = torch.cat([torch.ones(len(positive_points)), torch.zeros(len(negative_points))], dim=0) if num_points else None
        masks, _, _ = predictor.predict(
            point_coords=point_coords,
            point_labels=point_labels,
            box=box_filters[0],
            multimask_output=True
        )
        masks = masks[:, None, ...]
    
    (img_masked, masks_gallery, img_matted), msg =  create_mask_output(img_np, masks, box_filters)
    # save img_masked, masks_gallery, img_matted to files
    img_masked[0].save("/root/fstudio/sam_output/img_masked.png")
    masks_gallery[0].save("/root/fstudio/sam_output/masks_gallery.png")
    img_matted[0].save("/root/fstudio/sam_output/img_matted.png")
    return img_masked, masks_gallery, img_matted

    


if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    sam_model_path = "/root/autodl-tmp/models/sam/sam_vit_l_0b3195.pth"
    images, msg = load_img_from_path("/root/autodl-tmp/sd-dataset/alex/alex-768")
    if not images:
        print(msg)

    box_filters = np.array([[100, 100, 650, 650]])
    sam_only_predict(sam_model_path, images[0], box_filters=box_filters)

    
    # masks = mask_entire_image(sam, images[0])