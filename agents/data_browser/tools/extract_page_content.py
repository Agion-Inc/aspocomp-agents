"""Tool for extracting content from a web page."""

import sys
import os
import asyncio
import time
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.data_browser.database import DataBrowserDatabase
from agents.data_browser.playwright_engine import PlaywrightEngine
from agents.data_browser.extractor import ContentExtractor
from agents.data_browser.formatter import DataFormatter
from agents.data_browser.models import Extraction
from agents.data_browser.config import AGENT_CONFIG


def extract_page_content(
    visit_id: int,
    output_format: str = "json",
    extraction_selectors: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Extract text and structured content from a page.
    
    This tool extracts content from a previously visited page. It extracts
    text, headers, links, tables, and other structured content, then formats
    it as JSON or Markdown.
    
    Args:
        visit_id: Page visit ID from navigate_to_page (required)
        output_format: Output format - "json" or "markdown" (default: "json")
        extraction_selectors: Optional CSS selectors for specific content:
            {
                "main_content": "CSS selector",
                "tables": "CSS selector",
                "images": "CSS selector"
            }
    
    Returns:
        Dictionary with extraction_id, extracted_data (JSON or Markdown string),
        and metadata
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
        
        if not visit.navigation_successful:
            return {
                "success": False,
                "error": f"Navigation was not successful for visit {visit_id}"
            }
        
        # Validate output format
        if output_format not in ["json", "markdown"]:
            return {
                "success": False,
                "error": "output_format must be 'json' or 'markdown'"
            }
        
        # Get credentials if available
        credentials = None
        if visit.credential_id:
            from agents.data_browser.credential_manager import CredentialManager
            credential_manager = CredentialManager()
            credential = db.get_credential(visit.credential_id, visit.user_id)
            if credential:
                credentials = credential_manager.decrypt_credential(credential.encrypted_data)
        
        # Get page content using Playwright
        engine = PlaywrightEngine(AGENT_CONFIG)
        start_time = time.time()
        
        async def extract():
            await engine.start()
            # Navigate with credentials if available
            nav_result = await engine.navigate_to_page(visit.url, credentials)
            if not nav_result.get("success"):
                return {"error": nav_result.get("error", "Navigation failed")}
            # Get content from current page
            content = await engine.get_page_content(visit.url)
            await engine.close()
            return content
        
        # Handle asyncio in sync context - check if event loop is running
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, extract())
                page_content = future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            page_content = asyncio.run(extract())
        
        if page_content.get("error"):
            return {
                "success": False,
                "error": f"Failed to get page content: {page_content.get('error')}"
            }
        
        # Extract content
        extractor = ContentExtractor(AGENT_CONFIG)
        extracted = extractor.extract_text_content(
            page_content.get("html", ""),
            visit.url,
            extraction_selectors
        )
        
        # Add extraction metadata
        extracted["extracted_at"] = datetime.now().isoformat()
        
        # Format output
        formatter = DataFormatter()
        if output_format == "json":
            formatted_data = formatter.format_as_json(
                extracted,
                visit.url,
                page_content.get("title", "")
            )
        else:
            formatted_data = formatter.format_as_markdown(
                extracted,
                visit.url,
                page_content.get("title", "")
            )
        
        # Save extraction to file
        extraction_time_ms = int((time.time() - start_time) * 1000)
        extraction_dir = os.path.join(
            AGENT_CONFIG["storage"]["extractions_path"],
            str(visit_id)
        )
        os.makedirs(extraction_dir, exist_ok=True)
        
        file_extension = "json" if output_format == "json" else "md"
        file_path = os.path.join(extraction_dir, f"content.{file_extension}")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(formatted_data)
        
        # Create preview (first 500 chars)
        preview = formatted_data[:500] + "..." if len(formatted_data) > 500 else formatted_data
        
        # Save extraction record
        extraction = Extraction(
            visit_id=visit_id,
            url=visit.url,
            output_format=output_format,
            extracted_data_path=file_path,
            text_content_preview=preview,
            images_count=0,  # Will be updated by extract_images tool
            extraction_time_ms=extraction_time_ms
        )
        extraction_id = db.save_extraction(extraction)
        
        return {
            "success": True,
            "extraction_id": extraction_id,
            "extracted_data": formatted_data,
            "url": visit.url,
            "title": page_content.get("title", ""),
            "format": output_format,
            "extraction_time_ms": extraction_time_ms
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to extract page content: {str(e)}"
        }

