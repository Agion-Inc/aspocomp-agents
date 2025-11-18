"""Tool for navigating to a web page using Playwright."""

import sys
import os
import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlparse

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '../../..')
sys.path.insert(0, os.path.abspath(project_root))

from agents.data_browser.database import DataBrowserDatabase
from agents.data_browser.playwright_engine import PlaywrightEngine
from agents.data_browser.credential_manager import CredentialManager
from agents.data_browser.models import PageVisit, Service
from agents.data_browser.config import AGENT_CONFIG


def navigate_to_page(
    url: str,
    user_id: str,
    service_id: Optional[int] = None,
    credential_id: Optional[int] = None,
    wait_for_selector: Optional[str] = None
) -> Dict[str, Any]:
    """Navigate to a web page using Playwright.
    
    This tool navigates to a web page, optionally using stored credentials
    for authentication. It logs the visit and returns navigation status.
    
    Args:
        url: URL to navigate to (required)
        user_id: User ID making the request (required)
        service_id: Optional service ID if known
        credential_id: Optional credential ID to use for authentication
        wait_for_selector: Optional CSS selector to wait for after navigation
    
    Returns:
        Dictionary with visit_id, navigation_status, page_title, and url
    """
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return {
                "success": False,
                "error": "Invalid URL format"
            }
        
        db = DataBrowserDatabase()
        credential_manager = CredentialManager()
        
        # Get or create service
        domain = parsed.netloc
        service = db.get_service_by_domain(domain)
        if not service:
            service = Service(
                name=domain,
                domain=domain,
                base_url=f"{parsed.scheme}://{domain}"
            )
            service_id = db.save_service(service)
            service.id = service_id
        else:
            service_id = service.id
        
        # Get credentials if credential_id provided
        credentials = None
        credential_id_to_use = credential_id
        
        if credential_id_to_use:
            credential = db.get_credential(credential_id_to_use, user_id)
            if credential:
                # Decrypt credentials
                decrypted = credential_manager.decrypt_credential(credential.encrypted_data)
                credentials = decrypted
                # Update last used
                db.update_credential_last_used(credential_id_to_use)
        else:
            # Try to find existing credentials for this service
            existing_creds = db.get_credentials_for_service(service_id, user_id)
            if existing_creds:
                credential_id_to_use = existing_creds[0].id
                credential = db.get_credential(credential_id_to_use, user_id)
                if credential:
                    decrypted = credential_manager.decrypt_credential(credential.encrypted_data)
                    credentials = decrypted
                    db.update_credential_last_used(credential_id_to_use)
        
        # Navigate using Playwright
        engine = PlaywrightEngine(AGENT_CONFIG)
        
        async def navigate():
            await engine.start()
            result = await engine.navigate_to_page(url, credentials, wait_for_selector)
            await engine.close()
            return result
        
        # Handle asyncio in sync context - check if event loop is running
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, we need to run in a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, navigate())
                result = future.result()
        except RuntimeError:
            # No event loop running, safe to use asyncio.run
            result = asyncio.run(navigate())
        
        # Log visit
        visit = PageVisit(
            url=url,
            service_id=service_id,
            credential_id=credential_id_to_use if 'credential_id_to_use' in locals() and credential_id_to_use else credential_id,
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
                "service_id": service_id
            }
        else:
            return {
                "success": False,
                "visit_id": visit_id,
                "error": result.get("error", "Navigation failed")
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to navigate to page: {str(e)}"
        }

