import os
import sys
import cv2
import base64
import threading
import time
import atexit
import uuid
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from ultralytics import YOLO
from dotenv import load_dotenv
import httpx

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'atm_security_secret'

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Use threading mode (works on all Python versions)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading',
                    logger=False, engineio_logger=False)

# ── Supabase helpers (each creates a short-lived client to avoid eventlet issues) ──
def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

def sb_get(path, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{path}{('?' + params) if params else ''}"
    with httpx.Client(timeout=5.0) as c:
        r = c.get(url, headers=_headers())
        if not r.is_success:
            print(f"[SB GET] {path} → {r.status_code}: {r.text[:200]}")
        return r

def sb_post(path, data):
    with httpx.Client(timeout=5.0) as c:
        r = c.post(f"{SUPABASE_URL}/rest/v1/{path}", json=data, headers=_headers())
        if not r.is_success:
            print(f"[SB POST] {path} → {r.status_code}: {r.text[:200]}")
        return r

def sb_patch(path, query, data):
    with httpx.Client(timeout=5.0) as c:
        r = c.patch(f"{SUPABASE_URL}/rest/v1/{path}?{query}", json=data, headers=_headers())
        if not r.is_success:
            print(f"[SB PATCH] {path} → {r.status_code}: {r.text[:200]}")
        return r

def sb_upload(filename, img_bytes):
    upload_headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "image/jpeg"
    }
    with httpx.Client(timeout=15.0) as c:
        return c.post(f"{SUPABASE_URL}/storage/v1/object/security_captures/{filename}",
                      content=img_bytes, headers=upload_headers)

# ── ML Model ──────────────────────────────────────────────────────────────────
MODEL_PATH = 'runs/detect/atm_security/train_optimized_final/weights/best.pt'
model = YOLO(MODEL_PATH)

# ── Camera state ──────────────────────────────────────────────────────────────
camera        = None
camera_lock   = threading.Lock()
is_scanning   = False
app_running   = True
bg_thread     = None
thread_lock   = threading.Lock()
_idle_since   = None   # time when scanning stopped, for auto-release
IDLE_TIMEOUT  = 10     # seconds


def open_camera():
    print("[CAMERA] Opening…")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap.release()
        cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
        cap.set(cv2.CAP_PROP_FPS, 20)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        print("[CAMERA] Opened OK")
        return cap
    print("[CAMERA] Failed")
    return None


def release_camera_safe():
    global camera
    with camera_lock:
        if camera is not None:
            try: camera.release()
            except: pass
            camera = None
            print("[CAMERA] Released")


def cleanup():
    global app_running, is_scanning
    app_running = False
    is_scanning = False
    release_camera_safe()
    cv2.destroyAllWindows()
    print("[CLEANUP] Done")

atexit.register(cleanup)


