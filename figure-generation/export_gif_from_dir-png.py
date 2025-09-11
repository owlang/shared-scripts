#!/usr/bin/env python3
"""
Convert a directory of PNG files into an animated GIF.
Requires: pip install Pillow
"""

import os, sys, argparse
from PIL import Image
import glob

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

def main():
    parser = argparse.ArgumentParser(description="Convert PNG files in a directory to animated GIF")
    parser.add_argument("input_dir", required=True, help="Directory containing PNG files")
    parser.add_argument("-o", "--output", default="animation.gif", help="Output GIF filename")
    parser.add_argument("-d", "--duration", type=int, default=500, help="Frame duration in milliseconds")
    parser.add_argument("-l", "--loop", type=int, default=0, help="Number of loops (0 = infinite)")
    
    args = parser.parse_args()
    
    # Check if input directory exists
    if not os.path.isdir(args.input_dir):
        print(f"Error: Directory '{args.input_dir}' does not exist")
        sys.exit(1)
    
    # Convert PNG files to GIF
    success = convert_png_directory_to_gif(
        args.input_dir, 
        args.output, 
        args.duration, 
        args.loop
    )
    
    if success:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()