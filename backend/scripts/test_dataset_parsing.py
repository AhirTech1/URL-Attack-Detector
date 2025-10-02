"""
Quick test to verify the detector can handle dataset files
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from detection.detector import URLAttackDetector
from analysis.log_parser import LogParser

def test_dataset_parsing():
    """Test parsing the generated datasets"""
    
    # Initialize
    detector = URLAttackDetector()
    log_parser = LogParser()
    
    # Test CSV
    csv_file = Path(__file__).parent.parent / 'data' / 'test_dataset.csv'
    
    if not csv_file.exists():
        print(f"❌ Test file not found: {csv_file}")
        return False
    
    print(f"📁 Testing: {csv_file.name}")
    print("=" * 60)
    
    try:
        # Parse file
        print("⏳ Parsing CSV file...")
        entries = log_parser.parse(csv_file)
        print(f"✅ Parsed {len(entries)} entries")
        
        # Test first few entries
        print("\n⏳ Testing detection on first 5 entries...")
        for i, entry in enumerate(entries[:5]):
            print(f"\n  Entry {i+1}:")
            print(f"    URL: {entry['url'][:80]}...")
            
            result = detector.analyze_request(
                url=entry['url'],
                src_ip=entry.get('src_ip', 'unknown'),
                dst_ip=entry.get('dst_ip', 'unknown'),
                timestamp=entry.get('timestamp'),
                method=entry.get('method', 'GET')
            )
            
            print(f"    Detected: {result['attack_prediction']}")
            print(f"    Confidence: {result['confidence']:.2%}")
            if result['rule_matched']:
                print(f"    Rule: {result['rule_matched']}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_dataset_parsing()
    sys.exit(0 if success else 1)
