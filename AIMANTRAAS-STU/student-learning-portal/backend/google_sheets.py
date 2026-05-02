"""
Google Sheets Integration Module for AI Mantraas Student Portal
===============================================================
This module handles all interactions with Google Sheets API.
It provides methods to read from and write to Google Sheets.
"""

import os
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from .env file in root directory
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scope for Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GoogleSheetsManager:
    """Manager class for Google Sheets operations."""
    
    def __init__(self, spreadsheet_id=None, credentials_dict=None):
        """
        Initialize the Google Sheets manager.
        
        Args:
            spreadsheet_id: The ID of the Google Sheet (from URL)
            credentials_dict: Dictionary containing service account credentials
        """
        self.spreadsheet_id = spreadsheet_id or os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
        self.credentials_dict = credentials_dict
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Sheets service."""
        try:
            if self.credentials_dict:
                # Use provided credentials dictionary
                credentials = service_account.Credentials.from_service_account_info(
                    self.credentials_dict, 
                    scopes=SCOPES
                )
            else:
                # Try to load from environment variable (private key)
                private_key = os.getenv('GOOGLE_PRIVATE_KEY', '')
                if private_key:
                    # Create credentials from environment variables
                    credentials_info = {
                        "type": "service_account",
                        "project_id": "ai-mantraas-stu",
                        "private_key": private_key.replace('\\n', '\n'),
                        "client_email": os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL'),
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                    credentials = service_account.Credentials.from_service_account_info(
                        credentials_info, 
                        scopes=SCOPES
                    )
                else:
                    logger.error("No Google credentials found")
                    return
            
            # Build the service
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.info("Google Sheets service initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Google Sheets service: {e}")
            self.service = None
    
    def is_connected(self):
        """Check if the service is connected."""
        return self.service is not None
    
    def read_sheet(self, range_name):
        """
        Read data from a Google Sheet.
        
        Args:
            range_name: The range to read (e.g., 'Sheet1!A1:D10')
            
        Returns:
            List of rows if successful, None otherwise
        """
        if not self.service:
            logger.error("Service not initialized")
            return None
        
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            logger.info(f"Read {len(values)} rows from {range_name}")
            return values
            
        except HttpError as e:
            logger.error(f"HTTP error reading sheet: {e}")
            return None
        except Exception as e:
            logger.error(f"Error reading sheet: {e}")
            return None
    
    def write_to_sheet(self, range_name, values, major_dimension='ROWS'):
        """
        Write data to a Google Sheet.
        
        Args:
            range_name: The range to write (e.g., 'Sheet1!A1')
            values: List of lists to write
            major_dimension: 'ROWS' or 'COLUMNS'
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Service not initialized")
            return False
        
        try:
            body = {
                'values': values,
                'majorDimension': major_dimension
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"Wrote {result.get('updatedCells', 0)} cells to {range_name}")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error writing to sheet: {e}")
            return False
        except Exception as e:
            logger.error(f"Error writing to sheet: {e}")
            return False
    
    def append_to_sheet(self, sheet_name, values):
        """
        Append a row to a Google Sheet.
        
        Args:
            sheet_name: Name of the sheet (e.g., 'JoinRequests')
            values: List of values to append
            
        Returns:
            True if successful, False otherwise
        """
        if not self.service:
            logger.error("Service not initialized")
            return False
        
        try:
            range_name = f"{sheet_name}!A:A"
            body = {
                'values': [values],
                'majorDimension': 'ROWS'
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            logger.info(f"Appended row to {sheet_name}")
            return True
            
        except HttpError as e:
            logger.error(f"HTTP error appending to sheet: {e}")
            return False
        except Exception as e:
            logger.error(f"Error appending to sheet: {e}")
            return False
    
    def get_or_create_sheet(self, sheet_title):
        """
        Get or create a sheet in the spreadsheet.
        
        Args:
            sheet_title: Title of the sheet to create
            
        Returns:
            Sheet ID if successful, None otherwise
        """
        if not self.service:
            logger.error("Service not initialized")
            return None
        
        try:
            # First, try to get existing sheet
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            for sheet in sheets:
                if sheet.get('properties', {}).get('title') == sheet_title:
                    logger.info(f"Sheet '{sheet_title}' already exists")
                    return sheet.get('properties', {}).get('sheetId')
            
            # Create new sheet
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_title
                        }
                    }
                }]
            }
            
            result = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            sheet_id = result.get('replies', [{}])[0].get('addSheet', {}).get('properties', {}).get('sheetId')
            logger.info(f"Created new sheet '{sheet_title}' with ID {sheet_id}")
            return sheet_id
            
        except HttpError as e:
            logger.error(f"HTTP error creating sheet: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating sheet: {e}")
            return None


# Global instance
sheets_manager = None


def initialize_sheets():
    """Initialize the Google Sheets manager."""
    global sheets_manager
    
    spreadsheet_id = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    
    if not spreadsheet_id:
        logger.error("GOOGLE_SHEETS_SPREADSHEET_ID not set in environment")
        return None
    
    sheets_manager = GoogleSheetsManager(spreadsheet_id=spreadsheet_id)
    
    if sheets_manager.is_connected():
        logger.info("Google Sheets initialized successfully")
        return sheets_manager
    else:
        logger.error("Failed to initialize Google Sheets")
        return None


def get_sheets_manager():
    """Get the global sheets manager instance."""
    global sheets_manager
    if sheets_manager is None:
        initialize_sheets()
    return sheets_manager