# ── Background camera + inference thread ──────────────────────────────────────
def background_thread():
    global is_scanning, camera, _idle_since
    print("[THREAD] Started")

    while app_running:
        if is_scanning:
            _idle_since = None
            with camera_lock:
                if camera is None:
                    camera = open_camera()
                if camera is None:
                    time.sleep(0.5)
                    continue
                ok, frame = camera.read()

            if not ok or frame is None:
                time.sleep(0.05)
                continue

            try:
                small = cv2.resize(frame, (416, 312))
                results = model(small, conf=0.45, verbose=False)
                result  = results[0]
                annotated = result.plot()
                annotated = cv2.resize(annotated, (frame.shape[1], frame.shape[0]))

                classes = result.boxes.cls.tolist()
                status = {
                    'face_detected':   0 in classes,
                    'mask_detected':   1 in classes,
                    'helmet_detected': 2 in classes
                }

                _, buf = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, 60])
                b64 = base64.b64encode(buf).decode('utf-8')
                socketio.emit('security_update', {'image': b64, 'status': status})

            except Exception as e:
                print(f"[INFERENCE] {e}")

        else:
            # auto-release camera after idle timeout
            if camera is not None:
                if _idle_since is None:
                    _idle_since = time.time()
                elif time.time() - _idle_since > IDLE_TIMEOUT:
                    release_camera_safe()
                    _idle_since = None

        time.sleep(0.05)

    release_camera_safe()
    print("[THREAD] Stopped")


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/validate_card', methods=['POST'])
def validate_card():
    """Quick card existence check before PIN screen."""
    if not SUPABASE_URL or 'YOUR_' in SUPABASE_URL:
        return jsonify({'success': False, 'message': 'Database not configured.'})
    d    = request.json or {}
    card = str(d.get('card_number', '')).strip().replace(' ', '')
    if not card:
        return jsonify({'success': False, 'message': 'Please enter a card number.'})
    try:
        res = sb_get('accounts', f'card_number=eq.{card}&select=card_number,is_blocked')
        print(f"[validate_card] card={card} status={res.status_code} body={res.text[:200]}")
        if not res.is_success:
            return jsonify({'success': False, 'message': f'Database error ({res.status_code}). Check server logs.'})
        rows = res.json()
        if not rows:
            return jsonify({'success': False, 'message': 'Card not recognised. Try again.'})
        if rows[0].get('is_blocked'):
            return jsonify({'success': False, 'message': 'This card is blocked. Contact your bank.'})
        return jsonify({'success': True})
    except Exception as e:
        print(f"[validate_card] {e}")
        return jsonify({'success': False, 'message': 'Server error. Try again.'})


@app.route('/api/validate_pin', methods=['POST'])
def validate_pin():
    if not SUPABASE_URL or 'YOUR_' in SUPABASE_URL:
        return jsonify({'success': False, 'message': 'Database not configured.'})
    d    = request.json or {}
    card = str(d.get('card_number', '')).strip().replace(' ', '')
    pin  = str(d.get('pin', '')).strip()
    if not card or not pin:
        return jsonify({'success': False, 'message': 'Card number and PIN are required.'})
    try:
        res = sb_get('accounts', f'card_number=eq.{card}')
        print(f"[validate_pin] card={card} status={res.status_code} body={res.text[:300]}")
        if not res.is_success:
            return jsonify({'success': False, 'message': f'Database error ({res.status_code}).'})
        rows = res.json()
        if not rows:
            return jsonify({'success': False, 'message': 'Card not found.'})
        acct = rows[0]
        if acct.get('is_blocked'):
            return jsonify({'success': False, 'message': 'Card blocked. Contact your bank.'})
        if str(acct.get('pin', '')).strip() != pin:
            failed = int(acct.get('failed_attempts', 0)) + 1
            if failed >= 3:
                threading.Thread(target=sb_patch, args=('accounts', f'card_number=eq.{card}',
                    {'failed_attempts': failed, 'is_blocked': True}), daemon=True).start()
                return jsonify({'success': False, 'message': 'Card blocked after 3 wrong PINs.'})
            threading.Thread(target=sb_patch, args=('accounts', f'card_number=eq.{card}',
                {'failed_attempts': failed}), daemon=True).start()
            return jsonify({'success': False, 'message': f'Wrong PIN. {3 - failed} attempt(s) remaining.'})
        threading.Thread(target=sb_patch, args=('accounts', f'card_number=eq.{card}',
            {'failed_attempts': 0}), daemon=True).start()
        return jsonify({'success': True, 'name': acct.get('name', 'User')})
    except Exception as e:
        print(f"[validate_pin] {e}")
        return jsonify({'success': False, 'message': 'Server error. Try again.'})


@app.route('/api/balance', methods=['GET'])
def get_balance():
    card = request.args.get('card_number', '')
    try:
        res = sb_get('accounts', f'card_number=eq.{card}&select=name,balance')
        if res.is_success and res.json():
            d = res.json()[0]
            return jsonify({'success': True, 'balance': d['balance'], 'name': d.get('name')})
    except Exception as e:
        print(f"[balance] {e}")
    return jsonify({'success': False})


