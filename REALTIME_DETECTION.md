# 📡 Real-Time Threat Detection Implementation Guide

## Current Status: MOCK/SIMULATED ⚠️

Right now, the live threat notifications you see are **simulated/fake** data from `services/realtime.ts`:

```typescript
// Current: Mock service generates fake alerts every 7 seconds
intervalId = window.setInterval(() => {
  if (Math.random() < 0.25) {
    let result = generateMockResult(); // ← FAKE DATA
    onAlert(result);
  }
}, 7000);
```

**These are NOT real detections!** They're just for demonstration purposes.

---

## Making It Real: Two Options

### Option 1: Server-Sent Events (SSE) ⭐ **RECOMMENDED**

Real-time streaming from backend to frontend.

#### Step 1: Add SSE Endpoint to Backend

Add this to `backend/app.py`:

```python
from flask import Response, stream_with_context
import queue
import threading

# Global queue for real-time alerts
realtime_queue = queue.Queue(maxsize=100)

@app.route('/api/stream/alerts')
def stream_alerts():
    """Server-Sent Events endpoint for real-time alerts"""
    def generate():
        # Send connection acknowledgment
        yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        while True:
            try:
                # Wait for new detection
                detection = realtime_queue.get(timeout=30)
                yield f"data: {json.dumps(detection)}\n\n"
            except queue.Empty:
                # Send keepalive every 30 seconds
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
    """Broadcast detection to all connected clients"""
    high_severity = ['SQLi', 'CMD Injection', 'Web Shell', 'Directory Traversal', 'SSRF', 'XXE']
    
    if detection_result['attack_prediction'] in high_severity:
        try:
            realtime_queue.put(detection_result, block=False)
            logger.info(f"Broadcasting alert: {detection_result['attack_prediction']}")
        except queue.Full:
            logger.warning("Alert queue full, dropping oldest")
            # Clear old alerts and add new one
            while not realtime_queue.empty():
                try:
                    realtime_queue.get_nowait()
                except queue.Empty:
                    break
            realtime_queue.put(detection_result, block=False)
```

#### Step 2: Broadcast Detections During Analysis

Modify `analyze_log()` and `analyze_pcap()` in `backend/app.py`:

```python
@app.route('/api/analyze/log', methods=['POST'])
def analyze_log():
    # ... existing code ...
    
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
        
        # ⭐ BROADCAST HIGH-SEVERITY ATTACKS IN REAL-TIME
        broadcast_detection(detection_result)
    
    # ... rest of code ...
```

#### Step 3: Update Frontend to Use Real SSE

Replace `services/realtime.ts` with:

```typescript
import type { DetectionResult } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

export const realtimeService = {
  connect: (onAlert: (result: DetectionResult) => void): (() => void) => {
    console.log('🔌 Connecting to real-time backend stream...');
    
    let eventSource: EventSource | null = null;
    let reconnectTimeout: number | null = null;
    
    const connect = () => {
      try {
        eventSource = new EventSource(`${API_BASE_URL}/stream/alerts`);
        
        eventSource.onopen = () => {
          console.log('✅ Real-time stream connected');
        };
        
        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'connected') {
              console.log('Backend ready for alerts');
              return;
            }
            
            // Received real attack detection!
            console.log('🚨 Real attack detected:', data);
            onAlert(data as DetectionResult);
            
          } catch (error) {
            console.error('Error parsing alert:', error);
          }
        };
        
        eventSource.onerror = (error) => {
          console.error('❌ Stream error:', error);
          eventSource?.close();
          
          // Auto-reconnect after 5 seconds
          reconnectTimeout = window.setTimeout(() => {
            console.log('🔄 Reconnecting...');
            connect();
          }, 5000);
        };
        
      } catch (error) {
        console.error('Failed to create stream:', error);
      }
    };
    
    connect();
    
    // Return disconnect function
    const disconnect = () => {
      if (eventSource) {
        eventSource.close();
        eventSource = null;
      }
      if (reconnectTimeout) {
        clearTimeout(reconnectTimeout);
        reconnectTimeout = null;
      }
      console.log('🔌 Real-time stream disconnected');
    };
    
    return disconnect;
  },
};
```

---

### Option 2: WebSocket 🔌 **Alternative**

For bidirectional communication (if needed).

#### Step 1: Install flask-socketio

```bash
cd backend
pip install flask-socketio python-socketio
```

