import aiofiles
import requests
from bs4 import BeautifulSoup
from typing import Optional
import os


class FileHandler:
    """
    Utility class for handling file uploads and URL fetching
    """
    
    @staticmethod
    async def read_uploaded_file(file_path: str) -> str:
        """
        Read content from an uploaded file
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            File content as string
        """
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        return content
    
    @staticmethod
    def fetch_url_content(url: str) -> str:
        """
        Fetch and extract text content from a URL
        
        Args:
            url: URL to fetch
            
        Returns:
            Extracted text content
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
            
        except Exception as e:
            raise Exception(f"Failed to fetch URL content: {str(e)}")
    
    @staticmethod
    async def save_uploaded_file(file_data: bytes, filename: str) -> str:
        """
        Save uploaded file to disk
        
        Args:
            file_data: File bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        file_path = os.path.join(uploads_dir, filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)
        
        return file_path