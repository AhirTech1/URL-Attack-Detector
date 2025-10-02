"""
Real-time attack detection stream using Server-Sent Events (SSE)
Add this to your Flask backend
"""
from flask import Response, stream_with_context
import json
import time
import queue
import threading

# Global queue for real-time detections
realtime_queue = queue.Queue()

@app.route('/api/stream/alerts')
def stream_alerts():
    """
    Server-Sent Events endpoint for real-time attack alerts
    """
    def generate():
        # Send initial connection message
        yield f"data: {json.dumps({'type': 'connected'})}\n\n"
        
        while True:
            try:
                # Wait for new detection with timeout
                detection = realtime_queue.get(timeout=30)
                
                # Only send high-severity attacks
                high_severity = ['SQLi', 'CMD Injection', 'Web Shell', 'Directory Traversal', 'SSRF']
                if detection['attack_prediction'] in high_severity:
                    yield f"data: {json.dumps(detection)}\n\n"
                
            except queue.Empty:
                # Send keepalive ping every 30 seconds
                yield f": keepalive\n\n"
            except GeneratorExit:
                break
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

def broadcast_detection(detection_result):
    """
    Broadcast a detection to all connected clients
    Call this from your detection code
    """
    try:
        realtime_queue.put(detection_result, block=False)
    except queue.Full:
        pass

# Modify your analyze_log and analyze_pcap to broadcast detections
# Example in analyze_log():
def analyze_log():
    # ... existing code ...
    for idx, entry in enumerate(log_entries):
        detection_result = detector.analyze_request(...)
        detection_result['id'] = idx + 1
        results.append(detection_result)
        
        # Broadcast high-severity attacks in real-time
        high_severity = ['SQLi', 'CMD Injection', 'Web Shell', 'Directory Traversal', 'SSRF']
        if detection_result['attack_prediction'] in high_severity:
            broadcast_detection(detection_result)
    # ... rest of code ...