@app.route('/api/statement', methods=['GET'])
def get_statement():
    card = request.args.get('card_number', '')
    try:
        res = sb_get('transactions', f'card_number=eq.{card}&order=created_at.desc&limit=5')
        if res.is_success:
            return jsonify({'success': True, 'transactions': res.json()})
    except Exception as e:
        print(f"[statement] {e}")
    return jsonify({'success': False, 'transactions': []})


@app.route('/api/withdraw', methods=['POST'])
def withdraw():
    if not SUPABASE_URL or 'YOUR_' in SUPABASE_URL:
        return jsonify({'success': False, 'message': 'Database not configured.'})
    d    = request.json or {}
    card = str(d.get('card_number', '')).strip().replace(' ', '')
    fb64 = d.get('image', None)
    try:
        amt = float(d.get('amount', 0))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid amount.'})

    try:
        res = sb_get('accounts', f'card_number=eq.{card}&select=balance,name')
        if not res.is_success or not res.json():
            return jsonify({'success': False, 'message': 'Account not found.'})
        acct    = res.json()[0]
        bal     = float(acct['balance'])
        name    = acct.get('name', 'User')

        if amt <= 0:
            return jsonify({'success': False, 'message': 'Amount must be greater than zero.'})
        if bal < amt:
            return jsonify({'success': False, 'message': f'Insufficient funds. Balance: ₹{bal:,.2f}'})

        # ── 1. Commit financial transaction IMMEDIATELY (no upload wait) ──
        new_bal   = round(bal - amt, 2)
        txn_res   = sb_post('transactions',
                            {'card_number': card, 'amount': amt,
                             'type': 'WITHDRAWAL', 'image_url': None})
        sb_patch('accounts', f'card_number=eq.{card}', {'balance': new_bal})

        txn_id = None
        if txn_res.is_success and txn_res.json():
            txn_id = txn_res.json()[0].get('id')

        # ── 2. Upload face image in background (fire-and-forget) ──────────
        if fb64 and txn_id:
            def _upload_bg(tid, card_no, b64_img):
                try:
                    raw   = b64_img.split(',')[1] if ',' in b64_img else b64_img
                    byt   = base64.b64decode(raw)
                    fname = f"{card_no}_{int(time.time())}_{uuid.uuid4().hex[:6]}.jpg"
                    up    = sb_upload(fname, byt)
                    if up.is_success:
                        img_url = f"{SUPABASE_URL}/storage/v1/object/public/security_captures/{fname}"
                        sb_patch('transactions', f'id=eq.{tid}', {'image_url': img_url})
                        print(f"[STORAGE] uploaded {fname}")
                    else:
                        print(f"[STORAGE] upload failed: {up.status_code} {up.text[:120]}")
                except Exception as ex:
                    print(f"[STORAGE] bg error: {ex}")

            threading.Thread(target=_upload_bg, args=(txn_id, card, fb64), daemon=True).start()

        return jsonify({'success': True, 'new_balance': new_bal, 'name': name, 'amount': amt})

    except Exception as e:
        print(f"[withdraw] {e}")
        return jsonify({'success': False, 'message': 'Server error. Try again.'})



# ── SocketIO events ───────────────────────────────────────────────────────────
@socketio.on('start_scan')
def on_start():
    global is_scanning
    is_scanning = True
    print("[SCAN] ON")

@socketio.on('stop_scan')
def on_stop():
    global is_scanning
    is_scanning = False
    print("[SCAN] OFF")

@socketio.on('connect')
def on_connect():
    global bg_thread
    with thread_lock:
        if bg_thread is None or not bg_thread.is_alive():
            bg_thread = threading.Thread(target=background_thread, daemon=True)
            bg_thread.start()
    print('[WS] Client connected')


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 48)
    print("  ATM Security System  →  http://localhost:5001")
    print("=" * 48)
    try:
        socketio.run(app, debug=False, port=5001, allow_unsafe_werkzeug=True,
                     use_reloader=False)
    except OSError as e:
        if '10048' in str(e):
            print("[ERROR] Port in use. Run: taskkill /IM python.exe /F")
        else:
            raise
    finally:
        cleanup()
