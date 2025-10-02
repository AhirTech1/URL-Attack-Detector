"""
Main URL Attack Detector
Combines rule-based and ML-based detection
"""
import re
import logging
from typing import Dict, List, Any
from datetime import datetime
from urllib.parse import urlparse, parse_qs, unquote
import os

from .rules_engine import RulesEngine
from .ml_detector import MLDetector
from .feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

class URLAttackDetector:
    """Hybrid URL attack detector using rules and ML"""
    
    VERSION = "1.0.0"
    
    ATTACK_TYPES = [
        'Benign',
        'SQLi',
        'XSS',
        'CMD Injection',
        'Directory Traversal',
        'Web Shell',
        'Credential Stuffing',
        'SSRF',
        'LFI/RFI',
        'Typosquatting',
        'HTTP Parameter Pollution',
        'XXE'
    ]
    
    def __init__(self):
        """Initialize the detector"""
        self.rules_engine = RulesEngine()
        self.ml_detector = MLDetector()
        self.feature_extractor = FeatureExtractor()
        self.loaded = False
        
        try:
            self.ml_detector.load_model()
            self.loaded = True
            logger.info("URLAttackDetector initialized successfully")
        except Exception as e:
            logger.warning(f"ML model not loaded: {e}. Using rules-only mode.")
            self.loaded = False
    
    def analyze_request(self, url: str, src_ip: str = 'unknown', 
                       dst_ip: str = 'unknown', timestamp: str = None,
                       method: str = 'GET', headers: Dict = None, 
                       body: str = '') -> Dict[str, Any]:
        """
        Analyze a single HTTP request for attacks
        
        Returns:
            Dictionary with detection results
        """
        # Ensure all inputs are strings
        url = str(url) if url else ''
        src_ip = str(src_ip) if src_ip else 'unknown'
        dst_ip = str(dst_ip) if dst_ip else 'unknown'
        method = str(method) if method else 'GET'
        body = str(body) if body else ''
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        else:
            timestamp = str(timestamp)
        
        # Decode URL
        decoded_url = unquote(url)
        parsed = urlparse(decoded_url)
        
        # Extract features
        features = self.feature_extractor.extract(decoded_url, method, headers or {}, body)
        
        # Rule-based detection (fast, high precision)
        rule_results = self.rules_engine.check(decoded_url, method, headers or {}, body)
        
        # ML-based detection (catches novel attacks)
        ml_prediction = None
        ml_confidence = 0.0
        
        if self.loaded:
            try:
                ml_prediction, ml_confidence = self.ml_detector.predict(features)
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")
        
        # Combine results
        final_prediction, final_confidence, rule_matched, success_flag = self._combine_results(
            rule_results, ml_prediction, ml_confidence, decoded_url
        )
        
        return {
            'timestamp': timestamp,
            'src_ip': src_ip,
            'dst_ip': dst_ip,
            'host': parsed.netloc or dst_ip,
            'uri': parsed.path + ('?' + parsed.query if parsed.query else ''),
            'method': method,
            'attack_prediction': final_prediction,
            'confidence': round(final_confidence, 4),
            'rule_matched': rule_matched,
            'success_flag': success_flag,
            'features': {
                'url_length': features.get('url_length', 0),
                'num_special_chars': features.get('num_special_chars', 0),
                'entropy': round(features.get('entropy', 0.0), 2)
            }
        }
    
    def _combine_results(self, rule_results: Dict, ml_prediction: str, 
                        ml_confidence: float, url: str) -> tuple:
        """
        Combine rule-based and ML results
        
        Returns:
            (attack_type, confidence, rule_matched, success_flag)
        """
        # If rules found something with high confidence, trust it
        if rule_results['matched_rules']:
            attack_type = rule_results['attack_type']
            confidence = rule_results['confidence']
            rule_matched = ', '.join(rule_results['matched_rules'])
            success_flag = self._check_success_indicators(url, attack_type)
            return attack_type, confidence, rule_matched, success_flag
        
        # If ML detector is available and confident
        if ml_prediction and ml_confidence > 0.5:
            return ml_prediction, ml_confidence, None, False
        
        # Default to benign
        return 'Benign', ml_confidence if ml_confidence > 0 else 0.1, None, False
    
    def _check_success_indicators(self, url: str, attack_type: str) -> bool:
        """
        Check if attack was likely successful based on response indicators
        This is a heuristic - in real scenarios, you'd check HTTP response codes/content
        """
        # Success indicators (simplified)
        success_patterns = {
            'SQLi': [r'union.*select', r'sleep\(\d+\)', r'benchmark\('],
            'XSS': [r'<script>', r'onerror=', r'onload='],
            'CMD Injection': [r';.*ls', r'\|.*whoami', r'&&.*cat'],
            'Directory Traversal': [r'\.\./.*passwd', r'\.\./.*shadow'],
            'LFI/RFI': [r'include.*\.\.', r'require.*http://'],
            'Web Shell': [r'\.php\?cmd=', r'backdoor\.(php|asp|jsp)']
        }
        
        if attack_type in success_patterns:
            patterns = success_patterns[attack_type]
            for pattern in patterns:
                if re.search(pattern, url.lower()):
                    return True
        
        return False
    
    def is_loaded(self) -> bool:
        """Check if ML model is loaded"""
        return self.loaded
    
    def get_version(self) -> str:
        """Get detector version"""
        return self.VERSION
    
    def get_supported_attacks(self) -> List[str]:
        """Get list of supported attack types"""
        return self.ATTACK_TYPES.copy()
