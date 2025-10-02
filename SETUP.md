## 🚀 SETUP INSTRUCTIONS

### Quick Setup (Automated)

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Install Python dependencies
2. Generate 10,000 training samples
3. Train the ML model
4. Create sample test files

### Manual Setup

#### Backend Setup

1. **Install Python dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Generate dataset:**
```bash
python scripts/generate_dataset.py
```

Output:
- `backend/data/train_dataset.csv` (10,000 samples)
- `backend/data/test_dataset.csv` (2,000 samples)

3. **Train ML model:**
```bash
python scripts/train_model.py
```

This will:
- Extract features from all URLs
- Train Random Forest classifier
- Evaluate on validation set
- Save model to `backend/models/rf_classifier.pkl`

Expected accuracy: **95%+**

4. **Generate sample test files (optional):**
```bash
python scripts/generate_sample_logs.py
```

Creates sample HTTP logs in `backend/sample_data/`

5. **Run the backend server:**
```bash
python app.py
```

Server runs on `http://localhost:5000`

#### Frontend Setup

1. **Install Node.js dependencies:**
```bash
npm install
```

2. **Run development server:**
```bash
npm run dev
```

Frontend runs on `http://localhost:5173`

### Verify Installation

#### Test the detector:
```bash
cd backend
python scripts/test_detector.py
```

Expected output:
```
Testing URL Attack Detector
================================================================================

✓ URL: http://example.com/products?category=electronics
  Expected: Benign
  Detected: Benign (confidence: 15.00%)

✓ URL: http://site.com/login?user=' OR '1'='1
  Expected: SQLi
  Detected: SQLi (confidence: 90.00%)
  Rule: SQL_OR_INJECTION

...

Accuracy: 12/12 (100.0%)
```

#### Test the API:
```bash
# Health check
curl http://localhost:5000/api/health

# Should return:
# {"status":"healthy","timestamp":"...","detector_loaded":true}
```

### Using the Application

1. **Open browser** to `http://localhost:5173`

2. **Upload a file:**
   - Click "Analyze PCAP" for `.pcap` files
   - Click "Analyze HTTP Log" for `.csv` or `.json` files
   - Sample files are in `backend/sample_data/`

3. **View results:**
   - Dashboard shows all detections
   - Filter by IP, attack type, confidence
   - View charts and statistics
   - Export to CSV/JSON

### Troubleshooting

#### "Model not found" error:
```bash
cd backend
python scripts/train_model.py
```

#### "Scapy not available" warning:
- Windows: May need to install Npcap from https://npcap.com/
- Linux: `sudo apt-get install tcpdump`

#### Backend won't start:
```bash
# Check if port 5000 is available
netstat -ano | findstr :5000  # Windows
lsof -i :5000                  # Linux/Mac
```

#### Frontend won't connect:
- Check `services/api.ts` has correct API URL
- Ensure backend is running on port 5000
- Check browser console for CORS errors

### Development

#### Add new attack patterns:
Edit `backend/detection/rules_engine.py`

#### Retrain with more data:
1. Edit `backend/scripts/generate_dataset.py`
2. Increase `total_samples` parameter
3. Run `python scripts/train_model.py`

#### Modify features:
Edit `backend/detection/feature_extractor.py`

### Production Deployment

For production use:

1. **Use a database** instead of in-memory storage
2. **Add authentication** (JWT tokens)
3. **Enable HTTPS**
4. **Use Gunicorn** for Flask:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
5. **Build frontend:**
   ```bash
   npm run build
   ```
6. **Use nginx** to serve frontend and proxy API

### System Requirements

**Minimum:**
- 2GB RAM
- 2 CPU cores
- 500MB disk space

**Recommended:**
- 4GB+ RAM
- 4+ CPU cores
- 1GB+ disk space

### Performance Tips

- Increase `n_estimators` in Random Forest for better accuracy
- Use `n_jobs=-1` to use all CPU cores
- Cache PCAP parsing results
- Use database for large-scale deployment
- Consider using Redis for session management
