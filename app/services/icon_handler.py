import base64
import uuid
import re
from pathlib import Path


class IconHandler:
    """Handles icon processing and storage for categories and subcategories"""
    
    def __init__(self):
        self.icons_base_path = Path("static/images/icons/")
        self.custom_icons_path = self.icons_base_path / "brand"
        self.custom_icons_path.mkdir(parents=True, exist_ok=True)
    
    def process_icon(self, icon_type: str, icon_value: str) -> str:
        """
        Process icon based on type and return the standardized icon_name format
        
        Args:
            icon_type: 'feather', 'emoji', or 'upload'
            icon_value: The icon identifier or base64/raw SVG data
            
        Returns:
            Standardized icon_name (e.g., 'fthr:coffee', 'emoji:🍕', 'img:brand/abc123.svg')
        """
        if icon_type == "feather":
            return f"fthr:{icon_value}"
        
        elif icon_type == "emoji":
            return f"emoji:{icon_value}"
        
        elif icon_type == "upload":
            filename = self._save_svg_file(icon_value)
            return f"img:brand/{filename}"
        
        else:
            raise ValueError(f"Unsupported icon type: {icon_type}")
    
    def _save_svg_file(self, svg_data: str) -> str:
        """
        Save SVG data to file and return filename
        
        Args:
            svg_data: Base64 encoded SVG or raw SVG string
            
        Returns:
            Generated filename
        """
        unique_id = str(uuid.uuid4())[:5]
        filename = f"custom_{unique_id}.svg"
        file_path = self.custom_icons_path / filename
        
        try:
            if svg_data.startswith('data:image/svg+xml;base64,'):
                base64_data = svg_data.split(',', 1)[1]
                svg_content = base64.b64decode(base64_data).decode('utf-8')
            else:
                svg_content = svg_data
            
            if not svg_content.strip().startswith('<svg'):
                raise ValueError("Invalid SVG content")
            
            svg_content = self._sanitize_svg(svg_content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            return filename
            
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise ValueError(f"Failed to process SVG file: {str(e)}")
    
    def _sanitize_svg(self, svg_content: str) -> str:
        """
        Basic SVG sanitization to remove potentially dangerous elements
        
        Args:
            svg_content: Raw SVG content
            
        Returns:
            Sanitized SVG content
        """
        svg_content = re.sub(r'<script[^>]*>.*?</script>', '', svg_content, flags=re.IGNORECASE | re.DOTALL)
        svg_content = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', svg_content, flags=re.IGNORECASE)
        
        svg_content = svg_content.strip()
        if not svg_content.startswith('<?xml'):
            if not svg_content.startswith('<svg'):
                raise ValueError("Invalid SVG structure")
        
        return svg_content
    
    def delete_custom_icon(self, icon_name: str) -> bool:
        """
        Delete a custom icon file
        
        Args:
            icon_name: Icon name in format 'img:brand/filename.svg'
            
        Returns:
            True if successfully deleted, False otherwise
        """
        if not icon_name.startswith('img:brand/'):
            return False
        
        filename = icon_name.replace('img:brand/', '')
        file_path = self.custom_icons_path / filename
        
        try:
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"Error deleting icon file {filename}: {e}")
        
        return False