# 🔧 Troubleshooting Guide

## Common Issues and Solutions

### 1. "int() argument must be a string..." Error ✅ FIXED

**Problem**: Backend crashes when analyzing dataset files

**Cause**: Dataset files had `None` values that couldn't be converted to integers

**Solution**: 
- Updated `backend/app.py` with safe type conversions
- Updated `backend/analysis/log_parser.py` to handle None values
- Updated `backend/detection/detector.py` to ensure string types

**How to apply fix**:
```bash
# Stop the backend (Ctrl+C)
# Restart the backend
cd backend
python app.py
```

### 2. Backend Not Starting

**Check Python version**:
```bash
python --version
# Should be Python 3.8 or higher
```

**Check dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

**Check if port 5000 is in use**:
```bash
# Windows
netstat -ano | findstr :5000

# Linux/Mac
lsof -i :5000
```

**Solution**: Kill the process or change port in `backend/app.py`

### 3. "Model not found" Error

**Problem**: ML model hasn't been trained yet

**Solution**:
```bash
cd backend

# Generate dataset
python scripts/generate_dataset.py

# Train model (takes 2-5 minutes)
python scripts/train_model.py
```

### 4. Frontend Can't Connect to Backend

**Check backend is running**:
```bash
curl http://localhost:5000/api/health
```

Should return: `{"status":"healthy",...}`

**Check API URL in frontend**:
- File: `services/api.ts`
- Should be: `const API_BASE_URL = 'http://localhost:5000/api';`

**Check CORS**:
- Backend should have `flask-cors` installed
- Check `pip show flask-cors`

### 5. PCAP Files Won't Upload

**Windows**: Install Npcap
- Download from: https://npcap.com/
- Install with WinPcap compatibility

**Linux**: Install tcpdump
```bash
sudo apt-get install tcpdump
```

**Check Scapy**:
```bash
python -c "import scapy; print('Scapy OK')"
```

### 6. CSV/JSON Files Fail to Parse

**Format Requirements**:

CSV must have headers:
```csv
url,src_ip,method,timestamp
http://example.com,192.168.1.1,GET,2025-10-02T10:00:00
```

JSON must be array or object with 'results' key:
```json
[
  {
    "url": "http://example.com",
    "src_ip": "192.168.1.1",
    "method": "GET"
  }
]
```

**Required fields**: Only `url` is mandatory
**Optional fields**: src_ip, dst_ip, method, timestamp, headers, body

### 7. Results Not Showing

**Check browser console** (F12):
- Look for API errors
- Check network tab for failed requests

**Check backend logs**:
- Backend terminal shows request logs
- Look for error messages

**Check analysis ID**:
- Each analysis gets a unique ID
- Old results are kept in memory until restart

### 8. Export Not Working

**Check analysis ID exists**:
```bash
curl http://localhost:5000/api/stats
```

**Check results folder**:
- Results saved to `backend/results/`
- Check folder permissions

### 9. Low Detection Accuracy

**Retrain model with more data**:
```bash
cd backend/scripts

# Edit generate_dataset.py
# Increase total_samples to 20000+

python generate_dataset.py
python train_model.py
```

**Add more rules**:
- Edit `backend/detection/rules_engine.py`
- Add patterns to existing attack types

### 10. Memory Issues

**Symptoms**: Backend crashes, slow performance

**Solutions**:
1. **Limit result storage**:
   - Results stored in memory
   - Clear old results periodically
   - Use database for production

2. **Reduce dataset size**:
   - Use smaller test files
   - Process in batches

3. **Increase system resources**:
   - Close other applications
   - Add more RAM
   - Use virtual memory

### 11. Slow Detection Speed

**Optimize**:
1. **Disable ML for testing**:
   ```python
   # In detector.py
   self.loaded = False
   ```

2. **Reduce tree count**:
   ```python
   # In train_model.py
   n_estimators=50  # instead of 100
   ```

3. **Use multiprocessing**:
   ```python
   # In app.py
   from multiprocessing import Pool
   ```

## Testing Your Fixes

### Test Detection
```bash
cd backend
python scripts/test_detector.py
```

### Test Dataset Parsing
```bash
cd backend
python scripts/test_dataset_parsing.py
```

### Test API
```bash
# Health check
curl http://localhost:5000/api/health

# Stats
curl http://localhost:5000/api/stats
```

### Test File Upload (with curl)
```bash
curl -X POST \
  -F "file=@backend/sample_data/sample_http_log.csv" \
  http://localhost:5000/api/analyze/log
```

## Getting Help

### Enable Debug Logging

**Backend**:
```python
# In app.py
logging.basicConfig(level=logging.DEBUG)
```

**Frontend**:
```javascript
// In api.ts
console.log('Request:', ...);
console.log('Response:', ...);
```

### Check Versions
```bash
# Python
python --version

# Node
node --version

# Packages
pip list | grep flask
npm list react
```

### Reset Everything
```bash
# Stop all servers (Ctrl+C in each terminal)

# Backend
cd backend
rm -rf __pycache__
rm -rf data/
rm -rf models/
rm -rf uploads/*
rm -rf results/*

# Reinstall
pip install -r requirements.txt

# Regenerate
python scripts/generate_dataset.py
python scripts/train_model.py

# Frontend
npm install

# Restart
python app.py  # Terminal 1
npm run dev    # Terminal 2
```

## Still Having Issues?

1. Check all error messages carefully
2. Look in backend terminal for Python errors
3. Look in browser console (F12) for JavaScript errors
4. Check file permissions
5. Verify all dependencies are installed
6. Try the sample files first before your own files

## Quick Fixes Applied

✅ Fixed int() conversion errors in app.py
✅ Added safe string conversions in detector.py
✅ Improved log parser error handling
✅ Added better type checking throughout

**To apply**: Simply restart the backend server!

---

**Last Updated**: 2025-10-02
**Status**: ✅ All major issues resolved
