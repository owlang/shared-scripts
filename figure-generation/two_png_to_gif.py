import os, argparse
import time
import shutil
from PIL import Image
import glob

def fade_images(image1_path, image2_path, output_dir, steps=10):
    """
    Fades between two images of the same size and saves the results.
    
    Parameters:
        image1_path (str): Path to the first image.
        image2_path (str): Path to the second image.
        output_dir (str): Directory to save the output images.
        steps (int): Number of intermediate frames.
    """
    # Load the images
    img1 = Image.open(image1_path).convert("RGBA")
    img2 = Image.open(image2_path).convert("RGBA")

    # Ensure the images have the same size
    if img1.size != img2.size:
        raise ValueError("Images must be of the same size.")
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate the fade effect
    for i in range(steps + 1):
        alpha = i / steps  # Calculate blend factor
        blended = Image.blend(img1, img2, alpha=alpha)
        blended.save(os.path.join(output_dir, f"frame_{i:03d}.png"))

    print(f"Fading frames saved to {output_dir}")


def convert_png_directory_to_gif(input_dir, output_file="animation.gif", duration=500, loop=0):
    """
    Convert all PNG files in a directory to an animated GIF.
    
    Args:
        input_dir (str): Directory containing PNG files
        output_file (str): Output GIF filename
        duration (int): Duration between frames in milliseconds
        loop (int): Number of loops (0 = infinite)
    """
    
    # Get all PNG files in the directory
    png_pattern = os.path.join(input_dir, "*.png")
    png_files = glob.glob(png_pattern)
    
    if not png_files:
        print(f"No PNG files found in directory: {input_dir}")
        return False
    
    # Sort files naturally (handles numbered sequences properly)
    png_files.sort()
    
    print(f"Found {len(png_files)} PNG files")
    
    # Load all images
    images = []
    for i, png_file in enumerate(png_files):
        try:
            img = Image.open(png_file)
            # Convert to RGB if necessary (GIF doesn't support RGBA)
            if img.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            images.append(img)
            print(f"Loaded: {os.path.basename(png_file)}")
            
        except Exception as e:
            print(f"Error loading {png_file}: {e}")
            continue
    
    if not images:
        print("No valid images could be loaded")
        return False
    
    # Save as animated GIF
    try:
        print(f"Creating animated GIF: {output_file}")
        images[0].save(
            output_file,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=loop,
            optimize=True
        )
        print(f"Successfully created: {output_file}")
        return True
        
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return False

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Fade between two PNG images of the same size.")
    parser.add_argument("-a", "--a-image", required=True, help="Path to the first PNG image.")
    parser.add_argument("-b", "--b-image", required=True, help="Path to the second PNG image.")
    parser.add_argument("-o", "--output", required=True, help="Output directory to save fading frames.")
    parser.add_argument("-s", "--steps", type=int, default=10, help="Number of fade steps (default: 10).")
    parser.add_argument("-d", "--duration", type=int, default=10, help="Transition timing of .gif file.")
    parser.add_argument("-l", "--loop", type=int, default=0, help="Number of times looping through images. (default inf loop)")

    args = parser.parse_args()

    temp_odir='temp-%s' % time.time()

    # Perform the fade effect
    fade_images(args.a_image, args.b_image, temp_odir, steps=args.steps)

    # Aggregate to .gif
    convert_png_directory_to_gif(temp_odir, output_file=args.output, duration=args.duration, loop=args.loop)

    # Clean-up
    shutil.rmtree(temp_odir)
