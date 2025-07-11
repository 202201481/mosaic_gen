import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from sklearn.cluster import KMeans
import colorsys

class OptimizedMosaicGenerator:
    def __init__(self):
        # Rubik's cube colors (standard colors)
        self.rubik_colors = {
            'white': (255, 255, 255),
            'yellow': (255, 213, 0),
            'orange': (255, 88, 0),
            'red': (196, 30, 58),
            'green': (0, 158, 96),
            'blue': (0, 81, 186)
        }
        
        # Convert to numpy array for faster computation
        self.color_array = np.array(list(self.rubik_colors.values()))
        
        # Precompute LAB colors for faster matching
        self.lab_colors = {}
        for name, rgb in self.rubik_colors.items():
            self.lab_colors[name] = self.rgb_to_lab_fast(np.array(rgb))
    
    def enhance_image_lightweight(self, image):
        """Lightweight but effective image enhancement"""
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Quick contrast and color enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(1.3)
        
        # Light sharpening
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=110, threshold=1))
        
        return image
    
    def rgb_to_lab_fast(self, rgb):
        """Fast RGB to LAB conversion with error handling"""
        try:
            # Normalize RGB
            rgb_norm = np.clip(rgb / 255.0, 0, 1)
            
            # Gamma correction with safety checks
            def gamma_correct(c):
                c = np.clip(c, 0, 1)
                return np.where(c > 0.04045, 
                               np.power((c + 0.055) / 1.055, 2.4), 
                               c / 12.92)
            
            rgb_linear = gamma_correct(rgb_norm)
            
            # Convert to XYZ
            xyz = np.dot(rgb_linear, np.array([
                [0.4124564, 0.3575761, 0.1804375],
                [0.2126729, 0.7151522, 0.0721750],
                [0.0193339, 0.1191920, 0.9503041]
            ]))
            
            # Normalize by illuminant D65
            xyz_norm = xyz / np.array([0.95047, 1.00000, 1.08883])
            xyz_norm = np.clip(xyz_norm, 0, 100)  # Safety clipping
            
            # Convert to LAB with safety checks
            def f(t):
                t = np.clip(t, 0, 100)
                return np.where(t > 0.008856, 
                               np.power(t, 1/3), 
                               (903.3 * t + 16) / 116)
            
            fxyz = f(xyz_norm)
            
            L = np.clip(116 * fxyz[1] - 16, 0, 100)
            a = np.clip(500 * (fxyz[0] - fxyz[1]), -128, 127)
            b = np.clip(200 * (fxyz[1] - fxyz[2]), -128, 127)
            
            return np.array([L, a, b])
        except:
            # Fallback to simple RGB if LAB fails
            return rgb_norm * 100
    
    def find_closest_rubik_color_fast(self, pixel_rgb):
        """Fast color matching with error handling"""
        try:
            # Ensure valid RGB values
            pixel_rgb = np.clip(pixel_rgb, 0, 255).astype(int)
            
            # Convert to LAB for perceptual matching
            pixel_lab = self.rgb_to_lab_fast(pixel_rgb)
            
            min_distance = float('inf')
            closest_color = 'white'
            
            for name, lab_color in self.lab_colors.items():
                # Calculate Euclidean distance in LAB space
                distance = np.sqrt(np.sum((pixel_lab - lab_color) ** 2))
                
                if distance < min_distance:
                    min_distance = distance
                    closest_color = name
            
            return self.rubik_colors[closest_color], closest_color
            
        except Exception as e:
            print(f"Color matching error: {e}, falling back to white")
            return self.rubik_colors['white'], 'white'
    
    def rgb_to_hex(self, rgb):
        """Convert RGB tuple to hex string"""
        r, g, b = [int(np.clip(c, 0, 255)) for c in rgb]
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def generate_mosaic(self, image, width, height):
        """Generate Rubik's cube mosaic with proper 3x3 face resolution
        
        CRITICAL UNDERSTANDING:
        - For a 32x32 cube mosaic, we need 96x96 pixels (32*3 = 96)
        - Each cube has a 3x3 face pattern
        - Each pixel in the resized image becomes one face of a cube
        """
        print(f"🎯 Starting mosaic generation: {width}x{height} cubes")
        
        # Convert to RGB if not already
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # CRITICAL: Calculate the exact pixel resolution needed
        # Each cube needs 3x3 pixels for its face pattern
        target_pixel_width = width * 3
        target_pixel_height = height * 3
        
        print(f"📐 Target resolution: {target_pixel_width}x{target_pixel_height} pixels")
        print(f"📊 Each cube maps to exactly 3x3 pixels")
        
        # Resize image to exact target size
        resized_image = image.resize(
            (target_pixel_width, target_pixel_height), 
            Image.Resampling.LANCZOS
        )
        
        # Apply lightweight enhancement
        enhanced_image = self.enhance_image_lightweight(resized_image)
        image_array = np.array(enhanced_image)
        
        print(f"✅ Image processed to {image_array.shape}")
        
        # Initialize grids
        detailed_grid = []  # For PDF with 3x3 faces per cube
        simple_grid = []    # For website with dominant colors
        color_count = {}
        
        # Process each cube
        for cube_y in range(height):
            detailed_row = []
            simple_row = []
            
            for cube_x in range(width):
                # Extract exactly 3x3 pixel region for this cube
                start_x = cube_x * 3
                start_y = cube_y * 3
                end_x = start_x + 3
                end_y = start_y + 3
                
                # Get the 3x3 pixel block
                cube_region = image_array[start_y:end_y, start_x:end_x]
                
                # Convert each pixel to a cube face
                cube_faces = []
                face_colors = []
                
                for face_y in range(3):
                    face_row = []
                    for face_x in range(3):
                        # Get the exact pixel color
                        pixel_rgb = cube_region[face_y, face_x]
                        
                        # Find closest Rubik's color
                        closest_rgb, closest_name = self.find_closest_rubik_color_fast(pixel_rgb)
                        
                        face_data = {
                            'color': self.rgb_to_hex(closest_rgb),
                            'name': closest_name
                        }
                        face_row.append(face_data)
                        face_colors.append(face_data['color'])
                        
                        # Count colors
                        color_count[face_data['color']] = color_count.get(face_data['color'], 0) + 1
                    
                    cube_faces.append(face_row)
                
                # Store detailed cube data for PDF
                cube_data = {
                    'faces': cube_faces,
                    'position': {'x': cube_x, 'y': cube_y}
                }
                detailed_row.append(cube_data)
                
                # Get dominant color for website display
                dominant_color = max(set(face_colors), key=face_colors.count)
                simple_row.append(dominant_color)
            
            detailed_grid.append(detailed_row)
            simple_grid.append(simple_row)
            
            # Progress indicator
            if (cube_y + 1) % 10 == 0 or cube_y == height - 1:
                print(f"🔄 Processed {cube_y + 1}/{height} rows")
        
        total_faces = width * height * 9
        print(f"✅ Mosaic complete: {len(color_count)} unique colors, {total_faces} total faces")
        
        return {
            'grid': self.create_expanded_display_grid(detailed_grid, width, height),  # 3x expanded for website
            'detailed_grid': detailed_grid,
            'colorCount': color_count,
            'dimensions': {
                'width': width,
                'height': height,
                'display_width': width * 3,  # Actual display width (3x3 per cube)
                'display_height': height * 3,  # Actual display height (3x3 per cube)
                'total': width * height,
                'total_faces': total_faces,
                'pixel_resolution': f"{target_pixel_width}x{target_pixel_height}"
            }
        }
    
    def create_expanded_display_grid(self, detailed_grid, cube_width, cube_height):
        """Create expanded 3x3 grid for website display"""
        # Calculate final dimensions: each cube becomes 3x3 pixels
        final_height = cube_height * 3
        final_width = cube_width * 3
        
        # Create the expanded grid
        expanded_grid = []
        
        for cube_row in range(cube_height):
            # For each cube row, we need to create 3 pixel rows
            for face_row in range(3):
                pixel_row = []
                
                for cube_col in range(cube_width):
                    # Get the cube data
                    cube_data = detailed_grid[cube_row][cube_col]
                    
                    # Add the 3 face colors from this face row
                    for face_col in range(3):
                        face_color = cube_data['faces'][face_row][face_col]['color']
                        pixel_row.append(face_color)
                
                expanded_grid.append(pixel_row)
        
        print(f"✅ Created expanded display grid: {len(expanded_grid)}×{len(expanded_grid[0])} pixels")
        return expanded_grid

# Create a global instance for backwards compatibility
MosaicGenerator = OptimizedMosaicGenerator
