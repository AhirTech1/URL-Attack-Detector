"""
PCAP file parser to extract HTTP requests
Uses scapy for packet parsing
"""
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

try:
    from scapy.all import rdpcap, TCP, Raw, IP
    from scapy.layers.http import HTTPRequest, HTTP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    logging.warning("Scapy not available. PCAP parsing will not work.")

logger = logging.getLogger(__name__)

class PCAPParser:
    """Parse PCAP files to extract HTTP requests"""
    
    def __init__(self):
        """Initialize parser"""
        if not SCAPY_AVAILABLE:
            logger.warning("Scapy not installed. Install with: pip install scapy")
    
    def parse(self, pcap_file: Path) -> List[Dict[str, Any]]:
        """
        Parse PCAP file and extract HTTP requests
        
        Args:
            pcap_file: Path to PCAP file
        
        Returns:
            List of HTTP request dictionaries
        """
        if not SCAPY_AVAILABLE:
            raise RuntimeError("Scapy not available. Cannot parse PCAP files.")
        
        requests = []
        
        try:
            logger.info(f"Reading PCAP file: {pcap_file}")
            packets = rdpcap(str(pcap_file))
            logger.info(f"Total packets: {len(packets)}")
            
            for packet in packets:
                try:
                    # Check if packet has HTTP layer
                    if packet.haslayer(HTTPRequest):
                        http_request = self._extract_http_request(packet)
                        if http_request:
                            requests.append(http_request)
                    
                    # Also check for HTTP in Raw layer (for non-standard parsers)
                    elif packet.haslayer(TCP) and packet.haslayer(Raw):
                        raw_data = packet[Raw].load
                        if self._is_http_request(raw_data):
                            http_request = self._parse_raw_http(packet, raw_data)
                            if http_request:
                                requests.append(http_request)
                
                except Exception as e:
                    logger.debug(f"Error parsing packet: {e}")
                    continue
            
            logger.info(f"Extracted {len(requests)} HTTP requests")
        
        except Exception as e:
            logger.error(f"Error reading PCAP file: {e}")
            raise
        
        return requests
    
    def _extract_http_request(self, packet) -> Dict[str, Any]:
        """Extract HTTP request details from packet with HTTP layer"""
        try:
            http_layer = packet[HTTPRequest]
            
            # Build URL
            host = http_layer.Host.decode() if http_layer.Host else 'unknown'
            path = http_layer.Path.decode() if http_layer.Path else '/'
            url = f"http://{host}{path}"
            
            # Extract other fields
            method = http_layer.Method.decode() if http_layer.Method else 'GET'
            
            # Get IPs
            src_ip = packet[IP].src if packet.haslayer(IP) else 'unknown'
            dst_ip = packet[IP].dst if packet.haslayer(IP) else 'unknown'
            
            # Timestamp
            timestamp = datetime.fromtimestamp(float(packet.time)).isoformat()
            
            # Headers
            headers = {}
            if hasattr(http_layer, 'fields'):
                for field, value in http_layer.fields.items():
                    if isinstance(value, bytes):
                        headers[field] = value.decode('utf-8', errors='ignore')
            
            # Body (if present in Raw layer)
            body = ''
            if packet.haslayer(Raw):
                try:
                    raw_load = packet[Raw].load
                    if isinstance(raw_load, bytes):
                        # Try to extract body after headers
                        body_start = raw_load.find(b'\r\n\r\n')
                        if body_start != -1:
                            body = raw_load[body_start + 4:].decode('utf-8', errors='ignore')
                except:
                    pass
            
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
            logger.debug(f"Error extracting HTTP request: {e}")
            return None
    
    def _is_http_request(self, raw_data: bytes) -> bool:
        """Check if raw data is an HTTP request"""
        try:
            if isinstance(raw_data, bytes):
                data_str = raw_data.decode('utf-8', errors='ignore')
                return any(data_str.startswith(method) 
                          for method in ['GET ', 'POST ', 'PUT ', 'DELETE ', 'HEAD ', 'OPTIONS ', 'PATCH '])
            return False
        except:
            return False
    
    def _parse_raw_http(self, packet, raw_data: bytes) -> Dict[str, Any]:
        """Parse HTTP request from raw TCP data"""
        try:
            data_str = raw_data.decode('utf-8', errors='ignore')
            lines = data_str.split('\r\n')
            
            if not lines:
                return None
            
            # Parse request line
            request_line = lines[0].split(' ')
            if len(request_line) < 2:
                return None
            
            method = request_line[0]
            path = request_line[1]
            
            # Parse headers
            headers = {}
            host = 'unknown'
            body = ''
            
            i = 1
            while i < len(lines) and lines[i]:
                if ': ' in lines[i]:
                    key, value = lines[i].split(': ', 1)
                    headers[key] = value
                    if key.lower() == 'host':
                        host = value
                i += 1
            
            # Body is after empty line
            if i + 1 < len(lines):
                body = '\r\n'.join(lines[i + 1:])
            
            # Build URL
            url = f"http://{host}{path}"
            
            # Get IPs
            src_ip = packet[IP].src if packet.haslayer(IP) else 'unknown'
            dst_ip = packet[IP].dst if packet.haslayer(IP) else 'unknown'
            
            # Timestamp
            timestamp = datetime.fromtimestamp(float(packet.time)).isoformat()
            
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
            logger.debug(f"Error parsing raw HTTP: {e}")
            return None