#### Step 2: Add WebSocket Support

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected to WebSocket')
    emit('connected', {'status': 'ready'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected from WebSocket')

def broadcast_detection_ws(detection_result):
    """Broadcast via WebSocket"""
    high_severity = ['SQLi', 'CMD Injection', 'Web Shell', 'Directory Traversal', 'SSRF']
    
    if detection_result['attack_prediction'] in high_severity:
        socketio.emit('alert', detection_result)

# Run with socketio
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
```

#### Step 3: Update Frontend for WebSocket

```typescript
import { io, Socket } from 'socket.io-client';

export const realtimeService = {
  connect: (onAlert: (result: DetectionResult) => void): (() => void) => {
    const socket: Socket = io('http://localhost:5000');
    
    socket.on('connect', () => {
      console.log('✅ WebSocket connected');
    });
    
    socket.on('alert', (data) => {
      console.log('🚨 Real attack detected:', data);
      onAlert(data as DetectionResult);
    });
    
    socket.on('disconnect', () => {
      console.log('🔌 WebSocket disconnected');
    });
    
    return () => {
      socket.disconnect();
    };
  },
};
```

---

## Quick Implementation (SSE - 5 Minutes)

### 1. Add to `backend/app.py` (at the top with imports):

```python
from flask import Response, stream_with_context
import queue

realtime_queue = queue.Queue(maxsize=100)
```

### 2. Add these functions to `backend/app.py` (before `if __name__`):

```python
@app.route('/api/stream/alerts')
def stream_alerts():
    def generate():
        yield f"data: {json.dumps({'type': 'connected'})}\n\n"
        while True:
            try:
                detection = realtime_queue.get(timeout=30)
                yield f"data: {json.dumps(detection)}\n\n"
            except queue.Empty:
                yield f": keepalive\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive'}
    )

def broadcast_detection(detection_result):
    high_severity = ['SQLi', 'CMD Injection', 'Web Shell', 'Directory Traversal', 'SSRF', 'XXE']
    if detection_result['attack_prediction'] in high_severity:
        try:
            realtime_queue.put(detection_result, block=False)
        except queue.Full:
            pass
```

### 3. Add to `analyze_log()` function (after creating detection_result):

```python
broadcast_detection(detection_result)  # Add this line
```

### 4. Replace `services/realtime.ts`:

```typescript
import type { DetectionResult } from '../types';

const API_BASE_URL = 'http://localhost:5000/api';

export const realtimeService = {
  connect: (onAlert: (result: DetectionResult) => void): (() => void) => {
    const eventSource = new EventSource(`${API_BASE_URL}/stream/alerts`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type !== 'connected') {
        onAlert(data as DetectionResult);
      }
    };
    
    return () => eventSource.close();
  },
};
```

### 5. Restart Backend

```bash
# Stop (Ctrl+C)
python app.py
```

---

## Testing Real-Time Alerts

1. **Start backend**: `python app.py`
2. **Start frontend**: `npm run dev`
3. **Upload a file** with attacks (e.g., `test_dataset.csv`)
4. **Watch for alerts** as each high-severity attack is detected!

---

## Comparison

| Feature | SSE | WebSocket | Mock (Current) |
|---------|-----|-----------|----------------|
| Real-time | ✅ | ✅ | ❌ |
| Setup Complexity | ⭐ Easy | ⭐⭐ Medium | ⭐ Very Easy |
| Browser Support | ✅ All modern | ✅ All modern | ✅ All |
| Server Load | Low | Medium | None |
| Bidirectional | ❌ | ✅ | ❌ |
| Auto Reconnect | ✅ Built-in | Manual | N/A |
| Production Ready | ✅ | ✅ | ❌ |

---

## Current Mock Behavior

**Location**: `services/realtime.ts`

**What it does**:
- Generates fake attacks every 7 seconds
- 25% chance of triggering
- Only shows high-severity attacks
- Data is completely random

**To disable mock alerts**:
Comment out the useEffect in `App.tsx`:

```typescript
// Effect for real-time alerts
useEffect(() => {
  // let disconnect: (() => void) | undefined;
  
  // if (analysisId) {
  //   disconnect = realtimeService.connect(addAlert);
  // }

  // return () => {
  //   if (disconnect) {
  //     disconnect();
  //   }
  // };
}, [analysisId, addAlert]);
```

---

## Recommendation

**For SIH Demo**: Keep the mock (current) - it shows the feature without complexity

**For Production**: Use SSE (Option 1) - easy to implement, reliable, and efficient

---

## Summary

🔴 **Current**: Mock alerts (fake data, demonstrates UI)  
🟢 **Recommended**: SSE implementation (real detections, 5-minute setup)  
🟡 **Advanced**: WebSocket (bidirectional, more complex)

Choose based on your needs! For the hackathon demo, the current mock is fine. For real deployment, implement SSE.
