from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class TextElement:
    """Represents a text element with its styling properties."""
    text: str
    font_size: int
    color: str
    stroke_color: str
    stroke_width: int
    hor_offset: int
    vert_offset: int

@dataclass
class PromptRecord:
    """Represents a single prompt record from the Excel file."""
    
    # Basic Information
    prompt_id: int
    category: str
    prompt_title: str
    status: str
    version: str
    publish_date: Optional[datetime]
    
    # Asset Paths
    head_video_path: str
    head_music_path: str
    tail_video_path: str
    tail_music_path: str
    tail_comic_image_path: str
    voiceover_path: str
    
    # Content
    voiceover_script: str
    
    # Text Elements (using TextElement class to avoid repetition)
    text_elements: list[TextElement]
    
    # Links
    google_doc_link: str
    notion_link: str
    gumroad_link: str
    
    # Additional Info
    notes: str
    
    @classmethod
    def from_excel_row(cls, row_data: Dict[str, Any]) -> 'PromptRecord':
        """Create PromptRecord from Excel row data."""
        
        # Parse date
        publish_date = None
        if row_data.get('Publish Date'):
            if isinstance(row_data['Publish Date'], datetime):
                publish_date = row_data['Publish Date']
            else:
                try:
                    publish_date = datetime.strptime(str(row_data['Publish Date']), '%Y-%m-%d')
                except (ValueError, TypeError):
                    publish_date = None
        
        # Create text elements (avoiding repetition with loop)
        text_elements = []
        for i in range(1, 4):  # Text 1, 2, 3
            text = row_data.get(f'Text {i}', '')
            if text:  # Only create if text exists
                text_element = TextElement(
                    text=str(text),
                    font_size=int(row_data.get(f'Font Size {i}', 24)),
                    color=str(row_data.get(f'Color {i}', '#FFFFFF')),
                    stroke_color=str(row_data.get(f'Stroke Color {i}', '#000000')),
                    stroke_width=int(row_data.get(f'Stroke Width {i}', 1)),
                    hor_offset=int(row_data.get(f'Hor Offset {i}', 0)),
                    vert_offset=int(row_data.get(f'Vert Offset {i}', 0))
                )
                text_elements.append(text_element)
        
        return cls(
            prompt_id=int(row_data.get('Prompt ID', 0)),
            category=str(row_data.get('Category', '')),
            prompt_title=str(row_data.get('Prompt Title', '')),
            status=str(row_data.get('Status', '')),
            version=str(row_data.get('Version', '')),
            publish_date=publish_date,
            head_video_path=str(row_data.get('Head Video Path', '')),
            head_music_path=str(row_data.get('Head Music Path', '')),
            tail_video_path=str(row_data.get('Tail Video Path', '')),
            tail_music_path=str(row_data.get('Tail Music Path', '')),
            tail_comic_image_path=str(row_data.get('Tail Comic Image Path', '')),
            voiceover_path=str(row_data.get('Voiceover Path', '')),
            voiceover_script=str(row_data.get('Voiceover Script', '')),
            text_elements=text_elements,
            google_doc_link=str(row_data.get('Google Doc Link', '')),
            notion_link=str(row_data.get('Notion Link', '')),
            gumroad_link=str(row_data.get('Gumroad Link', '')),
            notes=str(row_data.get('Notes', ''))
        )
    
    def get_text_element(self, index: int) -> Optional[TextElement]:
        """Get text element by index (0-based)."""
        if 0 <= index < len(self.text_elements):
            return self.text_elements[index]
        return None
    
    def has_all_assets(self) -> bool:
        """Check if all required asset paths are provided."""
        required_assets = [
            self.head_video_path,
            self.head_music_path,
            self.tail_video_path,
            self.tail_music_path,
            self.voiceover_path
        ]
        return all(asset.strip() for asset in required_assets)
    
    def is_ready_for_production(self) -> bool:
        """Check if prompt is ready for video production."""
        return (
            self.status.lower() == 'done' and
            self.has_all_assets() and
            len(self.text_elements) > 0 and
            self.voiceover_script.strip()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy serialization."""
        result = {
            'prompt_id': self.prompt_id,
            'category': self.category,
            'prompt_title': self.prompt_title,
            'status': self.status,
            'version': self.version,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'head_video_path': self.head_video_path,
            'head_music_path': self.head_music_path,
            'tail_video_path': self.tail_video_path,
            'tail_music_path': self.tail_music_path,
            'tail_comic_image_path': self.tail_comic_image_path,
            'voiceover_path': self.voiceover_path,
            'voiceover_script': self.voiceover_script,
            'google_doc_link': self.google_doc_link,
            'notion_link': self.notion_link,
            'gumroad_link': self.gumroad_link,
            'notes': self.notes
        }
        
        # Add text elements
        for i, text_elem in enumerate(self.text_elements, 1):
            result[f'text_{i}'] = text_elem.text
            result[f'font_size_{i}'] = text_elem.font_size
            result[f'color_{i}'] = text_elem.color
            result[f'stroke_color_{i}'] = text_elem.stroke_color
            result[f'stroke_width_{i}'] = text_elem.stroke_width
            result[f'hor_offset_{i}'] = text_elem.hor_offset
            result[f'vert_offset_{i}'] = text_elem.vert_offset
        
        return result

# Example usage
if __name__ == "__main__":
    # Sample data matching your example
    sample_data = {
        'Prompt ID': 1,
        'Category': 'Travel',
        'Prompt Title': 'Find Cheap Flights',
        'Status': 'Done',
        'Version': '1.0',
        'Publish Date': '2025-08-06',
        'Head Video Path': '/Assets/Intro/travel_intro_sample.mp4',
        'Head Music Path': '/Assets/Music/music_placeholder.mp3',
        'Tail Video Path': '/Assets/Tail/travel_tail_sample.mp4',
        'Tail Music Path': '/Assets/Music/music_placeholder.mp3',
        'Tail Comic Image Path': '/Categories/Travel/Tail/comic_outro_image.png',
        'Voiceover Path': '/Assets/Voiceovers_Lena/sample_voiceover.mp3',
        'Voiceover Script': 'This prompt helps users find the best flight deals using ChatGPT.',
        'Text 1': 'Find Cheap Flights',
        'Font Size 1': 48,
        'Color 1': '#FFFFFF',
        'Stroke Color 1': '#000000',
        'Stroke Width 1': 2,
        'Hor Offset 1': 0,
        'Vert Offset 1': -200,
        'Text 2': 'Built with ChatGPT',
        'Font Size 2': 36,
        'Color 2': '#FFD700',
        'Stroke Color 2': '#000000',
        'Stroke Width 2': 1,
        'Hor Offset 2': 0,
        'Vert Offset 2': -100,
        'Text 3': 'Modify it to match your destination!',
        'Font Size 3': 32,
        'Color 3': '#00BFFF',
        'Stroke Color 3': '#000000',
        'Stroke Width 3': 1,
        'Hor Offset 3': 0,
        'Vert Offset 3': -50,
        'Google Doc Link': 'https://docs.google.com/find-flights',
        'Notion Link': 'https://notion.so/find-flights',
        'Gumroad Link': 'https://gumroad.com/find-flights',
        'Notes': 'This is your first prompt — focus on tone, energy, and clarity.'
    }
    
    # Create record from sample data
    record = PromptRecord.from_excel_row(sample_data)
    print(f"Created record: {record.prompt_title}")
    print(f"Ready for production: {record.is_ready_for_production()}")
    print(f"Number of text elements: {len(record.text_elements)}")