\
import torch
import torchvision.transforms as transforms
from PIL import Image
import os
import argparse
import math

# Attempt to import the model.
# This assumes 'models.py' is in the same directory or accessible in PYTHONPATH.
try:
    from models import AtoB
except ImportError:
    print("Error: Could not import 'AtoB' from 'models.py'. Make sure 'models.py' is accessible.")
    print("If 'models.py' is in a different location, you might need to adjust PYTHONPATH or the import statement.")
    exit(1)

def get_image_paths(directory: str, exclude_subdir: str = None) -> list[str]:
    """Gets all valid image file paths from a directory, optionally excluding a subdirectory."""
    allowed_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')
    image_paths = []
    abs_exclude_path = os.path.abspath(os.path.join(directory, exclude_subdir)) if exclude_subdir else None

    for root, dirs, files in os.walk(directory):
        # If an exclude_subdir is specified, skip it
        if abs_exclude_path and os.path.abspath(root).startswith(abs_exclude_path):
            continue
        
        for file in files:
            if file.lower().endswith(allowed_extensions):
                image_paths.append(os.path.join(root, file))
    return image_paths

def pad_image_to_patch_size(image: Image.Image, patch_size: int) -> tuple[Image.Image, tuple[int, int]]:
    """Pads an image so its dimensions are divisible by patch_size."""
    original_width, original_height = image.size
    
    pad_width = math.ceil(original_width / patch_size) * patch_size
    pad_height = math.ceil(original_height / patch_size) * patch_size

    if image.mode == 'RGBA':
        padding_color = (0, 0, 0, 0) 
    elif image.mode == 'L':
        padding_color = 0 
    else: 
        padding_color = (0, 0, 0) 

    padded_image = Image.new(image.mode, (pad_width, pad_height), padding_color)
    padded_image.paste(image, (0, 0))
    return padded_image, (original_width, original_height)

def unpad_image(image: Image.Image, original_width: int, original_height: int) -> Image.Image:
    """Crops a padded image back to its original dimensions."""
    return image.crop((0, 0, original_width, original_height))

def create_patches_from_image(padded_image: Image.Image, patch_size: int) -> list[dict]:
    """Creates a list of patches from a padded image."""
    patches_info = []
    width, height = padded_image.size
    for y_coord in range(0, height, patch_size):
        for x_coord in range(0, width, patch_size):
            patch = padded_image.crop((x_coord, y_coord, x_coord + patch_size, y_coord + patch_size))
            patches_info.append({'image_pil': patch, 'coords': (x_coord, y_coord)})
    return patches_info

def stitch_patches_to_image(processed_patches_info: list, target_width: int, target_height: int) -> Image.Image:
    """Stitches processed PIL image patches back into a full image."""
    if not processed_patches_info:
        raise ValueError("No processed patches to stitch.")

    output_mode = processed_patches_info[0]['image_pil'].mode
    
    final_image = Image.new(output_mode, (target_width, target_height))
    for patch_info in processed_patches_info:
        patch_pil = patch_info['image_pil']
        coords = patch_info['coords']
        final_image.paste(patch_pil, coords)
    return final_image

def tensor_to_pil(tensor_image: torch.Tensor, mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5)) -> Image.Image:
    """Converts a tensor image to a PIL Image, denormalizing it."""
    tensor_image = tensor_image.cpu().clone().detach()
    if tensor_image.ndim == 4: # NCHW (batch size 1)
        tensor_image = tensor_image.squeeze(0) # Remove batch dim
    
    if tensor_image.ndim == 3: # CHW
        for c in range(tensor_image.size(0)):
            tensor_image[c] = tensor_image[c] * std[c] + mean[c]
    else:
        raise ValueError(f"Unsupported tensor ndim after squeeze: {tensor_image.ndim}")

    tensor_image = torch.clamp(tensor_image, 0, 1)
    pil_image = transforms.ToPILImage()(tensor_image)
    return pil_image

def main():
    parser = argparse.ArgumentParser(description='Inference script for document image cleaning using CycleGAN.')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing input document images.')
    parser.add_argument('--output_subdir_name', type=str, default='cleaned_output', help='Name of the subdirectory within input_dir to save cleaned images.')
    parser.add_argument('--model_path', type=str, default='Output/S-color0.5/model/netG_A2B.pth', help='Path to the pre-trained generator model (netG_A2B).')
    parser.add_argument('--patch_size', type=int, default=256, help='Size of the image patches (e.g., 256 for 256x256).')
    parser.add_argument('--input_nc', type=int, default=3, help='Number of channels of input data for the model.')
    parser.add_argument('--output_nc', type=int, default=3, help='Number of channels of output data for the model.')
    parser.add_argument('--cuda', action='store_true', help='Use GPU computation if available.')
    
    args = parser.parse_args()

    if args.patch_size <= 0:
        print("Error: --patch_size must be a positive integer.")
        return

    if args.cuda and torch.cuda.is_available():
        device = torch.device('cuda')
        print("CUDA selected and available. Using GPU.")
    else:
        device = torch.device('cpu')
        if args.cuda:
            print("CUDA selected but not available. Using CPU.")
        else:
            print("Using CPU.")

    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found at {args.model_path}")
        return

    try:
        model = AtoB(args.input_nc, args.output_nc).to(device)
        model.load_state_dict(torch.load(args.model_path, map_location=device))
        model.eval() 
        print(f"Model loaded successfully from {args.model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")
        return

    transform_patch = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=(0.5, 0.5, 0.5), std=(0.5, 0.5, 0.5))
    ])

    output_dir_path = os.path.join(args.input_dir, args.output_subdir_name)
    os.makedirs(output_dir_path, exist_ok=True)
    print(f"Cleaned images will be saved in: {output_dir_path}")

    image_files = get_image_paths(args.input_dir, exclude_subdir=args.output_subdir_name)
    if not image_files:
        print(f"No images found in {args.input_dir} (excluding ./{args.output_subdir_name}/).")
        return
    
    print(f"Found {len(image_files)} images to process.")

    for img_path in image_files:
        print(f"Processing: {img_path} ...")
        try:
            original_pil_image = Image.open(img_path).convert('RGB')
            
            padded_pil_image, (orig_w, orig_h) = pad_image_to_patch_size(original_pil_image, args.patch_size)
            
            patches_info_list = create_patches_from_image(padded_pil_image, args.patch_size)
            
            processed_patches_for_stitching = []

            with torch.no_grad():
                for patch_info in patches_info_list:
                    pil_patch = patch_info['image_pil']
                    patch_tensor = transform_patch(pil_patch).unsqueeze(0).to(device)
                    cleaned_patch_tensor = model(patch_tensor)
                    cleaned_pil_patch = tensor_to_pil(cleaned_patch_tensor)
                    processed_patches_for_stitching.append({
                        'image_pil': cleaned_pil_patch,
                        'coords': patch_info['coords']
                    })
            
            stitched_padded_image = stitch_patches_to_image(
                processed_patches_for_stitching,
                padded_pil_image.width,
                padded_pil_image.height
            )
            
            final_cleaned_image = unpad_image(stitched_padded_image, orig_w, orig_h)
            
            base, ext = os.path.splitext(os.path.basename(img_path))
            output_filename = f"{base}_cleaned.png"
            output_save_path = os.path.join(output_dir_path, output_filename)
            final_cleaned_image.save(output_save_path)
            print(f"Saved cleaned image to: {output_save_path}")

        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            import traceback
            traceback.print_exc()

    print("Inference complete.")

if __name__ == '__main__':
    main()
