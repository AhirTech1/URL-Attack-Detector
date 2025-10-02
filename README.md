# URL Attack Detector

**Smart India Hackathon - Cybersecurity Solution**

A comprehensive web-based system for detecting and analyzing URL-based cyber attacks using hybrid rule-based and machine learning approaches.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-blue)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-19-blue)](https://reactjs.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green)](https://flask.palletsprojects.com/)

## 🎯 Problem Statement

HTTP is one of the most exploited protocols by cyber threat actors. This system identifies various types of cyber-attacks carried out by exploiting the URL field of HTTP protocol, including:

- ✅ SQL Injection (Multiple types)
- ✅ Cross-Site Scripting (XSS)
- ✅ Command Injection
- ✅ Directory Traversal
- ✅ Server-Side Request Forgery (SSRF)
- ✅ Local/Remote File Inclusion (LFI/RFI)
- ✅ Web Shell Uploads
- ✅ Credential Stuffing / Brute Force
- ✅ Typosquatting / URL Spoofing
- ✅ HTTP Parameter Pollution
- ✅ XML External Entity Injection (XXE)

## 🌟 Features

### Detection Capabilities
- **Hybrid Detection**: Combines rule-based (70+ patterns) and ML-based (Random Forest) detection
- **Real-time Analysis**: Process network traffic in real-time
- **PCAP Support**: Analyze network captures directly
- **Log Analysis**: Process HTTP logs (CSV/JSON format)
- **High Accuracy**: 95%+ detection rate with low false positives

### Visualization & Reporting
- **Interactive Dashboard**: Real-time results visualization
- **Attack Analytics**: Pie charts, bar graphs, and timeline analysis
- **Advanced Filtering**: Filter by IP, attack type, confidence level
- **Data Export**: Export results to CSV/JSON formats
- **Real-time Alerts**: Live notifications for critical attacks

## 🏗️ Architecture

```
┌─────────────────┐
│   Frontend      │
│  React + TS     │
└────────┬────────┘
         │ REST API
┌────────▼────────┐
│   Flask API     │
└────────┬────────┘
         │
    ┌────┴─────┬──────────────┬────────────┐
    │          │              │            │
┌───▼───┐  ┌──▼───┐  ┌──────▼──────┐  ┌──▼──────┐
│ PCAP  │  │ Log  │  │   Rules     │  │   ML    │
│Parser │  │Parser│  │   Engine    │  │ Model   │
└───────┘  └──────┘  └─────────────┘  └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ 
- **Python** 3.8+
- **Git**

### Installation

#### 1. Clone the repository
```bash
git clone https://github.com/AhirTech1/URL-Attack-Detector.git
cd URL-Attack-Detector
```

#### 2. Setup Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Generate training dataset
python scripts/generate_dataset.py

# Train ML model (takes 2-5 minutes)
python scripts/train_model.py

# Run the Flask server
python app.py
```

Backend will run on `http://localhost:5000`

#### 3. Setup Frontend

```bash
# From project root
npm install

# Run development server
npm run dev
```

Frontend will run on `http://localhost:5173`

#### 4. Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## 📖 Usage

### Analyzing PCAP Files

1. Click **"Analyze PCAP"** tab
2. Upload a `.pcap` or `.pcapng` file
3. Wait for analysis to complete
4. View results in the interactive dashboard

### Analyzing HTTP Logs

1. Click **"Analyze HTTP Log"** tab
2. Upload a `.csv` or `.json` log file
3. View detection results with confidence scores

### Filtering Results

- **By IP Address**: Filter attacks from specific source IPs
- **By Attack Type**: View specific attack categories
- **By Confidence**: Show only high-confidence detections (e.g., >80%)

### Exporting Data

- Click **"Export CSV"** or **"Export JSON"**
- Download complete analysis results

## 🔬 Detection Methods

### Rule-Based Engine

**Fast & Precise** - 70+ regex patterns for known attack signatures

Example SQLi detection:
```python
{
    'name': 'SQL_UNION_SELECT',
    'pattern': r'union[\s]+select',
    'confidence': 0.95
}
```

### Machine Learning Engine

**Adaptive & Smart** - Random Forest classifier with 60+ features

Features extracted:
- URL length and structure
- Special character counts
- Entropy (randomness measure)
- Suspicious keywords
- Encoding indicators

## 📊 Dataset

The system includes a synthetic dataset generator that creates realistic attack samples:

- **Training Set**: 10,000 samples
- **Test Set**: 2,000 samples
- **Attack Distribution**: 30% attacks, 70% benign
- **Attack Variety**: 11 different attack types

## 🧪 Testing

### Test the Detector
```bash
cd backend
python scripts/test_detector.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# Stats
curl http://localhost:5000/api/stats
```

## 📁 Project Structure

```
URL-Attack-Detector/
├── backend/                    # Python Flask backend
│   ├── app.py                  # Main API server
│   ├── detection/              # Detection engines
│   │   ├── detector.py         # Hybrid detector
│   │   ├── rules_engine.py     # Rule-based detection
│   │   ├── ml_detector.py      # ML classifier
│   │   └── feature_extractor.py # Feature engineering
│   ├── analysis/               # File parsers
│   │   ├── pcap_parser.py      # PCAP parser
│   │   └── log_parser.py       # Log parser
│   ├── scripts/                # Utilities
│   │   ├── generate_dataset.py # Dataset generator
│   │   ├── train_model.py      # Model trainer
│   │   └── test_detector.py    # Testing script
│   ├── data/                   # Generated datasets
│   ├── models/                 # Trained ML models
│   └── requirements.txt        # Python dependencies
│
├── src/                        # Frontend source
│   ├── components/             # React components
│   │   ├── Dashboard.tsx       # Main dashboard
│   │   ├── FileUpload.tsx      # File upload
│   │   ├── ResultsTable.tsx    # Results display
│   │   └── charts/             # Visualizations
│   ├── services/               # API services
│   │   ├── api.ts              # API client
│   │   └── realtime.ts         # Real-time alerts
│   └── types.ts                # TypeScript types
│
├── package.json                # Node dependencies
├── tsconfig.json               # TypeScript config
└── README.md                   # This file
```

## 🎓 Technical Details

### Backend Stack
- **Framework**: Flask 3.0
- **ML Library**: scikit-learn 1.3
- **Network Analysis**: Scapy 2.5
- **Data Processing**: Pandas, NumPy

### Frontend Stack
- **Framework**: React 19
- **Language**: TypeScript 5.8
- **Build Tool**: Vite 6
- **Charts**: Recharts 3.2

### ML Model
- **Algorithm**: Random Forest Classifier
- **Features**: 60+ engineered features
- **Training Time**: ~2-5 minutes
- **Accuracy**: 95%+ on test set
- **Model Size**: ~10MB

## 📈 Performance

- **Rule Detection**: < 1ms per URL
- **ML Prediction**: ~10ms per URL  
- **PCAP Parsing**: 100-500 requests/second
- **Memory Usage**: ~200MB (with model loaded)
- **Concurrent Analyses**: Supports multiple simultaneous analyses

## 🛡️ Security Considerations

- File uploads are validated and sanitized
- Temporary files are cleaned up after processing
- API endpoints include error handling
- No sensitive data is stored permanently
- Results are kept in memory (use DB for production)

## 🔮 Future Enhancements

- [ ] Deep Learning models (LSTM, Transformer)
- [ ] Real-time PCAP streaming
- [ ] Database integration for result persistence
- [ ] User authentication and multi-tenancy
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] Integration with SIEM systems
- [ ] Mobile app support

## 🤝 Contributing

This project was developed for Smart India Hackathon. Contributions are welcome!

## 📄 License

This project is open source and available under the MIT License.

## 👥 Team

**AhirTech1** - [GitHub Profile](https://github.com/AhirTech1)

## 🙏 Acknowledgments

- Smart India Hackathon for the problem statement
- scikit-learn for ML capabilities
- Scapy for network analysis
- React team for the excellent framework

---

**Built with ❤️ for Smart India Hackathon 2025**
