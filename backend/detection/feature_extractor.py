"""
Feature extraction for ML model
"""
import re
import math
from typing import Dict, Any
from urllib.parse import urlparse, parse_qs, unquote
from collections import Counter

class FeatureExtractor:
    """Extract features from HTTP requests for ML model"""
    
    def extract(self, url: str, method: str = 'GET', 
                headers: Dict = None, body: str = '') -> Dict[str, Any]:
        """
        Extract comprehensive features from HTTP request
        
        Returns:
            Dictionary of features
        """
        decoded_url = unquote(url)
        parsed = urlparse(decoded_url)
        
        features = {}
        
        # URL-based features
        features['url_length'] = len(decoded_url)
        features['domain_length'] = len(parsed.netloc)
        features['path_length'] = len(parsed.path)
        features['query_length'] = len(parsed.query)
        
        # Character counts
        features['num_dots'] = decoded_url.count('.')
        features['num_slashes'] = decoded_url.count('/')
        features['num_question_marks'] = decoded_url.count('?')
        features['num_ampersands'] = decoded_url.count('&')
        features['num_equals'] = decoded_url.count('=')
        features['num_hyphens'] = decoded_url.count('-')
        features['num_underscores'] = decoded_url.count('_')
        features['num_percent'] = decoded_url.count('%')
        features['num_semicolons'] = decoded_url.count(';')
        features['num_single_quotes'] = decoded_url.count("'")
        features['num_double_quotes'] = decoded_url.count('"')
        features['num_backslashes'] = decoded_url.count('\\')
        features['num_parentheses'] = decoded_url.count('(') + decoded_url.count(')')
        features['num_angle_brackets'] = decoded_url.count('<') + decoded_url.count('>')
        features['num_digits'] = sum(c.isdigit() for c in decoded_url)
        
        # Special character ratio
        special_chars = sum(not c.isalnum() and c not in ['.', '/', '?', '&', '=', '-', '_'] 
                          for c in decoded_url)
        features['num_special_chars'] = special_chars
        features['special_char_ratio'] = special_chars / len(decoded_url) if decoded_url else 0
        
        # Entropy (measure of randomness)
        features['entropy'] = self._calculate_entropy(decoded_url)
        
        # Subdomain count
        features['num_subdomains'] = parsed.netloc.count('.') if parsed.netloc else 0
        
        # Path depth
        features['path_depth'] = len([p for p in parsed.path.split('/') if p])
        
        # Query parameter count
        query_params = parse_qs(parsed.query)
        features['num_params'] = len(query_params)
        
        # Suspicious keywords (binary flags)
        features['has_script'] = int('<script' in decoded_url.lower())
        features['has_union'] = int('union' in decoded_url.lower())
        features['has_select'] = int('select' in decoded_url.lower())
        features['has_exec'] = int('exec' in decoded_url.lower() or 'execute' in decoded_url.lower())
        features['has_drop'] = int('drop' in decoded_url.lower())
        features['has_insert'] = int('insert' in decoded_url.lower())
        features['has_update'] = int('update' in decoded_url.lower())
        features['has_delete'] = int('delete' in decoded_url.lower())
        features['has_dotdot'] = int('..' in decoded_url)
        features['has_localhost'] = int('localhost' in decoded_url.lower() or '127.0.0.1' in decoded_url)
        features['has_file_protocol'] = int('file://' in decoded_url.lower())
        features['has_data_uri'] = int('data:' in decoded_url.lower())
        features['has_onerror'] = int('onerror' in decoded_url.lower())
        features['has_onload'] = int('onload' in decoded_url.lower())
        features['has_javascript'] = int('javascript:' in decoded_url.lower())
        features['has_eval'] = int('eval(' in decoded_url.lower())
        features['has_base64'] = int('base64' in decoded_url.lower())
        features['has_cmd'] = int(re.search(r'\bcmd\b', decoded_url.lower()) is not None)
        features['has_shell'] = int('shell' in decoded_url.lower())
        features['has_system'] = int('system' in decoded_url.lower())
        features['has_etc_passwd'] = int('etc/passwd' in decoded_url.lower())
        
        # Encoding indicators
        features['has_hex_encoding'] = int(re.search(r'\\x[0-9a-f]{2}', decoded_url.lower()) is not None)
        features['has_unicode_encoding'] = int(re.search(r'\\u[0-9a-f]{4}', decoded_url.lower()) is not None)
        features['has_url_encoding'] = int('%' in decoded_url and re.search(r'%[0-9a-f]{2}', decoded_url.lower()))
        
        # Method
        features['method_get'] = int(method == 'GET')
        features['method_post'] = int(method == 'POST')
        features['method_put'] = int(method == 'PUT')
        features['method_delete'] = int(method == 'DELETE')
        
        # Body length
        features['body_length'] = len(body)
        
        # Domain features
        features['is_ip_address'] = int(self._is_ip_address(parsed.netloc))
        features['has_port'] = int(':' in parsed.netloc and not self._is_ip_address(parsed.netloc))
        
        return features
    
    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text"""
        if not text:
            return 0.0
        
        counter = Counter(text)
        length = len(text)
        entropy = -sum((count / length) * math.log2(count / length) 
                      for count in counter.values())
        return entropy
    
    def _is_ip_address(self, text: str) -> bool:
        """Check if text is an IP address"""
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}(:\d+)?$'
        return bool(re.match(ip_pattern, text))
    
    def get_feature_names(self) -> list:
        """Get list of all feature names"""
        dummy_features = self.extract('http://example.com/test')
        return list(dummy_features.keys())
