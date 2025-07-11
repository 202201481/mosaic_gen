from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import Color, black, white
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.renderPDF import drawToFile
from reportlab.platypus.flowables import Flowable
from PIL import Image as PILImage
import io
import math

class ColorRect(Flowable):
    """A simple colored rectangle flowable"""
    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.color = color
    
    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.rect(0, 0, self.width, self.height, fill=1)

class FixedPDFGenerator:
    def __init__(self):
        self.color_names = {
            '#FFFFFF': 'White',
            '#FFD500': 'Yellow', 
            '#FF5800': 'Orange',
            '#C41E3A': 'Red',
            '#009E60': 'Green',
            '#0051BA': 'Blue'
        }
        
        self.color_objects = {
            '#FFFFFF': colors.white,
            '#FFD500': colors.yellow,
            '#FF5800': colors.orange,
            '#C41E3A': colors.red,
            '#009E60': colors.green,
            '#0051BA': colors.blue
        }

    def hex_to_color(self, hex_color):
        """Convert hex color to ReportLab Color object"""
        if hex_color in self.color_objects:
            return self.color_objects[hex_color]
        
        # Parse hex color manually
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0  
            b = int(hex_color[4:6], 16) / 255.0
            return Color(r, g, b)
        return colors.white

    def create_mosaic_flowable(self, mosaic_data, max_width=6*inch):
        """Create a flowable mosaic using colored rectangles"""
        print("Creating mosaic flowable...")
        
        # Get the expanded grid
        grid = mosaic_data.get('grid', [])
        if not grid:
            return Paragraph("No mosaic data available", getSampleStyleSheet()['Normal'])
        
        grid_height = len(grid)
        grid_width = len(grid[0]) if grid else 0
        
        print(f"Grid dimensions: {grid_width}x{grid_height}")
        
        # Calculate cell size to fit within max_width
        cell_size = min(max_width / grid_width, 8)  # Max 8 points per cell
        
        # Create a table with colored cells
        table_data = []
        for row in grid:
            table_row = []
            for cell_color in row:
                # Create a small colored paragraph
                table_row.append('')
            table_data.append(table_row)
        
        # Create table
        table = Table(table_data, colWidths=[cell_size]*grid_width, rowHeights=[cell_size]*grid_height)
        
        # Apply colors to cells
        table_style = [('GRID', (0, 0), (-1, -1), 0.5, colors.black)]
        
        for row_idx, row in enumerate(grid):
            for col_idx, cell_color in enumerate(row):
                color_obj = self.hex_to_color(cell_color)
                table_style.append(('BACKGROUND', (col_idx, row_idx), (col_idx, row_idx), color_obj))
        
        table.setStyle(TableStyle(table_style))
        
        print("Mosaic flowable created successfully")
        return table

    def generate_pdf(self, mosaic_data, settings):
        """Generate PDF with mosaic image and cube instructions"""
        try:
            print("=== Starting FIXED PDF Generation ===")
            print(f"Settings: {settings}")
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center
            )
            
            story = []
            
            # Title page
            story.append(Paragraph("Your Rubik's Cube Mosaic", title_style))
            story.append(Spacer(1, 20))
            
            # Add mosaic visualization
            print("Adding mosaic visualization...")
            mosaic_flowable = self.create_mosaic_flowable(mosaic_data)
            story.append(mosaic_flowable)
            story.append(Spacer(1, 20))
            
            # Add dimensions info
            dimensions = mosaic_data.get('dimensions', {})
            info_text = f"""
            <b>Mosaic Specifications:</b><br/>
            • Cube Grid: {settings.get('width', 16)}×{settings.get('height', 16)} cubes<br/>
            • Total Cubes: {dimensions.get('total', settings.get('width', 16) * settings.get('height', 16))}<br/>
            • Total Faces: {dimensions.get('total_faces', 'N/A')}<br/>
            • Display Resolution: {dimensions.get('display_width', 'N/A')}×{dimensions.get('display_height', 'N/A')} pixels
            """
            story.append(Paragraph(info_text, styles['Normal']))
            story.append(PageBreak())
            
            # Add cube instructions
            print("Adding cube instructions...")
            self.add_cube_instructions(story, mosaic_data, settings, styles)
            
            print("Building final PDF...")
            doc.build(story)
            
            print("✅ PDF generated successfully!")
            buffer.seek(0)
            return buffer
            
        except Exception as e:
            print(f"=== PDF Generation Error ===")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            raise e

    def add_cube_instructions(self, story, mosaic_data, settings, styles):
        """Add detailed cube instructions to PDF"""
        detailed_grid = mosaic_data.get('detailed_grid', [])
        if not detailed_grid:
            story.append(Paragraph("No detailed cube data available", styles['Normal']))
            return
        
        story.append(Paragraph("Detailed Cube Instructions", styles['Heading1']))
        story.append(Spacer(1, 12))
        
        cube_count = 0
        cubes_per_page = 12  # 4x3 layout
        
        for row_idx, cube_row in enumerate(detailed_grid):
            for col_idx, cube_data in enumerate(cube_row):
                cube_count += 1
                
                # Add page break every 12 cubes
                if cube_count > 1 and (cube_count - 1) % cubes_per_page == 0:
                    story.append(PageBreak())
                
                # Cube header
                cube_title = f"Cube {cube_count} (Row {row_idx + 1}, Col {col_idx + 1})"
                story.append(Paragraph(cube_title, styles['Heading3']))
                
                # Create 3x3 face table
                faces = cube_data.get('faces', [])
                if faces and len(faces) == 3:
                    face_data = []
                    for face_row in faces:
                        if len(face_row) == 3:
                            face_data.append([self.color_names.get(face['color'], face['name']) for face in face_row])
                        else:
                            face_data.append(['White', 'White', 'White'])
                    
                    # Create face table
                    face_table = Table(face_data, colWidths=[0.8*inch]*3, rowHeights=[0.3*inch]*3)
                    face_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10)
                    ]))
                    
                    # Add colors to table
                    for row_idx_face, face_row in enumerate(faces):
                        for col_idx_face, face in enumerate(face_row):
                            color_obj = self.hex_to_color(face['color'])
                            face_table.setStyle(TableStyle([
                                ('BACKGROUND', (col_idx_face, row_idx_face), (col_idx_face, row_idx_face), color_obj)
                            ]))
                    
                    story.append(face_table)
                
                story.append(Spacer(1, 12))
        
        print(f"Added instructions for {cube_count} cubes")
