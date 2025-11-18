"""Tool for executing stored Playwright navigation scripts."""

import sys
import os
import asyncio
from typing import Dict, Any, Optional

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.data_browser.database import DataBrowserDatabase
from agents.data_browser.playwright_engine import PlaywrightEngine
from agents.data_browser.models import PageVisit
from agents.data_browser.config import AGENT_CONFIG


def execute_navigation_script(
    script_id: int,
    url: str,
    user_id: str,
    parameters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Execute a stored Playwright navigation script.
    
    This tool executes a previously stored Playwright script for complex
    navigation flows. The script receives the page object and parameters.
    
    Args:
        script_id: Navigation script ID (required)
        url: Starting URL (required)
        user_id: User ID making the request (required)
        parameters: Optional parameters dictionary to pass to script
    
    Returns:
        Dictionary with visit_id, navigation_status, page_title, and url
    """
    try:
        db = DataBrowserDatabase()
        
        # Get script
        script = db.get_navigation_script(script_id)
        if not script:
            return {
                "success": False,
                "error": f"Script ID {script_id} not found"
            }
        
        # Get service
        service = db.get_service(script.service_id)
        if not service:
            return {
                "success": False,
                "error": f"Service ID {script.service_id} not found"
            }
        
        # Execute script using Playwright
        engine = PlaywrightEngine(AGENT_CONFIG)
        
        async def execute():
            await engine.start()
            result = await engine.execute_script(script.script_code, url, parameters)
            await engine.close()
            return result
        
        # Handle asyncio in sync context - check if event loop is running
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, execute())
                result = future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            result = asyncio.run(execute())
        
        # Log visit
        visit = PageVisit(
            url=url,
            service_id=script.service_id,
            credential_id=None,  # Scripts handle their own auth
            user_id=user_id,
            navigation_successful=result.get("success", False),
            error_message=result.get("error")
        )
        visit_id = db.save_page_visit(visit)
        
        if result.get("success"):
            return {
                "success": True,
                "visit_id": visit_id,
                "page_title": result.get("page_title", ""),
                "url": result.get("url", url),
                "service_id": script.service_id
            }
        else:
            return {
                "success": False,
                "visit_id": visit_id,
                "error": result.get("error", "Script execution failed")
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute navigation script: {str(e)}"
        }

