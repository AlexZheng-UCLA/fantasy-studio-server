from src.function import full_process

def _full_process(metadata):

    sam_model_type = metadata['sam_model_type']
    dino_model_type = metadata['dino_model_type']
    text_prompt = metadata['text_prompt']
    num_boxes = metadata['num_boxes']
    box_threshold = metadata['box_threshold']
    dilation_amt = metadata['dilation_amt']
    img_source_dir = metadata['img_source_dir']
    background_dir = metadata['background_dir']
    save_dir = metadata['save_dir']
    multimask_output = metadata['multimask_output']    
    mask_option = metadata['mask_option']              # ["1", "2", "3, "largest", "smallest"]

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
        mask_option=mask_option,
        save_image=True, 
        save_mask=True, 
        save_background=True,
        save_blend=True, 
        save_image_masked=True,
        save_process=True,
    )
    return process_info