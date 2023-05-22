import os 
import base64
from src.function import full_process

def _get_images(user):
    save_dir = f'/root/fstudio-storage/{user}/output'
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    image_files = os.listdir(save_dir)
    images = []
    for image_file in image_files:
        with open(os.path.join(save_dir, image_file), "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
            images.append(img_base64)
    return images


def _upload_files(user, files):
    user_dir = f'/root/fstudio-storage/{user}'
    save_dir = f'/root/fstudio-storage/{user}/upload'
    filenames = []
    save_paths = []
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for file in files:
        if file:
            filenames.append(file.filename)
            save_path = os.path.join(save_dir, file.filename)
            file.save(save_path)
            save_paths.append(save_path)
    return filenames, save_paths 


def _full_process(metadata):
    user = metadata['user']
    user_dir = f'/root/fstudio-storage/{user}'
    save_dir = f'/root/fstudio-storage/{user}/output'

    sam_model_type = metadata['sam_model_type']
    dino_model_type = metadata['dino_model_type']
    text_prompt = metadata['text_prompt']
    num_boxes = int(metadata['num_boxes'])
    box_threshold = float(metadata['box_threshold'])
    dilation_amt = metadata['dilation_amt']
    img_source_dir = os.path.join(user_dir, 'upload')
    background_dir = '/root/fstudio-server/background'
    save_dir = save_dir
    multimask_output = metadata['multimask_output']    
    # mask_option = metadata['mask_option']              # ["1", "2", "3, "largest", "smallest"]

    process_info = full_process(
        sam_model_type=sam_model_type, 
        dino_model_type=dino_model_type, 
        text_prompt=text_prompt, 
        num_boxes=num_boxes,
        box_threshold=box_threshold, 
        dilation_amt=dilation_amt,
        img_source_dir=img_source_dir, 
        background_dir=background_dir,
        save_dir=save_dir,
        multimask_output=multimask_output,
        # mask_option=mask_option,
        save_image=True, 
        save_mask=True, 
        save_background=False,
        save_blend=True, 
        save_image_masked=True,
        save_process=True,
    )

    return process_info