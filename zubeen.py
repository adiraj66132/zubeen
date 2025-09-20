from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import time
import os
import sys
import random
import math

# Optimized ASCII characters for clean, recognizable output
ASCII_CHARS_CLEAN = [
    "@", "#", "%", "*", "+", "=", "-", ":", ".", " "
]

# Alternative set with good contrast
ASCII_CHARS_BALANCED = [
    "@", "%", "#", "*", "+", "=", "-", ":", ",", ".", " "
]

def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def preprocess_image_optimized(image):
    """Optimized image preprocessing for clean ASCII conversion"""
    # Convert to grayscale first
    if image.mode != 'L':
        image = image.convert('L')
    
    # Moderate contrast enhancement for clarity
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.4)
    
    # Slight brightness adjustment
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.05)
    
    # Apply histogram equalization for better distribution
    image = ImageOps.equalize(image, mask=None)
    
    # Light sharpening for definition without noise
    image = image.filter(ImageFilter.SHARPEN)
    
    return image

def calculate_optimal_size(image, max_width=120, max_height=60):
    """Calculate optimal ASCII size for clean output"""
    width, height = image.size
    
    # Calculate aspect ratio
    aspect_ratio = height / width
    
    # Terminal character aspect ratio (optimized for readability)
    terminal_ratio = 0.45
    
    # Calculate dimensions favoring readability
    if width > height:
        new_width = min(max_width, 120)
        new_height = int(new_width * aspect_ratio * terminal_ratio)
    else:
        new_height = min(max_height, 60)
        new_width = int(new_height / (aspect_ratio * terminal_ratio))
    
    return new_width, new_height

def resize_image_optimized(image, target_width=None, target_height=None):
    """Optimized image resizing for clean ASCII output"""
    if target_width is None and target_height is None:
        target_width, target_height = calculate_optimal_size(image)
    elif target_width is None:
        width, height = image.size
        target_width = int(target_height * width / height / 0.45)
    elif target_height is None:
        width, height = image.size
        target_height = int(target_width * height / width * 0.45)
    
    # Use LANCZOS for high-quality resampling
    resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    return resized

