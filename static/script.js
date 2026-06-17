document.addEventListener('DOMContentLoaded', () => {
    // Force polling: Werkzeug dev server is WSGI-only and cannot handle
    // raw WebSocket upgrades in threading mode — doing so causes a 500
    // "write() before start_response" AssertionError crash.
    const socket = io({ transports: ['polling'], upgrade: false });

    /* ── State ────────────────────────────────── */
    let currentPin      = '';
    let currentCard     = '';
    let capturedFace    = null;   // base64 face from security scan
    let userName        = '';
    let pendingAmount   = 0;

    /* ── DOM refs ─────────────────────────────── */
    const webcamFeed     = document.getElementById('webcam-feed');
    const securityAlert  = document.getElementById('security-alert');
    const alertMsg       = document.getElementById('alert-msg');
    const statusFace     = document.getElementById('status-face');
    const statusMask     = document.getElementById('status-mask');
    const statusHelmet   = document.getElementById('status-helmet');
    const btnProceed     = document.getElementById('btn-proceed');
    const pinLoading     = document.getElementById('pin-loading');
    const pinError       = document.getElementById('pin-error');
    const camPlaceholder = document.getElementById('cam-placeholder');
    const footerCard     = document.getElementById('footer-card');

    /* ── Screen map ───────────────────────────── */
    const screens = {
        welcome: 'screen-welcome', pin: 'screen-pin', scan: 'screen-scan',
        menu: 'screen-menu', withdrawal: 'screen-withdrawal',
        balance: 'screen-balance', ministatement: 'screen-ministatement',
        pinchange: 'screen-pinchange', processing: 'screen-processing',
        dispense: 'screen-dispense'
    };

    /* ── showScreen ───────────────────────────── */
    window.showScreen = async (id) => {
        // hide all
        Object.values(screens).forEach(sid => {
            const el = document.getElementById(sid);
            if (el) el.classList.remove('active');
        });

        const target = document.getElementById(screens[id]);
        if (target) target.classList.add('active');

        // Camera control
        if (id === 'scan') {
            socket.emit('start_scan');
            capturedFace = null;
            camPlaceholder.style.display = 'flex';
            webcamFeed.classList.remove('active');
            webcamFeed.src = '';
        } else {
            socket.emit('stop_scan');
        }

        // Per-screen side-effects
        if (id === 'welcome') {
            currentPin = ''; currentCard = '';
            updatePinDisplay();
            document.getElementById('demo-card-number').value = '';
            footerCard.textContent = '';
        }

        if (id === 'balance') await loadBalance();
        if (id === 'ministatement') await loadStatement();
    };

    /* ── Clock ────────────────────────────────── */
    const tick = () => {
        const now = new Date();
        document.getElementById('system-time').textContent =
            now.toLocaleTimeString('en-IN', { hour12: false });
    };
    tick(); setInterval(tick, 1000);

    /* ── Step 1: Insert Card ─────────────────── */
    const btnInsert = document.getElementById('btn-insert-card');
    btnInsert.addEventListener('click', async () => {
        const cardInput = document.getElementById('demo-card-number').value.trim().replace(/\s+/g, '');
        if (!cardInput) { showToast('Please enter your card number.', 'error'); return; }
        if (cardInput.length < 6) { showToast('Card number too short.', 'error'); return; }

        // Show loading on button
        btnInsert.disabled = true;
        btnInsert.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Checking...';

        try {
            const res = await fetch('/api/validate_card', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ card_number: cardInput })
            });
            const data = await res.json();
            if (data.success) {
                currentCard = cardInput;
                footerCard.textContent = `Card: ••••${currentCard.slice(-4)}`;
                currentPin = '';
                updatePinDisplay();
                showScreen('pin');
            } else {
                showToast(data.message || 'Card not recognised.', 'error');
                document.getElementById('demo-card-number').focus();
            }
        } catch (e) {
            showToast('Cannot reach server. Check connection.', 'error');
        } finally {
            btnInsert.disabled = false;
            btnInsert.innerHTML = '<i class="fas fa-arrow-right-to-bracket"></i> INSERT CARD';
        }
    });

    // Allow Enter key on card number field
    document.getElementById('demo-card-number').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') btnInsert.click();
    });

    /* ── Step 2: PIN numpad ───────────────────── */
    document.querySelectorAll('.num').forEach(btn => {
        btn.addEventListener('click', () => {
            if (currentPin.length < 4) {
                currentPin += btn.dataset.n;
                updatePinDisplay();
                // auto submit when 4 digits
                if (currentPin.length === 4) setTimeout(submitPin, 120);
            }
        });
    });

    document.getElementById('btn-clear').addEventListener('click', () => {
        currentPin = currentPin.slice(0, -1);
        updatePinDisplay();
    });

    document.getElementById('btn-pin-enter').addEventListener('click', submitPin);

    function updatePinDisplay() {
        for (let i = 0; i < 4; i++) {
            const dot = document.getElementById(`dot-${i}`);
            dot.classList.toggle('filled', i < currentPin.length);
            dot.classList.remove('error');
        }
    }

    async function submitPin() {
        if (currentPin.length < 4) { showToast('Enter all 4 digits.', 'warn'); return; }
        pinError.classList.add('hidden');
        pinLoading.classList.remove('hidden');
        document.querySelectorAll('.num,.btn-clear,.btn-enter').forEach(b => b.disabled = true);

        try {
            const res = await fetch('/api/validate_pin', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: currentPin, card_number: currentCard })
            });
            const data = await res.json();

            if (data.success) {
                userName = data.name || 'User';
                showScreen('scan');
            } else {
                // shake dots red
                for (let i = 0; i < 4; i++) {
                    document.getElementById(`dot-${i}`).classList.add('error');
                }
                pinError.textContent = data.message || 'Invalid PIN';
                pinError.classList.remove('hidden');
                currentPin = '';
                setTimeout(updatePinDisplay, 600);
            }
        } catch (e) {
            pinError.textContent = 'Cannot reach server. Try again.';
            pinError.classList.remove('hidden');
            currentPin = '';
            setTimeout(updatePinDisplay, 300);
        } finally {
            pinLoading.classList.add('hidden');
            document.querySelectorAll('.num,.btn-clear,.btn-enter').forEach(b => b.disabled = false);
        }
    }

    /* ── Step 3: Security Scan ───────────────── */
    socket.on('security_update', (data) => {
        if (!document.getElementById('screen-scan').classList.contains('active')) return;

        // Show feed
        if (!webcamFeed.classList.contains('active')) {
            camPlaceholder.style.display = 'none';
            webcamFeed.classList.add('active');
        }
        webcamFeed.src = 'data:image/jpeg;base64,' + data.image;

        const { face_detected, mask_detected, helmet_detected } = data.status;

        // Update status pills
        statusFace.className   = 'status-item ' + (face_detected ? 'clear' : '');
        statusMask.className   = 'status-item ' + (mask_detected ? 'danger' : '');
        statusHelmet.className = 'status-item ' + (helmet_detected ? 'danger' : '');

        // Alert
        if (mask_detected) {
            alertMsg.textContent = 'PLEASE REMOVE MASK';
            securityAlert.classList.remove('hidden');
        } else if (helmet_detected) {
            alertMsg.textContent = 'PLEASE REMOVE HELMET';
            securityAlert.classList.remove('hidden');
        } else {
            securityAlert.classList.add('hidden');
        }

        // Proceed button
        const ok = face_detected && !mask_detected && !helmet_detected;
        btnProceed.classList.toggle('disabled', !ok);
        btnProceed.disabled = !ok;
        if (ok) capturedFace = data.image;
    });

    document.getElementById('btn-proceed').addEventListener('click', () => {
        document.getElementById('welcome-name').textContent = `Welcome, ${userName}!`;
        showScreen('menu');
    });

    /* ── Withdrawal ──────────────────────────── */
    document.querySelectorAll('.amt-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const amt = parseInt(btn.dataset.amt);
            doWithdraw(amt);
        });
    });

    document.getElementById('btn-withdraw-custom').addEventListener('click', () => {
        const val = parseFloat(document.getElementById('custom-amount').value);
        if (!val || val <= 0 || val % 100 !== 0) {
            showToast('Enter a valid amount (multiples of 100)', 'error'); return;
        }
        doWithdraw(val);
    });

    async function doWithdraw(amount) {
        pendingAmount = amount;
        document.getElementById('processing-msg').textContent = `Processing ₹${amount.toLocaleString('en-IN')}…`;
        showScreen('processing');

        try {
            const res = await fetch('/api/withdraw', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    card_number: currentCard,
                    amount: amount,
                    image: capturedFace
                })
            });
            const data = await res.json();

            if (data.success) {
                // Populate receipt
                const now = new Date();
                document.getElementById('rcpt-name').textContent    = data.name || userName;
                document.getElementById('rcpt-card').textContent    = `••••${currentCard.slice(-4)}`;
                document.getElementById('rcpt-amount').textContent  = `₹ ${parseFloat(data.amount).toLocaleString('en-IN')}`;
                document.getElementById('rcpt-balance').textContent = `₹ ${parseFloat(data.new_balance).toLocaleString('en-IN')}`;
                document.getElementById('rcpt-date').textContent    = now.toLocaleString('en-IN');
                setTimeout(() => showScreen('dispense'), 800);
            } else {
                showToast(data.message || 'Transaction failed.', 'error');
                showScreen('withdrawal');
            }
        } catch (e) {
            showToast('Server error. Please try again.', 'error');
            showScreen('menu');
        }
    }

    /* ── Balance ─────────────────────────────── */
    async function loadBalance() {
        const el  = document.getElementById('balance-display');
        const nm  = document.getElementById('balance-acct-name');
        el.textContent = 'Loading…';
        try {
            const res = await fetch(`/api/balance?card_number=${currentCard}`);
            const d   = await res.json();
            if (d.success) {
                el.textContent = `₹ ${parseFloat(d.balance).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;
                nm.textContent = d.name || '';
            } else {
                el.textContent = 'Unavailable';
            }
        } catch { el.textContent = 'Error'; }
    }

    /* ── Statement ───────────────────────────── */
    async function loadStatement() {
        const container = document.getElementById('statement-list-container');
        container.innerHTML = '<div class="stmt-loading"><div class="spinner"></div> Loading…</div>';
        try {
            const res = await fetch(`/api/statement?card_number=${currentCard}`);
            const d   = await res.json();

            if (d.success && d.transactions.length > 0) {
                container.innerHTML = d.transactions.map(t => {
                    const dt   = new Date(t.created_at);
                    const date = dt.toLocaleDateString('en-IN', { day:'2-digit', month:'short' });
                    const isD  = t.type === 'WITHDRAWAL';
                    return `
                    <div class="stmt-row">
                        <div class="stmt-left">
                            <span class="stmt-date">${date}</span>
                            <span class="stmt-type">${t.type}</span>
                        </div>
                        <span class="stmt-amount ${isD ? 'debit' : 'credit'}">
                            ${isD ? '−' : '+'}₹${parseFloat(t.amount).toLocaleString('en-IN')}
                        </span>
                    </div>`;
                }).join('');
            } else {
                container.innerHTML = '<div class="stmt-loading">No transactions found.</div>';
            }
        } catch {
            container.innerHTML = '<div class="stmt-loading">Failed to load.</div>';
        }
    }

    /* ── PIN Change ──────────────────────────── */
    document.getElementById('btn-change-pin').addEventListener('click', () => {
        const old1 = document.getElementById('old-pin').value;
        const new1 = document.getElementById('new-pin-1').value;
        const new2 = document.getElementById('new-pin-2').value;
        if (!old1 || old1.length !== 4) { showToast('Enter your current 4-digit PIN.', 'warn'); return; }
        if (new1.length !== 4 || new2.length !== 4) { showToast('New PIN must be 4 digits.', 'warn'); return; }
        if (new1 !== new2) { showToast('New PINs do not match.', 'error'); return; }
        document.getElementById('processing-msg').textContent = 'Updating PIN…';
        showScreen('processing');
        // TODO: connect to a /api/change_pin endpoint when ready
        setTimeout(() => {
            showToast('PIN changed successfully!', 'success');
            showScreen('menu');
        }, 1500);
    });

    /* ── Toast Notifications ─────────────────── */
    function showToast(msg, type = 'info') {
        const existing = document.querySelector('.atm-toast');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = `atm-toast toast-${type}`;
        toast.innerHTML = `<i class="fas fa-${type === 'error' ? 'circle-xmark' : type === 'success' ? 'circle-check' : 'circle-info'}"></i> ${msg}`;
        document.body.appendChild(toast);

        const style = document.createElement('style');
        style.textContent = `
            .atm-toast {
                position:fixed; bottom:28px; left:50%; transform:translateX(-50%) translateY(20px);
                padding:12px 24px; border-radius:100px;
                font-size:0.85rem; font-weight:600;
                display:flex; align-items:center; gap:8px;
                z-index:9999; white-space:nowrap;
                animation:toastIn 0.3s ease forwards;
                backdrop-filter:blur(12px);
                font-family:'Inter',sans-serif;
            }
            .toast-error   { background:rgba(255,51,102,0.15); border:1px solid rgba(255,51,102,0.4); color:#ff3366; }
            .toast-success { background:rgba(0,230,118,0.12); border:1px solid rgba(0,230,118,0.35); color:#00e676; }
            .toast-warn    { background:rgba(255,184,0,0.12); border:1px solid rgba(255,184,0,0.35); color:#ffb800; }
            .toast-info    { background:rgba(0,240,255,0.1); border:1px solid rgba(0,240,255,0.3); color:#00f0ff; }
            @keyframes toastIn { to { transform:translateX(-50%) translateY(0); opacity:1; } }
        `;
        if (!document.getElementById('toast-styles')) {
            style.id = 'toast-styles';
            document.head.appendChild(style);
        }

        setTimeout(() => toast.remove(), 3500);
    }
});
