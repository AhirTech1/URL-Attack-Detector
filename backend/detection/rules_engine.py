"""
Rule-based detection engine for URL attacks
Uses regex patterns and heuristics
"""
import re
from typing import Dict, List, Any
from urllib.parse import unquote

class RulesEngine:
    """Rule-based attack detection"""
    
    def __init__(self):
        """Initialize rules"""
        self.rules = self._load_rules()
    
    def _load_rules(self) -> Dict[str, List[Dict]]:
        """Load detection rules for each attack type"""
        return {
            'SQLi': [
                {
                    'name': 'SQL_UNION_SELECT',
                    'pattern': r'union[\s]+select',
                    'confidence': 0.95
                },
                {
                    'name': 'SQL_OR_INJECTION',
                    'pattern': r"('|\"|`)\s*(or|OR)\s*('|\"|`)?\s*('|\"|`)?1('|\"|`)?",
                    'confidence': 0.90
                },
                {
                    'name': 'SQL_COMMENT',
                    'pattern': r'(--|#|\/\*)',
                    'confidence': 0.75
                },
                {
                    'name': 'SQL_SLEEP',
                    'pattern': r'(sleep|benchmark|waitfor|pg_sleep)\s*\(',
                    'confidence': 0.92
                },
                {
                    'name': 'SQL_DROP_TABLE',
                    'pattern': r'drop[\s]+(table|database)',
                    'confidence': 0.98
                },
                {
                    'name': 'SQL_EXEC',
                    'pattern': r'(exec|execute)\s*\(',
                    'confidence': 0.85
                },
                {
                    'name': 'SQL_STACKED_QUERIES',
                    'pattern': r';[\s]*(select|insert|update|delete|drop)',
                    'confidence': 0.93
                }
            ],
            'XSS': [
                {
                    'name': 'XSS_SCRIPT_TAG',
                    'pattern': r'<script[^>]*>.*?</script>',
                    'confidence': 0.95
                },
                {
                    'name': 'XSS_ONERROR',
                    'pattern': r'onerror\s*=',
                    'confidence': 0.92
                },
                {
                    'name': 'XSS_ONLOAD',
                    'pattern': r'onload\s*=',
                    'confidence': 0.90
                },
                {
                    'name': 'XSS_JAVASCRIPT',
                    'pattern': r'javascript:',
                    'confidence': 0.88
                },
                {
                    'name': 'XSS_IMG_TAG',
                    'pattern': r'<img[^>]+src[^>]*>',
                    'confidence': 0.80
                },
                {
                    'name': 'XSS_IFRAME',
                    'pattern': r'<iframe[^>]*>',
                    'confidence': 0.85
                },
                {
                    'name': 'XSS_SVG',
                    'pattern': r'<svg[^>]*onload',
                    'confidence': 0.90
                },
                {
                    'name': 'XSS_EVENT_HANDLER',
                    'pattern': r'on(click|mouseover|focus|blur|change|submit)\s*=',
                    'confidence': 0.85
                }
            ],
            'CMD Injection': [
                {
                    'name': 'CMD_SEMICOLON',
                    'pattern': r';[\s]*(ls|cat|whoami|id|pwd|uname|wget|curl)',
                    'confidence': 0.95
                },
                {
                    'name': 'CMD_PIPE',
                    'pattern': r'\|[\s]*(ls|cat|whoami|id|pwd|uname)',
                    'confidence': 0.93
                },
                {
                    'name': 'CMD_AND',
                    'pattern': r'&&[\s]*(ls|cat|whoami|id|pwd)',
                    'confidence': 0.93
                },
                {
                    'name': 'CMD_BACKTICK',
                    'pattern': r'`[^`]*`',
                    'confidence': 0.88
                },
                {
                    'name': 'CMD_DOLLAR_PAREN',
                    'pattern': r'\$\([^)]*\)',
                    'confidence': 0.88
                },
                {
                    'name': 'CMD_SYSTEM_CALLS',
                    'pattern': r'(system|exec|shell_exec|passthru|popen)\s*\(',
                    'confidence': 0.92
                }
            ],
            'Directory Traversal': [
                {
                    'name': 'DIR_TRAVERSAL_DOTDOT',
                    'pattern': r'\.\.[\\/]',
                    'confidence': 0.90
                },
                {
                    'name': 'DIR_TRAVERSAL_ENCODED',
                    'pattern': r'(%2e%2e[\\/%]|%252e%252e)',
                    'confidence': 0.93
                },
                {
                    'name': 'DIR_TRAVERSAL_UNIX_PATHS',
                    'pattern': r'(etc/passwd|etc/shadow|proc/self)',
                    'confidence': 0.95
                },
                {
                    'name': 'DIR_TRAVERSAL_WINDOWS',
                    'pattern': r'(windows[\\/]system32|winnt[\\/]system32)',
                    'confidence': 0.95
                },
                {
                    'name': 'DIR_TRAVERSAL_BACKSLASH',
                    'pattern': r'\.\.\\',
                    'confidence': 0.88
                }
            ],
            'LFI/RFI': [
                {
                    'name': 'LFI_FILE_PROTOCOL',
                    'pattern': r'file:///',
                    'confidence': 0.93
                },
                {
                    'name': 'RFI_HTTP_INCLUDE',
                    'pattern': r'(include|require)[^=]*=\s*https?://',
                    'confidence': 0.95
                },
                {
                    'name': 'LFI_PHP_WRAPPER',
                    'pattern': r'php://(input|filter)',
                    'confidence': 0.92
                },
                {
                    'name': 'LFI_DATA_URI',
                    'pattern': r'data:text/html',
                    'confidence': 0.85
                },
                {
                    'name': 'LFI_EXPECT',
                    'pattern': r'expect://',
                    'confidence': 0.90
                }
            ],
            'SSRF': [
                {
                    'name': 'SSRF_LOCALHOST',
                    'pattern': r'(localhost|127\.0\.0\.1|0\.0\.0\.0)',
                    'confidence': 0.85
                },
                {
                    'name': 'SSRF_INTERNAL_IP',
                    'pattern': r'(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2[0-9]|3[01])\.\d{1,3}\.\d{1,3})',
                    'confidence': 0.80
                },
                {
                    'name': 'SSRF_METADATA',
                    'pattern': r'169\.254\.169\.254',
                    'confidence': 0.98
                },
                {
                    'name': 'SSRF_REDIRECT',
                    'pattern': r'(url|redirect|proxy|fetch)\s*=\s*https?://',
                    'confidence': 0.82
                }
            ],
            'Web Shell': [
                {
                    'name': 'WEBSHELL_PHP',
                    'pattern': r'(c99|r57|b374k|shell|cmd)\.php',
                    'confidence': 0.95
                },
                {
                    'name': 'WEBSHELL_ASP',
                    'pattern': r'(backdoor|shell|cmd)\.(asp|aspx)',
                    'confidence': 0.95
                },
                {
                    'name': 'WEBSHELL_JSP',
                    'pattern': r'(cmd|shell|backdoor)\.jsp',
                    'confidence': 0.95
                },
                {
                    'name': 'WEBSHELL_EVAL',
                    'pattern': r'(eval|assert|base64_decode)\s*\(',
                    'confidence': 0.80
                }
            ],
            'Credential Stuffing': [
                {
                    'name': 'CRED_STUFF_COMMON_COMBO',
                    'pattern': r'(username|user|email)=.*(password|pass|pwd)=',
                    'confidence': 0.70
                },
                {
                    'name': 'CRED_STUFF_ADMIN',
                    'pattern': r'(admin|root|administrator):',
                    'confidence': 0.75
                }
            ],
            'Typosquatting': [
                {
                    'name': 'TYPO_HOMOGRAPH',
                    'pattern': r'[а-яА-Я]',  # Cyrillic characters
                    'confidence': 0.85
                },
                {
                    'name': 'TYPO_SUBDOMAIN_SPAM',
                    'pattern': r'([a-z0-9-]+\.){5,}',
                    'confidence': 0.75
                }
            ],
            'HTTP Parameter Pollution': [
                {
                    'name': 'HPP_DUPLICATE_PARAMS',
                    'pattern': r'([?&])([^=&]+)=([^&]*)&\2=',
                    'confidence': 0.80
                }
            ],
            'XXE': [
                {
                    'name': 'XXE_DOCTYPE',
                    'pattern': r'<!DOCTYPE[^>]*<!ENTITY',
                    'confidence': 0.92
                },
                {
                    'name': 'XXE_ENTITY',
                    'pattern': r'<!ENTITY[^>]*SYSTEM',
                    'confidence': 0.95
                },
                {
                    'name': 'XXE_PARAMETER_ENTITY',
                    'pattern': r'<!ENTITY\s+%',
                    'confidence': 0.90
                }
            ]
        }
    
    def check(self, url: str, method: str = 'GET', 
             headers: Dict = None, body: str = '') -> Dict[str, Any]:
        """
        Check URL against all rules
        
        Returns:
            {
                'attack_type': str,
                'confidence': float,
                'matched_rules': List[str]
            }
        """
        # Combine all checkable content
        content = f"{url} {body}".lower()
        
        matched_rules = []
        max_confidence = 0.0
        detected_attack = 'Benign'
        
        # Check each attack type
        for attack_type, rules in self.rules.items():
            for rule in rules:
                if re.search(rule['pattern'], content, re.IGNORECASE):
                    matched_rules.append(rule['name'])
                    if rule['confidence'] > max_confidence:
                        max_confidence = rule['confidence']
                        detected_attack = attack_type
        
        return {
            'attack_type': detected_attack,
            'confidence': max_confidence,
            'matched_rules': matched_rules
        }
    
    def get_rule_count(self) -> int:
        """Get total number of rules"""
        return sum(len(rules) for rules in self.rules.values())
