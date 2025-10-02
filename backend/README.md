# Backend README

## URL Attack Detector - Backend

Machine learning and rule-based detection system for URL-based attacks.

### Features

- **Rule-Based Detection**: Fast pattern matching for known attack signatures
- **ML-Based Detection**: Random Forest classifier for novel attack detection
- **PCAP Parsing**: Extract HTTP requests from network captures
- **Log Analysis**: Process HTTP logs in CSV/JSON format
- **Data Export**: Export results to CSV/JSON

### Setup

1. **Install Python 3.8+**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate dataset:**
   ```bash
   python scripts/generate_dataset.py
   ```

4. **Train ML model:**
   ```bash
   python scripts/train_model.py
   ```

5. **Run the server:**
   ```bash
   python app.py
   ```

### API Endpoints

- `POST /api/analyze/pcap` - Analyze PCAP file
- `POST /api/analyze/log` - Analyze HTTP log file
- `GET /api/results/<analysis_id>` - Get analysis results
- `GET /api/export/<analysis_id>/<format>` - Export results
- `GET /api/health` - Health check
- `GET /api/stats` - Detection statistics

### Supported Attacks

1. SQL Injection (SQLi)
2. Cross-Site Scripting (XSS)
3. Command Injection
4. Directory Traversal
5. Local/Remote File Inclusion (LFI/RFI)
6. Server-Side Request Forgery (SSRF)
7. Web Shell Upload
8. Credential Stuffing
9. Typosquatting
10. HTTP Parameter Pollution
11. XML External Entity (XXE)
12. Benign Traffic

### Detection Methods

#### Rule-Based Engine
- 70+ regex patterns
- High precision for known attacks
- Instant detection

#### ML-Based Engine
- Random Forest classifier
- 60+ extracted features
- Novel attack detection

### Dataset Generation

The system includes a dataset generator that creates synthetic attack samples using realistic patterns:

```bash
python scripts/generate_dataset.py
```

This generates:
- `data/train_dataset.csv` - 10,000 samples
- `data/test_dataset.csv` - 2,000 samples

### Model Training

Train the machine learning model on the generated dataset:

```bash
python scripts/train_model.py
```

This creates `models/rf_classifier.pkl` with trained model, label encoder, and feature names.

### Project Structure

```
backend/
├── app.py                  # Flask API server
├── requirements.txt        # Python dependencies
├── detection/
│   ├── detector.py         # Main detector (hybrid)
│   ├── rules_engine.py     # Rule-based detection
│   ├── ml_detector.py      # ML-based detection
│   └── feature_extractor.py # Feature engineering
├── analysis/
│   ├── pcap_parser.py      # PCAP file parser
│   └── log_parser.py       # Log file parser
├── utils/
│   └── export.py           # Export utilities
├── scripts/
│   ├── generate_dataset.py # Dataset generator
│   └── train_model.py      # Model trainer
├── data/                   # Generated datasets
├── models/                 # Trained models
├── uploads/                # Temporary uploads
└── results/                # Export results
```

### Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:5000/api/health

# Analyze PCAP
curl -X POST -F "file=@sample.pcap" http://localhost:5000/api/analyze/pcap

# Export results
curl http://localhost:5000/api/export/<analysis_id>/csv -o results.csv
```

### Performance

- **Rule detection**: < 1ms per URL
- **ML prediction**: ~10ms per URL
- **PCAP parsing**: ~100-500 requests/second
- **Memory usage**: ~200MB (model loaded)

### Requirements

- Python 3.8+
- 2GB RAM minimum
- 100MB disk space for models and data
