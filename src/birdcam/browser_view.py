from flask import Flask, Response, render_template_string, request, abort
import cv2
import time

app = Flask(__name__)

# Sources
USB_INDEX = 0
USB2_INDEX = 1
RTSP_URL = "rtsp://192.168.1.222:8554/main"

# Display size (CSS)
DISPLAY_WIDTH = 480
DISPLAY_HEIGHT = 360

HTML = f"""
<!doctype html>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --columns: 2;
    --gap: 12px;
    --box-aspect: 16 / 9;
    --max-grid-width: 1200px;
  }}
  body {{ font-family: Arial, sans-serif; margin: 12px; display:flex; justify-content:center; }}
  .container {{ width: 100%; max-width: var(--max-grid-width); }}
  .grid {{
    display: grid;
    gap: var(--gap);
    grid-template-columns: 1fr;
    align-items: start;
  }}
  @media (min-width: 700px) {{
    .grid {{ grid-template-columns: repeat(var(--columns), 1fr); }}
  }}
  .cam-box {{
    box-sizing: border-box;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .cam-frame {{
    width: 100%;
    aspect-ratio: var(--box-aspect);
    background: #000;
    border: 1px solid #ccc;
    overflow: hidden;
    position: relative;
  }}
  .cam-frame img {{
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }}
  .cam-box h2 {{ margin: 0; font-size: 14px; text-align: center; }}

  .center-wrapper {{
    display: flex;
    justify-content: center;
  }}
  .center-inner {{
    width: 100%;
    max-width: 100%;
  }}

  @media (min-width: 700px) {{
    .cam-box.rtsp {{
      grid-column: 1 / -1;
    }}
    .center-inner {{
      max-width: calc((100% - var(--gap) * (var(--columns) - 1)) / var(--columns));
    }}
  }}
</style>

<div class="container">
  <div class="grid">
    <div class="cam-box">
      <h2>USB1</h2>
      <div class="cam-frame">
        <img src="{{{{ url_for('video_feed') }}}}?cam=usb1" alt="USB camera 1">
      </div>
    </div>

    <div class="cam-box">
      <h2>USB2</h2>
      <div class="cam-frame">
        <img src="{{{{ url_for('video_feed') }}}}?cam=usb2" alt="USB camera 2">
      </div>
    </div>

    <div class="cam-box rtsp">
      <div class="center-wrapper">
        <div class="center-inner">
          <h2>RTSP1</h2>
          <div class="cam-frame">
            <img src="{{{{ url_for('video_feed') }}}}?cam=rtsp" alt="RTSP camera">
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
"""


def open_capture(source):
    # source: int index or rtsp url string
    if isinstance(source, str):
        cap = cv2.VideoCapture(source)
    else:
        cap = cv2.VideoCapture(int(source))
    return cap

def gen_frames(source, reconnect_delay=2, max_retries=5):
    retries = 0
    cap = open_capture(source)
    try:
        while True:
            if not cap.isOpened():
                # attempt reconnect
                cap.release()
                retries += 1
                if retries > max_retries:
                    break
                time.sleep(reconnect_delay)
                cap = open_capture(source)
                continue
            ret, frame = cap.read()
            if not ret:
                # try reconnect on failure
                cap.release()
                retries += 1
                if retries > max_retries:
                    break
                time.sleep(reconnect_delay)
                cap = open_capture(source)
                continue
            retries = 0
            # Optional server-side resize:
            # frame = cv2.resize(frame, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            ret2, buf = cv2.imencode('.jpg', frame)
            if not ret2:
                continue
            frame_bytes = buf.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        if 'cap' in locals() and cap is not None:
            cap.release()

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/video_feed')
def video_feed():
    cam = request.args.get('cam', '')
    if cam == 'usb1':
        source = USB_INDEX
    elif cam == 'usb2':
        source = USB2_INDEX
    elif cam == 'rtsp':
        source = RTSP_URL
    else:
        return abort(404)
    return Response(gen_frames(source),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
