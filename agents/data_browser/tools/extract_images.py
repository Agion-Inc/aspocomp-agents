"""Tool for extracting images from a web page."""

import sys
import os
import asyncio
import requests
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.data_browser.database import DataBrowserDatabase
from agents.data_browser.playwright_engine import PlaywrightEngine
from agents.data_browser.extractor import ContentExtractor
from agents.data_browser.models import ExtractedImage
from agents.data_browser.config import AGENT_CONFIG


def extract_images(
    visit_id: int,
    download_images: bool = True,
    include_base64: bool = False
) -> Dict[str, Any]:
    """Extract images from a page.
    
    This tool extracts images from a previously visited page. It can download
    images to local storage and optionally encode them as base64.
    
    Args:
        visit_id: Page visit ID from navigate_to_page (required)
        download_images: Whether to download images to local storage (default: True)
        include_base64: Whether to include base64-encoded image data in response (default: False)
    
    Returns:
        Dictionary with images array containing URLs, local paths, and metadata
    """
    try:
        db = DataBrowserDatabase()
        
        # Get visit
        visit = db.get_page_visit(visit_id)
        if not visit:
            return {
                "success": False,
                "error": f"Visit ID {visit_id} not found"
            }
        
        # Get page HTML using Playwright
        engine = PlaywrightEngine(AGENT_CONFIG)
        
        async def get_html():
            await engine.start()
            content = await engine.get_page_content(visit.url)
            await engine.close()
            return content
        
        # Handle asyncio in sync context - check if event loop is running
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, get_html())
                page_content = future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            page_content = asyncio.run(get_html())
        
        if page_content.get("error"):
            return {
                "success": False,
                "error": f"Failed to get page content: {page_content.get('error')}"
            }
        
        # Extract images
        extractor = ContentExtractor(AGENT_CONFIG)
        images = extractor.extract_images(page_content.get("html", ""), visit.url)
        
        # Download images if requested
        downloaded_images = []
        images_dir = os.path.join(
            AGENT_CONFIG["storage"]["images_path"],
            str(visit_id)
        )
        
        if download_images:
            os.makedirs(images_dir, exist_ok=True)
        
        for i, img_info in enumerate(images):
            img_url = img_info.get("url", "")
            if not img_url:
                continue
            
            local_path = None
            file_size = None
            
            if download_images:
                try:
                    # Download image
                    response = requests.get(img_url, timeout=10, stream=True)
                    response.raise_for_status()
                    
                    # Determine file extension
                    parsed_url = urlparse(img_url)
                    path = parsed_url.path
                    ext = os.path.splitext(path)[1] or ".jpg"
                    
                    # Save to local storage
                    filename = f"image_{i+1}{ext}"
                    local_path = os.path.join(images_dir, filename)
                    
                    with open(local_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    
                    file_size = os.path.getsize(local_path)
                    
                    # Get image dimensions if possible
                    try:
                        from PIL import Image
                        with Image.open(local_path) as img:
                            img_info["width"], img_info["height"] = img.size
                            img_info["format"] = img.format.lower() if img.format else ext[1:]
                    except Exception:
                        pass
                
                except Exception as e:
                    # Continue even if download fails
                    pass
            
            # Save image record
            extracted_image = ExtractedImage(
                extraction_id=0,  # Will be updated if extraction exists
                image_url=img_url,
                local_path=local_path,
                alt_text=img_info.get("alt_text"),
                width=img_info.get("width"),
                height=img_info.get("height"),
                file_size=file_size,
                format=img_info.get("format")
            )
            
            # Try to find associated extraction
            extractions = db.get_extraction_history(visit.user_id, limit=1)
            if extractions:
                extracted_image.extraction_id = extractions[0].id
            
            image_id = db.save_extracted_image(extracted_image)
            
            img_result = {
                "id": image_id,
                "url": img_url,
                "alt_text": img_info.get("alt_text", ""),
                "local_path": local_path,
                "width": img_info.get("width"),
                "height": img_info.get("height"),
                "file_size": file_size,
                "format": img_info.get("format")
            }
            
            if include_base64 and local_path and os.path.exists(local_path):
                try:
                    import base64
                    with open(local_path, 'rb') as f:
                        img_data = f.read()
                        img_result["base64"] = base64.b64encode(img_data).decode('utf-8')
                except Exception:
                    pass
            
            downloaded_images.append(img_result)
        
        # Update extraction images count if extraction exists
        extractions = db.get_extraction_history(visit.user_id, limit=1)
        if extractions:
            # Note: This would require an update method in database
            pass
        
        return {
            "success": True,
            "images": downloaded_images,
            "images_count": len(downloaded_images),
            "url": visit.url
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract images: {str(e)}"
        }

