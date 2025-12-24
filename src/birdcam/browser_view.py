from flask import Flask, Response, render_template_string, request, abort
import cv2

app = Flask(__name__)

# Set camera indices (change if needed)
USB_INDEX = 0
INTERNAL_INDEX = 1

# Desired displayed size (CSS) — change as needed
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 360

HTML = f"""
<!doctype html>
<title>Two Cameras Side-by-Side</title>
<style>
  body {{ font-family: Arial, sans-serif; margin: 16px; }}
  .row {{ display: flex; gap: 12px; align-items: flex-start; }}
  .cam-box {{ flex: 0 0 auto; text-align: center; }}
  .cam-box img {{
    width: {DISPLAY_WIDTH}px;
    height: {DISPLAY_HEIGHT}px;
    object-fit: contain;
    border: 1px solid #ccc;
    background: #000;
  }}
  h2 {{ margin: 8px 0 6px; font-size: 16px; }}
</style>
<h1>Camera Feeds</h1>
<div class="row">
  <div class="cam-box">
    <h2>USB Camera (index {USB_INDEX})</h2>
    <img src="{{{{ url_for('video_feed') }}}}?cam=usb" alt="USB camera">
  </div>
  <div class="cam-box">
    <h2>Internal Camera (index {INTERNAL_INDEX})</h2>
    <img src="{{{{ url_for('video_feed') }}}}?cam=internal" alt="Internal camera">
  </div>
</div>
"""

def gen_frames(index):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        return
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # Optionally resize frame server-side to reduce bandwidth:
            # frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            ret2, buf = cv2.imencode('.jpg', frame)
            if not ret2:
                continue
            frame_bytes = buf.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cap.release()

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video_feed')
def video_feed():
    cam = request.args.get('cam', '')
    if cam == 'usb':
        idx = USB_INDEX
    elif cam == 'internal':
        idx = INTERNAL_INDEX
    else:
        return abort(404)
    return Response(gen_frames(idx),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
