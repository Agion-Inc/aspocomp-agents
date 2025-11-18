"""SharePoint service for file operations using Microsoft Graph API."""

import os
import requests
from typing import List, Dict, Any, Optional
from web_chat.backend import config


class SharePointService:
    """Service for interacting with SharePoint files via Microsoft Graph API."""
    
    def __init__(self):
        """Initialize SharePoint service with configuration."""
        self.site_id = os.environ.get('GLOBAL_SHAREPOINT_SITE_ID', '')
        self.folder_path = os.environ.get('SHAREPOINT_FOLDER_PATH', 'General')
        
        # Parse site ID (format: hostname,siteId,webId)
        if self.site_id:
            parts = self.site_id.split(',')
            if len(parts) >= 2:
                self.hostname = parts[0]
                self.site_id_parsed = parts[1]
                self.web_id = parts[2] if len(parts) > 2 else None
            else:
                self.hostname = None
                self.site_id_parsed = None
                self.web_id = None
        else:
            self.hostname = None
            self.site_id_parsed = None
            self.web_id = None
    
    def get_access_token(self, user_token: str) -> Optional[str]:
        """Get access token for Microsoft Graph API.
        
        Args:
            user_token: User's Azure AD access token
            
        Returns:
            Access token or None if unavailable
        """
        # For now, use the user's token directly
        # In production, you might want to exchange it for a SharePoint-specific token
        return user_token
    
    def get_graph_api_url(self, endpoint: str) -> str:
        """Build Microsoft Graph API URL.
        
        Args:
            endpoint: API endpoint path
            
        Returns:
            Full Graph API URL
        """
        base_url = "https://graph.microsoft.com/v1.0"
        return f"{base_url}{endpoint}"
    
    def get_site_drive_id(self, access_token: str) -> Optional[str]:
        """Get the default drive ID for the SharePoint site.
        
        Args:
            access_token: Access token for Graph API
            
        Returns:
            Drive ID or None
        """
        if not self.site_id_parsed:
            return None
        
        try:
            # Get site drives
            url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drives")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            drives = data.get('value', [])
            
            # Return the first drive (usually the default document library)
            if drives:
                return drives[0].get('id')
            
            return None
        except Exception as e:
            print(f"Error getting drive ID: {e}")
            return None
    
    def list_files(self, access_token: str, folder_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """List files in SharePoint folder.
        
        Args:
            access_token: Access token for Graph API
            folder_path: Folder path relative to drive root (defaults to configured folder)
            
        Returns:
            List of file/directory information dictionaries
        """
        if not self.site_id_parsed:
            return []
        
        folder_path = folder_path or self.folder_path
        
        try:
            # Get drive ID
            drive_id = self.get_site_drive_id(access_token)
            if not drive_id:
                return []
            
            # Build path for folder
            if folder_path and folder_path.strip():
                # Encode folder path
                path_parts = folder_path.strip('/').split('/')
                encoded_path = '/'.join(requests.utils.quote(part, safe='') for part in path_parts if part)
                if encoded_path:
                    url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drives/{drive_id}/root:/{encoded_path}:/children")
                else:
                    url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drives/{drive_id}/root/children")
            else:
                url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drives/{drive_id}/root/children")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = []
            
            for item in data.get('value', []):
                # Check if it's a folder
                is_folder = item.get('folder') is not None
                
                items.append({
                    'id': item.get('id'),
                    'name': item.get('name'),
                    'size': item.get('size', 0),
                    'webUrl': item.get('webUrl'),
                    'lastModifiedDateTime': item.get('lastModifiedDateTime'),
                    'createdDateTime': item.get('createdDateTime'),
                    'createdBy': item.get('createdBy', {}).get('user', {}).get('displayName', ''),
                    'isFolder': is_folder,
                    'mimeType': item.get('file', {}).get('mimeType', '') if item.get('file') else None
                })
            
            return items
        except Exception as e:
            print(f"Error listing files: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def upload_file(self, access_token: str, file_content: bytes, filename: str, folder_path: Optional[str] = None) -> Dict[str, Any]:
        """Upload a file to SharePoint.
        
        Args:
            access_token: Access token for Graph API
            file_content: File content as bytes
            filename: Name of the file
            folder_path: Folder path relative to drive root (defaults to configured folder)
            
        Returns:
            Dictionary with upload result
        """
        if not self.site_id_parsed:
            return {'success': False, 'error': 'SharePoint site not configured'}
        
        folder_path = folder_path or self.folder_path
        
        try:
            # Get drive ID
            drive_id = self.get_site_drive_id(access_token)
            if not drive_id:
                return {'success': False, 'error': 'Could not get drive ID'}
            
            # Build upload URL
            if folder_path:
                path_parts = folder_path.strip('/').split('/')
                encoded_path = '/'.join(requests.utils.quote(part, safe='') for part in path_parts)
                encoded_filename = requests.utils.quote(filename, safe='')
                url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drives/{drive_id}/root:/{encoded_path}/{encoded_filename}:/content")
            else:
                encoded_filename = requests.utils.quote(filename, safe='')
                url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drives/{drive_id}/root:/{encoded_filename}:/content")
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.put(url, headers=headers, data=file_content, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return {
                'success': True,
                'id': result.get('id'),
                'name': result.get('name'),
                'webUrl': result.get('webUrl'),
                'size': result.get('size', 0)
            }
        except Exception as e:
            print(f"Error uploading file: {e}")
            return {'success': False, 'error': str(e)}
    
    def download_file(self, access_token: str, file_id: str) -> Optional[bytes]:
        """Download a file from SharePoint.
        
        Args:
            access_token: Access token for Graph API
            file_id: SharePoint file ID
            
        Returns:
            File content as bytes or None
        """
        if not self.site_id_parsed:
            return None
        
        try:
            url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drive/items/{file_id}/content")
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return response.content
        except Exception as e:
            print(f"Error downloading file: {e}")
            return None
    
    def get_file_download_url(self, access_token: str, file_id: str) -> Optional[str]:
        """Get a download URL for a file (for direct browser download).
        
        Args:
            access_token: Access token for Graph API
            file_id: SharePoint file ID
            
        Returns:
            Download URL or None
        """
        if not self.site_id_parsed:
            return None
        
        try:
            url = self.get_graph_api_url(f"/sites/{self.site_id_parsed}/drive/items/{file_id}")
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            return data.get('@microsoft.graph.downloadUrl') or data.get('webUrl')
        except Exception as e:
            print(f"Error getting download URL: {e}")
            return None


def get_sharepoint_service() -> SharePointService:
    """Get SharePoint service instance."""
    return SharePointService()

