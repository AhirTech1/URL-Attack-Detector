"""
HTTP Log file parser (CSV/JSON)
"""
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LogParser:
    """Parse HTTP log files (CSV or JSON format)"""
    
    def parse(self, log_file: Path) -> List[Dict[str, Any]]:
        """
        Parse log file and extract HTTP requests
        
        Args:
            log_file: Path to log file (.csv or .json)
        
        Returns:
            List of HTTP request dictionaries
        """
        if log_file.suffix == '.csv':
            return self._parse_csv(log_file)
        elif log_file.suffix == '.json':
            return self._parse_json(log_file)
        else:
            raise ValueError(f"Unsupported file format: {log_file.suffix}")
    
    def _parse_csv(self, csv_file: Path) -> List[Dict[str, Any]]:
        """Parse CSV log file"""
        requests = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    request = self._normalize_log_entry(row)
                    if request:
                        requests.append(request)
            
            logger.info(f"Parsed {len(requests)} entries from CSV")
        
        except Exception as e:
            logger.error(f"Error parsing CSV: {e}")
            raise
        
        return requests
    
    def _parse_json(self, json_file: Path) -> List[Dict[str, Any]]:
        """Parse JSON log file"""
        requests = []
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both array and object with results key
            if isinstance(data, list):
                entries = data
            elif isinstance(data, dict) and 'results' in data:
                entries = data['results']
            else:
                entries = [data]
            
            for entry in entries:
                request = self._normalize_log_entry(entry)
                if request:
                    requests.append(request)
            
            logger.info(f"Parsed {len(requests)} entries from JSON")
        
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            raise
        
        return requests
    
    def _normalize_log_entry(self, entry: Dict) -> Dict[str, Any]:
        """
        Normalize log entry to standard format
        
        Expected fields (flexible):
        - url/uri/request_uri
        - src_ip/source_ip/client_ip
        - dst_ip/dest_ip/server_ip/host
        - timestamp/time
        - method
        - headers (optional)
        - body (optional)
        """
        try:
            # Extract URL (try multiple field names)
            url = (entry.get('url') or 
                   entry.get('uri') or 
                   entry.get('request_uri') or
                   entry.get('request') or
                   entry.get('path'))
            
            if not url:
                logger.debug("No URL found in log entry, skipping")
                return None
            
            # Ensure URL is a string
            url = str(url)
            
            # Build full URL if needed
            if not url.startswith('http'):
                host = (entry.get('host') or 
                       entry.get('dst_ip') or 
                       entry.get('server_ip') or
                       'unknown')
                url = f"http://{host}{url}"
            
            # Extract other fields with safe string conversion
            src_ip = str(entry.get('src_ip') or 
                        entry.get('source_ip') or 
                        entry.get('client_ip') or
                        entry.get('ip') or
                        'unknown')
            
            dst_ip = str(entry.get('dst_ip') or 
                        entry.get('dest_ip') or 
                        entry.get('server_ip') or
                        entry.get('host') or
                        'unknown')
            
            timestamp = entry.get('timestamp') or entry.get('time')
            if timestamp:
                timestamp = str(timestamp)
            else:
                timestamp = datetime.now().isoformat()
            
            method = str(entry.get('method') or 'GET')
            
            headers = entry.get('headers') or {}
            if isinstance(headers, str):
                try:
                    headers = json.loads(headers)
                except:
                    headers = {}
            
            body = str(entry.get('body') or entry.get('data') or '')
            
            return {
                'url': url,
                'method': method,
                'src_ip': src_ip,
                'dst_ip': dst_ip,
                'timestamp': timestamp,
                'headers': headers,
                'body': body
            }
        
        except Exception as e:
            logger.error(f"Error normalizing log entry: {e}")
            logger.error(f"Entry data: {entry}")
            return None