def adaptive_threshold(image, block_size=11):
    """Apply adaptive thresholding for better contrast"""
    pixels = list(image.getdata())
    width, height = image.size
    
    # Convert to 2D array
    pixel_matrix = []
    for y in range(height):
        row = []
        for x in range(width):
            row.append(pixels[y * width + x])
        pixel_matrix.append(row)
    
    # Apply adaptive threshold
    half_block = block_size // 2
    threshold_pixels = []
    
    for y in range(height):
        for x in range(width):
            # Calculate local average
            local_sum = 0
            count = 0
            
            for dy in range(-half_block, half_block + 1):
                for dx in range(-half_block, half_block + 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < height and 0 <= nx < width:
                        local_sum += pixel_matrix[ny][nx]
                        count += 1
            
            local_avg = local_sum / count
            current_pixel = pixel_matrix[y][x]
            
            # Enhanced threshold calculation
            if current_pixel > local_avg * 1.05:
                threshold_pixels.append(min(255, int(current_pixel * 1.2)))
            else:
                threshold_pixels.append(max(0, int(current_pixel * 0.8)))
    
    # Create new image with threshold pixels
    new_image = Image.new('L', (width, height))
    new_image.putdata(threshold_pixels)
    
    return new_image

def pixels_to_ascii_clean(image, ascii_chars, method='balanced'):
    """Clean pixel to ASCII conversion optimized for recognition"""
    pixels = list(image.getdata())
    
    if method == 'balanced':
        # Balanced method for clean, recognizable output
        ascii_str = ""
        for pixel_value in pixels:
            # Normalize pixel value
            normalized = pixel_value / 255.0
            
            # Apply gentle gamma correction
            gamma_corrected = normalized ** 0.85
            
            # Map to ASCII character
            ascii_index = min(int(gamma_corrected * len(ascii_chars)), len(ascii_chars) - 1)
            ascii_str += ascii_chars[ascii_index]
    
    elif method == 'simple':
        # Simple method for fast, clean conversion
        ascii_str = ""
        for pixel_value in pixels:
            ascii_index = min(pixel_value * len(ascii_chars) // 256, len(ascii_chars) - 1)
            ascii_str += ascii_chars[ascii_index]
    
    return ascii_str

def image_to_ascii_clean(image_path, width=120, method='balanced'):
    """Clean ASCII conversion optimized for recognition"""
    try:
        # Load image
        image = Image.open(image_path)
        print(f"Loaded image: {image.size} ({image.mode})")
        
        # Choose ASCII character set based on method
        if method == 'simple':
            ascii_chars = ASCII_CHARS_CLEAN
        else:
            ascii_chars = ASCII_CHARS_BALANCED
        
        # Optimized preprocessing
        print("Processing image for optimal clarity...")
        processed_image = preprocess_image_optimized(image)
        
        # Resize with optimal dimensions
        print("Resizing for perfect recognition...")
        resized_image = resize_image_optimized(processed_image, target_width=width)
        print(f"Resized to: {resized_image.size}")
        
        # Convert to ASCII with clean method
        print("Converting to clean ASCII...")
        ascii_str = pixels_to_ascii_clean(resized_image, ascii_chars, method)
        
        # Format into lines
        img_width = resized_image.width
        ascii_lines = []
        for i in range(0, len(ascii_str), img_width):
            line = ascii_str[i:(i + img_width)]
            ascii_lines.append(line)
        
        return ascii_lines, resized_image.size
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None, None

def create_multiple_quality_versions(image_path):
    """Create multiple versions with optimized quality settings"""
    versions = [
        {"name": "Balanced_Quality", "width": 120, "method": "balanced"},
        {"name": "Fast_Preview", "width": 80, "method": "simple"},
    ]
    
    results = {}
    
    for version in versions:
        print(f"\n🎨 Creating {version['name'].replace('_', ' ')}...")
        ascii_art, size = image_to_ascii_clean(
            image_path, 
            width=version['width'],
            method=version['method']
        )
        
        if ascii_art:
            results[version['name']] = {
                'art': ascii_art,
                'size': size,
                'settings': version
            }
            
            # Save to file
            filename = f"ascii_{version['name'].lower()}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ascii_art))
            print(f"✅ Saved as {filename}")
    
    return results

def animate_clean_ascii_singer(image_path, width=120, duration=20):
    """Animate clean ASCII art with smooth performance"""
    try:
        print("🎤 Creating clean animated ASCII singer...")
        
        # Generate base ASCII art with clean method
        ascii_art, size = image_to_ascii_clean(image_path, width, method='balanced')
        
        if not ascii_art:
            print("❌ Failed to generate ASCII art")
            return
        
        print(f"✅ Generated clean ASCII art: {size}")
        print("🎵 Starting smooth performance...")
        time.sleep(2)
        
        frame_count = 0
        start_time = time.time()
        
        while time.time() - start_time < duration:
            clear_screen()
            
            # Create performance frame
            performance_frame = []
            
            # Add animated header
            header = "🎤" + "═" * (len(ascii_art[0]) - 4) + "🎤"
            performance_frame.append(header)
            
            # Add stage lights effect
            if frame_count % 4 == 0:
                lights = "✨" + " " * (len(ascii_art[0]) - 4) + "✨"
            elif frame_count % 4 == 1:
                lights = " ⭐" + " " * (len(ascii_art[0]) - 6) + "⭐ "
            elif frame_count % 4 == 2:
                lights = "  ✦" + " " * (len(ascii_art[0]) - 8) + "✦  "
            else:
                lights = "   ✧" + " " * (len(ascii_art[0]) - 10) + "✧   "
            performance_frame.append(lights)
            
            # Add the main clean ASCII art
            performance_frame.extend(ascii_art)
            
            # Add stage floor with smooth beat visualization
            beat_intensity = int(3 + 2 * abs(math.sin(frame_count * 0.3)))
            stage_floor = "═" * beat_intensity + " ♪ LIVE ♪ " + "═" * beat_intensity
            if len(stage_floor) > len(ascii_art[0]):
                stage_floor = stage_floor[:len(ascii_art[0])]
            else:
                padding = (len(ascii_art[0]) - len(stage_floor)) // 2
                stage_floor = " " * padding + stage_floor + " " * padding
            performance_frame.append(stage_floor)
            
            # Add clean music visualization
            notes_line = ""
            music_notes = ["♪", "♫", "♬", "🎵"]
            for i in range(len(ascii_art[0]) // 6):
                if (i + frame_count) % 4 == 0:
                    notes_line += music_notes[frame_count % len(music_notes)] + "     "
                else:
                    notes_line += "      "
            performance_frame.append(notes_line[:len(ascii_art[0])])
            
            # Display frame
            for line in performance_frame:
                print(line)
            
            # Show performance stats
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            print(f"\n⏱️  Performance: {elapsed}s | Remaining: {remaining}s | Frame: {frame_count}")
            
            time.sleep(1.0 / 10)  # 10 FPS for smooth animation
            frame_count += 1
            
    except KeyboardInterrupt:
        clear_screen()
        print("🎵 Performance ended! Clean ASCII art rocks! 🎵")
    except Exception as e:
        print(f"❌ Error: {e}")

def interactive_quality_menu(image_path):
    """Interactive menu for different quality options"""
    while True:
        clear_screen()
        print("🎨 Optimized ASCII Art Generator 🎨")
        print("=" * 50)
        print("1. Generate All Quality Versions")
        print("2. Balanced Quality (120 chars wide)")
        print("3. Fast Preview (80 chars wide)")
        print("4. Animated Performance (120 chars)")
        print("5. Custom Settings")
        print("6. Compare Side by Side")
        print("q. Quit")
        
        choice = input("\nChoose option: ").lower().strip()
        
        if choice == 'q':
            break
        elif choice == '1':
            create_multiple_quality_versions(image_path)
            input("\n✅ All versions created! Press Enter to continue...")
        elif choice == '2':
            ascii_art, size = image_to_ascii_clean(image_path, 120, 'balanced')
            if ascii_art:
                clear_screen()
                for line in ascii_art:
                    print(line)
                input("\nPress Enter to continue...")
        elif choice == '3':
            ascii_art, size = image_to_ascii_clean(image_path, 80, 'simple')
            if ascii_art:
                clear_screen()
                for line in ascii_art:
                    print(line)
                input("\nPress Enter to continue...")
        elif choice == '4':
            animate_clean_ascii_singer(image_path, 120, 20)
            input("\nPress Enter to continue...")
        elif choice == '5':
            # Custom settings
            try:
                width = int(input("Enter width (50-150): "))
                width = max(50, min(150, width))  # Limit range for clean output
                method = input("Method (balanced/simple) [balanced]: ").strip()
                if not method:
                    method = 'balanced'
                
                ascii_art, size = image_to_ascii_clean(image_path, width, method)
                if ascii_art:
                    clear_screen()
                    for line in ascii_art:
                        print(line)
                    
                    save = input("\nSave this version? (y/n): ").lower()
                    if save == 'y':
                        filename = input("Enter filename (without .txt): ") + ".txt"
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(ascii_art))
                        print(f"✅ Saved as {filename}")
                    
                    input("Press Enter to continue...")
            except ValueError:
                input("Invalid input! Press Enter to continue...")
        elif choice == '7':
            print("Generating comparison versions...")
            versions = create_multiple_quality_versions(image_path)
            print(f"✅ Created {len(versions)} versions for comparison")
            input("Press Enter to continue...")

if __name__ == "__main__":
    image_path = "/home/adiraj/Code/zubeen/zubeen.jpg"
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print("🎨 Optimized ASCII Art Generator 🎨")
    print("This version creates clean, recognizable ASCII art!")
    
    interactive_quality_menu(image_path)
