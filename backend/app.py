from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import logging
from datetime import datetime
from pathlib import Path

from detection.detector import URLAttackDetector
from analysis.pcap_parser import PCAPParser
from analysis.log_parser import LogParser
from utils.export import DataExporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = Path('uploads')
RESULTS_FOLDER = Path('results')
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Initialize detector
detector = URLAttackDetector()
pcap_parser = PCAPParser()
log_parser = LogParser()
exporter = DataExporter()

# Store results in memory (in production, use a database)
analysis_results = {}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'detector_loaded': detector.is_loaded()
    })

@app.route('/api/analyze/pcap', methods=['POST'])
def analyze_pcap():
    """Analyze PCAP file for URL-based attacks"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith(('.pcap', '.pcapng')):
            return jsonify({'error': 'Invalid file format. Only .pcap and .pcapng files are supported'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        logger.info(f"Processing PCAP file: {filename}")
        
        # Parse PCAP to extract HTTP requests
        http_requests = pcap_parser.parse(filepath)
        logger.info(f"Extracted {len(http_requests)} HTTP requests from PCAP")
        
        # Analyze each request
        results = []
        for idx, req in enumerate(http_requests):
            detection_result = detector.analyze_request(
                url=req['url'],
                src_ip=req.get('src_ip', 'unknown'),
                dst_ip=req.get('dst_ip', 'unknown'),
                timestamp=req.get('timestamp', datetime.now().isoformat()),
                method=req.get('method', 'GET'),
                headers=req.get('headers', {}),
                body=req.get('body', '')
            )
            detection_result['id'] = idx + 1
            results.append(detection_result)
        
        # Store results
        analysis_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_results[analysis_id] = results
        
        # Clean up uploaded file
        filepath.unlink()
        
        return jsonify({
            'analysis_id': analysis_id,
            'count': len(results),
            'results': results[:20]  # Return first 20 for preview
        })
    
    except Exception as e:
        logger.error(f"Error analyzing PCAP: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/log', methods=['POST'])
def analyze_log():
    """Analyze HTTP log file (CSV/JSON) for URL-based attacks"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.endswith(('.csv', '.json')):
            return jsonify({'error': 'Invalid file format. Only .csv and .json files are supported'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        logger.info(f"Processing log file: {filename}")
        
        # Parse log file
        log_entries = log_parser.parse(filepath)
        logger.info(f"Extracted {len(log_entries)} log entries")
        
        # Analyze each entry
        results = []
        for idx, entry in enumerate(log_entries):
            detection_result = detector.analyze_request(
                url=entry['url'],
                src_ip=entry.get('src_ip', 'unknown'),
                dst_ip=entry.get('dst_ip', 'unknown'),
                timestamp=entry.get('timestamp', datetime.now().isoformat()),
                method=entry.get('method', 'GET'),
                headers=entry.get('headers', {}),
                body=entry.get('body', '')
            )
            detection_result['id'] = idx + 1
            results.append(detection_result)
        
        # Store results
        analysis_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        analysis_results[analysis_id] = results
        
        # Clean up uploaded file
        filepath.unlink()
        
        return jsonify({
            'analysis_id': analysis_id,
            'count': len(results),
            'results': results[:20]
        })
    
    except Exception as e:
        logger.error(f"Error analyzing log: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/results/<analysis_id>', methods=['GET'])
def get_results(analysis_id):
    """Get analysis results with filtering"""
    try:
        if analysis_id not in analysis_results:
            return jsonify({'error': 'Analysis not found'}), 404
        
        results = analysis_results[analysis_id]
        
        # Apply filters with safe conversions
        ip_filter = request.args.get('ip', '')
        attack_type = request.args.get('attack_type', 'All')
        
        confidence_str = request.args.get('confidence', '0')
        try:
            confidence = float(confidence_str) if confidence_str else 0
        except (ValueError, TypeError):
            confidence = 0
        
        offset_str = request.args.get('offset', '0')
        try:
            offset = int(offset_str) if offset_str else 0
        except (ValueError, TypeError):
            offset = 0
        
        limit_str = request.args.get('limit', '20')
        try:
            limit = int(limit_str) if limit_str else 20
        except (ValueError, TypeError):
            limit = 20
        
        filtered = results
        if ip_filter:
            filtered = [r for r in filtered if ip_filter in r.get('src_ip', '')]
        if attack_type and attack_type != 'All':
            filtered = [r for r in filtered if r.get('attack_prediction') == attack_type]
        if confidence > 0:
            filtered = [r for r in filtered if r.get('confidence', 0) * 100 >= confidence]
        
        return jsonify({
            'count': len(filtered),
            'results': filtered[offset:offset + limit]
        })
    
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/<analysis_id>/<format>', methods=['GET'])
def export_results(analysis_id, format):
    """Export analysis results to CSV or JSON"""
    try:
        if analysis_id not in analysis_results:
            return jsonify({'error': 'Analysis not found'}), 404
        
        results = analysis_results[analysis_id]
        
        if format == 'csv':
            filepath = exporter.to_csv(results, RESULTS_FOLDER / f'{analysis_id}.csv')
            return send_file(filepath, as_attachment=True, download_name=f'analysis_{analysis_id}.csv')
        elif format == 'json':
            filepath = exporter.to_json(results, RESULTS_FOLDER / f'{analysis_id}.json')
            return send_file(filepath, as_attachment=True, download_name=f'analysis_{analysis_id}.json')
        else:
            return jsonify({'error': 'Invalid format. Use csv or json'}), 400
    
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get detection statistics"""
    return jsonify({
        'total_analyses': len(analysis_results),
        'detector_version': detector.get_version(),
        'supported_attacks': detector.get_supported_attacks()
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
