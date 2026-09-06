from pathlib import Path
import os
import time
import json
import hmac
import hashlib
import threading
import queue
import urllib.parse
from datetime import datetime

import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

try:
    import websockets
except ImportError:
    websockets = None

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None


# ============================================================
# GuardAgent OS v5.0 • Binance AI Command Center
# Real-time market terminal + account monitor
# SAFE MODE — NO LIVE ORDERS
# ============================================================

st.set_page_config(
    page_title="GuardAgent OS • Real-Time Sentinel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env", override=True)

# -------------------- Premium UI --------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Orbitron:wght@500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp * { font-variant-numeric: tabular-nums; }
.ai-font, .hero-kicker, .metric-label, .pill, .brand-title { font-family: Orbitron, Inter, sans-serif !important; }
.stApp {
    background:
      radial-gradient(circle at 80% 5%, rgba(240,185,11,.12), transparent 25%),
      radial-gradient(circle at 10% 90%, rgba(50,120,255,.06), transparent 25%),
      #07090c;
    color:#f4f5f7;
}
.stApp:before {
    content:""; position:fixed; inset:0; pointer-events:none; opacity:.20;
    background-image:
      linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
    background-size:40px 40px;
}
section[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#0b0e12,#07090b);
    border-right:1px solid rgba(240,185,11,.16);
}
.block-container { max-width:1500px; padding-top:1.1rem; }
h1,h2,h3,h4 { font-family:"Space Grotesk",Inter,sans-serif !important; }

.brand { display:flex; align-items:center; gap:12px; padding:8px 0 18px; }
.brand-icon {
    width:46px; height:46px; border-radius:14px; display:flex;
    align-items:center; justify-content:center; background:#f0b90b; color:#111;
    font-size:24px; box-shadow:0 0 28px rgba(240,185,11,.22);
}
.brand-title { font-weight:800; letter-spacing:.7px; color:#f0b90b; }
.brand-sub { font-size:11px; color:#858c97; margin-top:3px; }

.hero {
    border:1px solid rgba(240,185,11,.20); border-radius:22px; padding:24px 28px;
    background:linear-gradient(135deg,rgba(240,185,11,.08),rgba(255,255,255,.025));
    box-shadow:0 18px 70px rgba(0,0,0,.28);
}
.hero-kicker { color:#f0b90b; font-size:11px; font-weight:800; letter-spacing:1.6px; }
.hero-title { font-size:32px; font-weight:800; margin:5px 0; }
.hero-text { color:#8f97a2; max-width:950px; line-height:1.6; font-size:13px; }

.pill {
    display:inline-flex; align-items:center; gap:7px; padding:6px 11px;
    border-radius:999px; font-size:10px; font-weight:800; letter-spacing:.4px;
}
.pill-live { background:rgba(0,214,143,.10); color:#00d68f; border:1px solid rgba(0,214,143,.24); }
.pill-warn { background:rgba(240,185,11,.10); color:#f0b90b; border:1px solid rgba(240,185,11,.25); }
.pill-off { background:rgba(255,70,70,.10); color:#ff8b8b; border:1px solid rgba(255,70,70,.22); }

.card, .metric-card {
    border:1px solid rgba(255,255,255,.075); border-radius:17px; padding:16px;
    background:rgba(16,19,24,.88);
}
.metric-card {
    border-color:rgba(240,185,11,.22);
    background:linear-gradient(145deg,rgba(240,185,11,.065),rgba(16,19,24,.92));
}
.metric-label { color:#929aa5; font-size:11px; text-transform:uppercase; letter-spacing:.5px; }
.metric-value { font-size:28px; font-weight:800; color:#f0b90b; margin-top:4px; }
.metric-small { color:#7f8791; font-size:10px; margin-top:4px; }
.section-title { font-size:18px; font-weight:800; margin:12px 0 10px; }
.status-box {
    border-radius:10px; padding:10px 12px; margin-bottom:8px; font-size:12px;
    border:1px solid rgba(255,255,255,.06);
}
.status-good { background:rgba(0,190,120,.13); color:#62efba; }
.status-warn { background:rgba(240,185,11,.13); color:#f5d66d; }
.status-bad { background:rgba(255,70,70,.13); color:#ff8787; }
.small-muted { color:#7f8791; font-size:10px; line-height:1.6; }

.log {
    border-left:3px solid #f0b90b; background:rgba(240,185,11,.05);
    padding:8px 11px; margin:6px 0; border-radius:0 8px 8px 0; font-size:11px;
}
div.stButton > button {
    background:#f0b90b !important; color:#111 !important; border:none !important;
    font-weight:800 !important; border-radius:9px !important;
}
[data-testid="stMetricValue"] { color:#f0b90b; }
div[data-testid="stDataFrame"] { border-radius:12px; overflow:hidden; }
footer { visibility:hidden; }
.ai-panel { border:1px solid rgba(0,214,143,.20); border-radius:18px; padding:16px; background:linear-gradient(135deg,rgba(0,214,143,.06),rgba(240,185,11,.035)); }
.ai-title { font-family:Orbitron,Inter,sans-serif; font-size:12px; letter-spacing:1.2px; color:#00d68f; font-weight:800; }
.ai-signal { font-family:Orbitron,Inter,sans-serif; font-size:22px; font-weight:800; margin-top:5px; }
.sub-card { border:1px solid rgba(240,185,11,.24); border-radius:18px; padding:18px; background:linear-gradient(145deg,rgba(240,185,11,.08),rgba(16,19,24,.94)); }
.badge { display:inline-block; padding:4px 8px; border-radius:999px; font-size:9px; font-weight:800; letter-spacing:.6px; background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.08); }
</style>
""", unsafe_allow_html=True)


# -------------------- Session state --------------------
DEFAULTS = {
    "price": 0.0,
    "previous_price": 0.0,
    "price_history": [],
    "tick_history": [],
    "market_ticks": {},
    "market_queue": None,
    "ws_status": "Starting",
    "ws_error": "",
    "events": [],
    "account": None,
    "account_error": "",
    "account_status": "Not checked",
    "account_last_check": 0.0,
    "server_offset_ms": 0,
    "server_offset_at": 0.0,
    "last_public_fetch": 0.0,
    "subaccount": None,
    "subaccount_error": "",
    "subaccount_last_check": 0.0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# -------------------- Config --------------------
WATCHLIST = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT", "ADAUSDT", "TRXUSDT"]
REST_ENDPOINTS = [
    "https://api.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
    "https://api4.binance.com",
]
PUBLIC_ENDPOINTS = [
    "https://data-api.binance.vision",
    "https://api.binance.com",
    "https://api1.binance.com",
]
session = requests.Session()
session.headers.update({"User-Agent": "GuardAgentOS/5.0", "Connection": "close"})


def api_key():
    return os.getenv("BINANCE_API_KEY", "").strip()


def api_secret():
    return os.getenv("BINANCE_SECRET_KEY", "").strip()


def add_event(message: str, level: str = "INFO"):
    stamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.events.insert(0, {"time": stamp, "level": level, "message": message})
    st.session_state.events = st.session_state.events[:80]


def get_json(base, path, params=None, timeout=8):
    r = session.get(base + path, params=params, timeout=timeout)
    if r.status_code >= 400:
        try:
            body = r.json()
        except Exception:
            body = r.text[:500]
        raise RuntimeError(f"HTTP {r.status_code}: {body}")
    return r.json()


# -------------------- Binance time + signed account --------------------
def get_server_time(force=False):
    now = time.time()
    if not force and (now - st.session_state.server_offset_at) < 20:
        return int(time.time() * 1000) + st.session_state.server_offset_ms

    last_error = None
    for base in REST_ENDPOINTS:
        try:
            t0 = time.time() * 1000
            data = get_json(base, "/api/v3/time", timeout=6)
            t1 = time.time() * 1000
            server_ms = int(data["serverTime"])
            midpoint = (t0 + t1) / 2
            st.session_state.server_offset_ms = int(server_ms - midpoint)
            st.session_state.server_offset_at = time.time()
            return int(time.time() * 1000) + st.session_state.server_offset_ms
        except Exception as e:
            last_error = e
    raise RuntimeError(f"Unable to sync Binance server time: {last_error}")


def signed_account_request():
    key, secret = api_key(), api_secret()
    if not key or not secret:
        raise RuntimeError("BINANCE_API_KEY / BINANCE_SECRET_KEY missing from .env")
    if len(key) < 20 or len(secret) < 20:
        raise RuntimeError("Binance credentials look incomplete.")

    last_error = None
    for attempt in range(2):
        try:
            timestamp = get_server_time(force=(attempt > 0))
            query = urllib.parse.urlencode(
                [("timestamp", str(timestamp)), ("recvWindow", "10000")],
                quote_via=urllib.parse.quote, safe=""
            )
            signature = hmac.new(
                secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
            ).hexdigest()
            final_query = query + "&signature=" + signature
            headers = {"X-MBX-APIKEY": key, "Accept": "application/json", "Connection": "close"}

            for base in REST_ENDPOINTS:
                try:
                    r = session.get(
                        base + "/api/v3/account?" + final_query,
                        headers=headers, timeout=12
                    )
                    if r.status_code == 200:
                        return r.json()

                    try:
                        body = r.json()
                    except Exception:
                        body = {"msg": r.text[:500]}
                    code = body.get("code")

                    if code == -1021:
                        last_error = RuntimeError("Timestamp rejected (-1021). Retrying with fresh server time.")
                        break
                    if code == -1022:
                        raise RuntimeError("Signature rejected (-1022). Check matching HMAC key + secret.")
                    if code == -2015:
                        raise RuntimeError(
                            "Binance rejected this API key (-2015). Check key type, IP restriction, "
                            "and account/User Data permission."
                        )
                    if r.status_code in (401, 403):
                        raise RuntimeError(
                            f"Binance authentication/permission error ({code}): {body.get('msg', body)}"
                        )
                    last_error = RuntimeError(f"Binance API error {r.status_code}: {body}")
                except requests.RequestException as e:
                    last_error = e
                    continue
        except RuntimeError:
            raise
        except Exception as e:
            last_error = e

    raise last_error or RuntimeError("Unknown Binance account API error")



def signed_sapi_get(path, params=None):
    """Signed HMAC GET for Binance SAPI USER_DATA endpoints."""
    key, secret = api_key(), api_secret()
    if not key or not secret:
        raise RuntimeError("BINANCE_API_KEY / BINANCE_SECRET_KEY missing from .env")
    params = dict(params or {})
    timestamp = get_server_time()
    params["timestamp"] = timestamp
    params.setdefault("recvWindow", 10000)
    query = urllib.parse.urlencode(params, doseq=True, quote_via=urllib.parse.quote, safe="")
    signature = hmac.new(secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256).hexdigest()
    final_query = query + "&signature=" + signature
    headers = {"X-MBX-APIKEY": key, "Accept": "application/json", "Connection": "close"}
    last_error = None
    for base in REST_ENDPOINTS:
        try:
            r = session.get(base + path + "?" + final_query, headers=headers, timeout=12)
            try:
                body = r.json()
            except Exception:
                body = {"msg": r.text[:500]}
            if r.status_code == 200:
                return body
            code = body.get("code") if isinstance(body, dict) else None
            if code == -1021:
                get_server_time(force=True)
                raise RuntimeError("Timestamp rejected (-1021). Please refresh and retry.")
            if code == -1022:
                raise RuntimeError("Signature rejected (-1022). Check matching HMAC key + secret.")
            if code == -2015:
                raise RuntimeError("Binance rejected this key (-2015). Check key type, IP restriction and permissions.")
            last_error = RuntimeError(f"Binance SAPI error {r.status_code}: {body}")
        except requests.RequestException as e:
            last_error = e
            continue
    raise last_error or RuntimeError("Unknown Binance SAPI error")


def refresh_subaccount(email, force=False):
    email = (email or "").strip()
    now = time.time()
    if not email:
        st.session_state.subaccount = None
        st.session_state.subaccount_error = "Enter the sub-account email for Master → Sub-account mode."
        return
    if not force and (now - st.session_state.subaccount_last_check) < 30:
        return
    try:
        data = signed_sapi_get("/sapi/v4/sub-account/assets", {"email": email})
        if not isinstance(data, dict) or "balances" not in data:
            raise RuntimeError(f"Unexpected sub-account response: {data}")
        st.session_state.subaccount = data
        st.session_state.subaccount_error = ""
        st.session_state.subaccount_last_check = now
        add_event("Master API → sub-account assets loaded successfully.", "OK")
    except Exception as e:
        st.session_state.subaccount = None
        st.session_state.subaccount_error = str(e)
        st.session_state.subaccount_last_check = now
        add_event(f"Sub-account sync failed: {e}", "ERROR")


def refresh_account(force=False):
    now = time.time()
    if not force and (now - st.session_state.account_last_check) < 30:
        return
    try:
        data = signed_account_request()
        st.session_state.account = data
        st.session_state.account_error = ""
        st.session_state.account_status = "Connected"
        st.session_state.account_last_check = now
        add_event("Binance account authentication successful.", "OK")
    except Exception as e:
        st.session_state.account = None
        st.session_state.account_error = str(e)
        st.session_state.account_status = "Offline"
        st.session_state.account_last_check = now
        add_event(str(e), "ERROR")


# -------------------- Public market data --------------------
@st.cache_data(ttl=3, show_spinner=False)
def public_24h(symbol):
    last = None
    for base in PUBLIC_ENDPOINTS:
        try:
            return get_json(base, "/api/v3/ticker/24hr", {"symbol": symbol}, timeout=6)
        except Exception as e:
            last = e
    raise RuntimeError(f"24h ticker unavailable: {last}")


@st.cache_data(ttl=3, show_spinner=False)
def order_book(symbol, limit=20):
    last = None
    for base in PUBLIC_ENDPOINTS:
        try:
            return get_json(base, "/api/v3/depth", {"symbol": symbol, "limit": limit}, timeout=6)
        except Exception as e:
            last = e
    raise RuntimeError(f"Order book unavailable: {last}")


@st.cache_data(ttl=4, show_spinner=False)
def recent_trades(symbol, limit=30):
    last = None
    for base in PUBLIC_ENDPOINTS:
        try:
            return get_json(base, "/api/v3/trades", {"symbol": symbol, "limit": limit}, timeout=6)
        except Exception as e:
            last = e
    raise RuntimeError(f"Trades unavailable: {last}")


@st.cache_data(ttl=10, show_spinner=False)
def klines(symbol, interval="1m", limit=120):
    last = None
    for base in PUBLIC_ENDPOINTS:
        try:
            data = get_json(
                base, "/api/v3/klines",
                {"symbol": symbol, "interval": interval, "limit": limit},
                timeout=8
            )
            cols = ["open_time","open","high","low","close","volume","close_time",
                    "quote_volume","trades","taker_base","taker_quote","ignore"]
            df = pd.DataFrame(data, columns=cols)
            for c in ["open","high","low","close","volume"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df["time"] = pd.to_datetime(df["open_time"], unit="ms")
            return df
        except Exception as e:
            last = e
    raise RuntimeError(f"Kline data unavailable: {last}")


@st.cache_data(ttl=15, show_spinner=False)
def all_prices():
    last = None
    for base in PUBLIC_ENDPOINTS:
        try:
            data = get_json(base, "/api/v3/ticker/price", timeout=10)
            return {x["symbol"]: float(x["price"]) for x in data}
        except Exception as e:
            last = e
    raise RuntimeError(f"Price map unavailable: {last}")


# -------------------- WebSocket --------------------
def websocket_worker(q):
    if websockets is None:
        q.put(("status", "Unavailable", "Install websockets package."))
        return

    streams = "/".join([f"{s.lower()}@ticker" for s in WATCHLIST])
    urls = [
        f"wss://stream.binance.com:9443/stream?streams={streams}",
        f"wss://stream.binance.com:443/stream?streams={streams}",
    ]

    async def run():
        import asyncio
        while True:
            connected = False
            for url in urls:
                try:
                    q.put(("status", "Connecting", ""))
                    async with websockets.connect(
                        url, ping_interval=20, ping_timeout=20,
                        close_timeout=5, max_size=2**20
                    ) as ws:
                        connected = True
                        q.put(("status", "ONLINE", ""))
                        while True:
                            raw = await ws.recv()
                            packet = json.loads(raw)
                            data = packet.get("data", packet)
                            if data.get("e") == "24hrTicker":
                                symbol = data.get("s", "")
                                price = float(data.get("c", 0))
                                q.put(("ticker", symbol, price))
                except Exception as e:
                    q.put(("status", "Reconnecting", str(e)[:220]))
                    await asyncio.sleep(2)
            if not connected:
                await asyncio.sleep(2)

    import asyncio
    try:
        asyncio.run(run())
    except Exception as e:
        q.put(("status", "Error", str(e)[:220]))


def start_websocket():
    if st.session_state.market_queue is None:
        st.session_state.market_queue = queue.Queue()
        threading.Thread(
            target=websocket_worker,
            args=(st.session_state.market_queue,),
            daemon=True,
            name="GuardAgent-Binance-Market-WS",
        ).start()


def process_market_queue():
    q = st.session_state.market_queue
    if q is None:
        return
    while True:
        try:
            item = q.get_nowait()
        except queue.Empty:
            break

        kind = item[0]
        if kind == "status":
            st.session_state.ws_status = item[1]
            st.session_state.ws_error = item[2] if len(item) > 2 else ""
        elif kind == "ticker":
            symbol, price = item[1], float(item[2])
            old = st.session_state.market_ticks.get(symbol, 0.0)
            st.session_state.market_ticks[symbol] = price

            if symbol == "BTCUSDT":
                st.session_state.previous_price = old
                st.session_state.price = price
                if old:
                    pct = (price - old) / old * 100
                    st.session_state.tick_history.append(pct)
                    st.session_state.tick_history = st.session_state.tick_history[-120:]
                    if abs(pct) >= 0.08:
                        label = "SHARP PUMP" if pct > 0 else "SHARP DUMP"
                        add_event(f"{label}: BTC/USDT moved {pct:+.3f}% tick-to-tick", "ALERT")

                st.session_state.price_history.append(price)
                st.session_state.price_history = st.session_state.price_history[-180:]


# -------------------- Account valuation --------------------
def account_summary(account):
    if not account:
        return pd.DataFrame(columns=["Asset", "Free", "Locked", "Total", "Free USDT Value", "Locked USDT Value", "USDT Value"])

    try:
        prices = all_prices()
    except Exception:
        prices = {}

    stable = {"USDT", "USDC", "FDUSD", "TUSD", "BUSD", "DAI"}
    rows = []
    for b in account.get("balances", []):
        asset = b.get("asset", "")
        free = float(b.get("free", 0) or 0)
        locked = float(b.get("locked", 0) or 0)
        total = free + locked
        if total <= 0:
            continue

        if asset in stable:
            value = total
        elif asset == "BTC":
            value = total * prices.get("BTCUSDT", 0)
        elif asset == "ETH":
            value = total * prices.get("ETHUSDT", 0)
        elif asset == "BNB":
            value = total * prices.get("BNBUSDT", 0)
        elif asset == "SOL":
            value = total * prices.get("SOLUSDT", 0)
        elif asset == "XRP":
            value = total * prices.get("XRPUSDT", 0)
        elif asset == "DOGE":
            value = total * prices.get("DOGEUSDT", 0)
        elif asset == "ADA":
            value = total * prices.get("ADAUSDT", 0)
        elif asset == "TRX":
            value = total * prices.get("TRXUSDT", 0)
        else:
            value = total * prices.get(asset + "USDT", 0)

        free_value = (free * value / total) if total else 0.0
        locked_value = (locked * value / total) if total else 0.0
        rows.append({
            "Asset": asset,
            "Free": free,
            "Locked": locked,
            "Total": total,
            "Free USDT Value": free_value,
            "Locked USDT Value": locked_value,
            "USDT Value": value,
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values("USDT Value", ascending=False)
    return df


def fmt_money(x):
    return f"${x:,.2f}"


def fmt_price(x):
    if x >= 1000:
        return f"${x:,.2f}"
    if x >= 1:
        return f"${x:,.4f}"
    return f"${x:,.6f}"


def risk_score(change_pct, spread_pct, imbalance):
    score = 18.0
    score += min(abs(change_pct) * 70, 35)
    score += min(spread_pct * 250, 25)
    score += min(abs(imbalance) * 30, 20)
    return int(max(0, min(100, score)))


# -------------------- Start background work --------------------
start_websocket()
process_market_queue()


# -------------------- Sidebar --------------------
with st.sidebar:
    st.markdown("""
    <div class="brand">
      <div class="brand-icon">🛡️</div>
      <div>
        <div class="brand-title">GUARDAGENT OS</div>
        <div class="brand-sub">AI Sentinel • Real-Time Binance Terminal</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.caption("SYSTEM STATUS")

    ws = st.session_state.ws_status
    if ws == "ONLINE":
        st.markdown('<div class="status-box status-good">● Market stream: ONLINE</div>', unsafe_allow_html=True)
    elif ws in ("Connecting", "Reconnecting", "Starting"):
        st.markdown(f'<div class="status-box status-warn">● Market stream: {ws}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="status-box status-bad">● Market stream: {ws}</div>', unsafe_allow_html=True)

    st.divider()
    st.caption("MARKET")

    selected_symbol = st.selectbox(
        "Trading pair",
        WATCHLIST,
        index=WATCHLIST.index("BTCUSDT"),
        label_visibility="collapsed"
    )
    interval = st.selectbox(
        "Chart interval",
        ["1m", "5m", "15m", "1h", "4h"],
        index=0
    )

    st.divider()
    st.caption("ACCOUNT IDENTITY")
    account_mode = st.radio(
        "Balance source",
        ["Direct API account", "Master → Sub-account"],
        index=0,
        help="Direct mode reads /api/v3/account for the API key. Master mode reads Binance SAPI sub-account assets using the master key + sub-account email."
    )
    agentic_confirmed = st.checkbox(
        "Label this as Agentic / Sub-account",
        value=False,
        help="This is only a UI label. It does not change Binance permissions or detect account type automatically."
    )
    account_online = (st.session_state.subaccount is not None) if account_mode == "Master → Sub-account" else (st.session_state.account_status == "Connected")
    if account_online:
        st.markdown('<div class="status-box status-good">● Account API: ONLINE</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-box status-bad">● Account API: OFFLINE</div>', unsafe_allow_html=True)
    subaccount_email = ""
    if account_mode == "Master → Sub-account":
        subaccount_email = st.text_input(
            "Sub-account email",
            value=os.getenv("BINANCE_SUBACCOUNT_EMAIL", ""),
            placeholder="agentic-subaccount@example.com",
            help="The target sub-account email. This is not an API secret."
        ).strip()

    if st.button("🔄 Sync Account", use_container_width=True):
        if account_mode == "Master → Sub-account":
            refresh_subaccount(subaccount_email, force=True)
        else:
            refresh_account(force=True)
        st.rerun()

    if st.button("🧹 Clear Sentinel Logs", use_container_width=True):
        st.session_state.events = []
        st.rerun()

    st.divider()
    st.markdown(
        '<div class="small-muted"><b>GuardAgent OS v5.0</b><br><br>'
        'Real-time market monitoring • account balance valuation • order-book analytics • '
        'AI risk sandbox.<br><br><b>SAFE MODE:</b> no live orders are submitted.</div>',
        unsafe_allow_html=True
    )


# -------------------- Account sync --------------------
if account_mode == "Master → Sub-account":
    if st.session_state.subaccount_last_check == 0 and subaccount_email:
        refresh_subaccount(subaccount_email, force=True)
else:
    if st.session_state.account_last_check == 0:
        refresh_account(force=True)



# -------------------- Header --------------------
account_label = ("MASTER → SUB-ACCOUNT" if account_mode == "Master → Sub-account" else ("AGENTIC / SUB-ACCOUNT" if agentic_confirmed else "BINANCE API ACCOUNT"))
market_pill = "pill-live" if ws == "ONLINE" else "pill-warn"

st.markdown(f"""
<div class="hero">
  <div class="hero-kicker">AUTONOMOUS TRADING INTELLIGENCE • {account_label}</div>
  <div class="hero-title">GuardAgent OS <span style="color:#f0b90b">v4.0</span></div>
  <div class="hero-text">
    Real-time Binance market stream, multi-asset watchlist, live order-book pressure,
    recent trades, candlestick analytics, account valuation and AI security scoring —
    built as a monitoring/sandbox terminal with <b>no live order execution</b>.
  </div>
</div>
""", unsafe_allow_html=True)

st.write("")
h1, h2, h3, h4 = st.columns(4)
with h1:
    st.markdown(f'<span class="pill {market_pill}">● MARKET {ws.upper()}</span>', unsafe_allow_html=True)
with h2:
    st.markdown(f'<span class="pill pill-live">● {account_label}</span>', unsafe_allow_html=True)
with h3:
    st.caption("Selected market")
    st.write(selected_symbol)
with h4:
    st.caption("Last UI sync")
    st.write(datetime.now().strftime("%H:%M:%S"))

st.divider()


# -------------------- Selected market snapshot --------------------
try:
    ticker = public_24h(selected_symbol)
except Exception as e:
    ticker = {}
    st.warning(f"Market REST snapshot unavailable: {e}")

live_price = st.session_state.market_ticks.get(selected_symbol, 0.0)
if not live_price:
    live_price = float(ticker.get("lastPrice", 0) or 0)

price_change = float(ticker.get("priceChangePercent", 0) or 0)
high_24 = float(ticker.get("highPrice", 0) or 0)
low_24 = float(ticker.get("lowPrice", 0) or 0)
volume_24 = float(ticker.get("volume", 0) or 0)
quote_volume = float(ticker.get("quoteVolume", 0) or 0)
trades_24 = int(ticker.get("count", 0) or 0)

m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">{selected_symbol}</div>'
                f'<div class="metric-value">{fmt_price(live_price) if live_price else "—"}</div>'
                f'<div class="metric-small">LIVE WEBSOCKET PRICE</div></div>', unsafe_allow_html=True)
with m2:
    cls = "#00d68f" if price_change >= 0 else "#ff7070"
    st.markdown(f'<div class="metric-card"><div class="metric-label">24H CHANGE</div>'
                f'<div class="metric-value" style="color:{cls}">{price_change:+.2f}%</div>'
                f'<div class="metric-small">BINANCE 24H TICKER</div></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">24H HIGH / LOW</div>'
                f'<div class="metric-value" style="font-size:21px">{fmt_price(high_24)}</div>'
                f'<div class="metric-small">LOW {fmt_price(low_24)}</div></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">24H QUOTE VOLUME</div>'
                f'<div class="metric-value" style="font-size:22px">{fmt_money(quote_volume)}</div>'
                f'<div class="metric-small">{volume_24:,.2f} BASE VOLUME</div></div>', unsafe_allow_html=True)
with m5:
    st.markdown(f'<div class="metric-card"><div class="metric-label">24H TRADES</div>'
                f'<div class="metric-value">{trades_24:,}</div>'
                f'<div class="metric-small">EXECUTED TRADES COUNT</div></div>', unsafe_allow_html=True)


# -------------------- Main analytics --------------------
left, right = st.columns([1.65, 1.0], gap="large")

with left:
    st.markdown(f'<div class="section-title">📊 {selected_symbol} Real-Time Analytics</div>', unsafe_allow_html=True)

    try:
        kdf = klines(selected_symbol, interval, 120)
        chart_df = kdf.set_index("time")[["close", "volume"]].copy()
        chart_df.columns = ["Price", "Volume"]
        st.line_chart(chart_df[["Price"]], height=270, use_container_width=True)
    except Exception as e:
        if selected_symbol == "BTCUSDT" and st.session_state.price_history:
            st.line_chart(pd.DataFrame({"BTC/USDT": st.session_state.price_history}), height=270, use_container_width=True)
        else:
            st.info(f"Candle chart waiting for Binance data: {e}")

    cA, cB, cC = st.columns(3)
    with cA:
        st.metric("Session Price", fmt_price(live_price) if live_price else "—")
    with cB:
        st.metric("24H High", fmt_price(high_24) if high_24 else "—")
    with cC:
        st.metric("24H Low", fmt_price(low_24) if low_24 else "—")

    st.markdown('<div class="section-title">📡 Multi-Market Watchlist</div>', unsafe_allow_html=True)
    watch_rows = []
    for sym in WATCHLIST:
        px = st.session_state.market_ticks.get(sym, 0.0)
        try:
            t = public_24h(sym)
            ch = float(t.get("priceChangePercent", 0) or 0)
            qv = float(t.get("quoteVolume", 0) or 0)
            if not px:
                px = float(t.get("lastPrice", 0) or 0)
        except Exception:
            ch, qv = 0.0, 0.0
        watch_rows.append({
            "Pair": sym,
            "Live Price": px,
            "24H %": ch,
            "Quote Volume": qv
        })
    wdf = pd.DataFrame(watch_rows)
    if not wdf.empty:
        wdf["Live Price"] = wdf["Live Price"].map(lambda x: f"${x:,.6f}" if x < 1 else f"${x:,.4f}")
        wdf["24H %"] = wdf["24H %"].map(lambda x: f"{x:+.2f}%")
        wdf["Quote Volume"] = wdf["Quote Volume"].map(lambda x: f"${x:,.0f}")
        st.dataframe(wdf, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">⚠️ AI Security Sentinel</div>', unsafe_allow_html=True)
    if st.session_state.events:
        for e in st.session_state.events[:10]:
            st.markdown(
                f'<div class="log"><b>{e["time"]}</b> · <b>{e["level"]}</b> · {e["message"]}</div>',
                unsafe_allow_html=True
            )
    else:
        st.markdown('<div class="card"><span class="small-muted">No security anomalies detected.</span></div>',
                    unsafe_allow_html=True)


with right:
    # -------- Order book --------
    st.markdown('<div class="section-title">📚 Live Order-Book Pressure</div>', unsafe_allow_html=True)
    try:
        ob = order_book(selected_symbol, 20)
        bids = pd.DataFrame(ob["bids"], columns=["Price", "Qty"]).astype(float)
        asks = pd.DataFrame(ob["asks"], columns=["Price", "Qty"]).astype(float)
        bid_value = float((bids["Price"] * bids["Qty"]).sum())
        ask_value = float((asks["Price"] * asks["Qty"]).sum())
        total_depth = bid_value + ask_value
        imbalance = (bid_value - ask_value) / total_depth if total_depth else 0.0
        best_bid = bids["Price"].iloc[0] if not bids.empty else 0
        best_ask = asks["Price"].iloc[0] if not asks.empty else 0
        spread = best_ask - best_bid
        spread_pct = (spread / live_price * 100) if live_price else 0
        score = risk_score(price_change, spread_pct, imbalance)

        ob1, ob2, ob3 = st.columns(3)
        with ob1:
            st.metric("Bid Depth", f"${bid_value:,.0f}")
        with ob2:
            st.metric("Ask Depth", f"${ask_value:,.0f}")
        with ob3:
            st.metric("Imbalance", f"{imbalance:+.1%}")

        if imbalance > 0.12:
            st.success("BUY-SIDE pressure is dominant")
        elif imbalance < -0.12:
            st.warning("SELL-SIDE pressure is dominant")
        else:
            st.info("Order-book pressure is relatively balanced")

        depth_df = pd.concat([
            bids.head(10).assign(Side="BID"),
            asks.head(10).assign(Side="ASK")
        ], ignore_index=True)
        depth_df["Notional"] = depth_df["Price"] * depth_df["Qty"]
        depth_df["Price"] = depth_df["Price"].map(lambda x: f"{x:.6f}" if x < 1 else f"{x:,.4f}")
        depth_df["Qty"] = depth_df["Qty"].map(lambda x: f"{x:,.5f}")
        depth_df["Notional"] = depth_df["Notional"].map(lambda x: f"${x:,.2f}")
        st.dataframe(depth_df[["Side","Price","Qty","Notional"]], use_container_width=True, hide_index=True)
    except Exception as e:
        imbalance, spread_pct, score = 0.0, 0.0, 50
        st.warning(f"Order book unavailable: {e}")

    # -------- Risk engine --------
    st.markdown('<div class="section-title">🧠 AI Risk Sandbox</div>', unsafe_allow_html=True)
    max_slippage = st.slider("Maximum Allowed Slippage", 0.1, 2.0, 0.5, 0.1, format="%.1f%%")
    allocation = st.number_input("Sandbox Allocation Cap (USDT)", 0.0, 1_000_000.0, 10.0, 10.0)
    estimated_loss = allocation * max_slippage / 100.0

    r1, r2 = st.columns(2)
    with r1:
        st.metric("Allocation", f"{allocation:,.2f} USDT")
    with r2:
        st.metric("Max Slippage Loss", f"{estimated_loss:,.2f} USDT")

    risk_score_value = int(min(100, max(0, score + max(0, max_slippage - 0.5) * 12)))
    st.progress(risk_score_value / 100, text=f"AI Market Risk Score: {risk_score_value}/100")

    if risk_score_value < 35:
        st.success("Risk gate: LOW")
    elif risk_score_value < 65:
        st.warning("Risk gate: MODERATE")
    else:
        st.error("Risk gate: HIGH")

    st.markdown(
        '<div class="small-muted">Simulation only. This control does not place, cancel, '
        'or modify any Binance order.</div>', unsafe_allow_html=True
    )

    # -------- AI command center --------
    signal = "WAIT / OBSERVE"
    if risk_score_value >= 70:
        signal = "RISK BLOCK"
    elif price_change > 1.2 and imbalance > 0.10:
        signal = "BULLISH MOMENTUM"
    elif price_change < -1.2 and imbalance < -0.10:
        signal = "BEARISH PRESSURE"
    elif abs(imbalance) < 0.05:
        signal = "NEUTRAL / BALANCED"
    rationale = (
        f"24H {price_change:+.2f}% · order-book imbalance {imbalance:+.1%} · spread {spread_pct:.3f}% · risk {risk_score_value}/100"
    )
    st.markdown(f"""<div class="ai-panel">
      <div class="ai-title">◈ AI SENTINEL DECISION LAYER</div>
      <div class="ai-signal">{signal}</div>
      <div class="small-muted" style="margin-top:6px">{rationale}</div>
      <div style="margin-top:10px"><span class="badge">SAFE MODE</span> <span class="badge">NO LIVE ORDERS</span> <span class="badge">RULE-BASED AI ENGINE</span></div>
    </div>""", unsafe_allow_html=True)

    # -------- Recent trades --------
    st.markdown('<div class="section-title">⚡ Recent Trades</div>', unsafe_allow_html=True)
    try:
        trades = recent_trades(selected_symbol, 20)
        tdf = pd.DataFrame(trades)
        if not tdf.empty:
            tdf["Price"] = pd.to_numeric(tdf["price"], errors="coerce")
            tdf["Qty"] = pd.to_numeric(tdf["qty"], errors="coerce")
            tdf["Side"] = tdf["isBuyerMaker"].map(lambda x: "SELL" if x else "BUY")
            tdf["Notional"] = tdf["Price"] * tdf["Qty"]
            tdf["Time"] = pd.to_datetime(tdf["time"], unit="ms").dt.strftime("%H:%M:%S")
            tdf["Price"] = tdf["Price"].map(lambda x: f"${x:,.6f}" if x < 1 else f"${x:,.4f}")
            tdf["Qty"] = tdf["Qty"].map(lambda x: f"{x:,.5f}")
            tdf["Notional"] = tdf["Notional"].map(lambda x: f"${x:,.2f}")
            st.dataframe(tdf[["Time","Side","Price","Qty","Notional"]].head(12),
                         use_container_width=True, hide_index=True)
    except Exception as e:
        st.caption(f"Recent trades waiting: {e}")


# -------------------- Account dashboard --------------------
st.divider()
st.markdown(f'<div class="section-title">💼 {account_label} Dashboard</div>', unsafe_allow_html=True)

active_account = st.session_state.subaccount if account_mode == "Master → Sub-account" else st.session_state.account
active_error = st.session_state.subaccount_error if account_mode == "Master → Sub-account" else st.session_state.account_error
active_status = ("Connected" if st.session_state.subaccount else "Offline") if account_mode == "Master → Sub-account" else st.session_state.account_status
active_sync = st.session_state.subaccount_last_check if account_mode == "Master → Sub-account" else st.session_state.account_last_check

if active_status == "Connected" and active_account:
    adf = account_summary(active_account)
    total_value = float(adf["USDT Value"].sum()) if not adf.empty else 0.0
    free_value = float(adf["Free USDT Value"].sum()) if not adf.empty else 0.0
    locked_value = float(adf["Locked USDT Value"].sum()) if not adf.empty else 0.0

    st.markdown(f"""<div class="sub-card">
      <div class="ai-title">● LIVE BALANCE VAULT</div>
      <div style="font-size:32px;font-weight:800;margin-top:6px">{total_value:,.2f} <span style="font-size:14px;color:#929aa5">USDT EST.</span></div>
      <div class="small-muted">{account_label} · last sync {datetime.fromtimestamp(active_sync).strftime('%H:%M:%S')}</div>
    </div>""", unsafe_allow_html=True)

    a1, a2, a3, a4 = st.columns(4)
    with a1: st.metric("Total Value", f"{total_value:,.2f} USDT")
    with a2: st.metric("Free Value", f"{free_value:,.2f} USDT")
    with a3: st.metric("Locked Value", f"{locked_value:,.2f} USDT")
    with a4: st.metric("Assets", f"{len(adf)}")

    if adf.empty:
        st.info("API connected, but no non-zero asset balance was returned.")
    else:
        display = adf.copy()
        for c in ["Free", "Locked", "Total"]:
            display[c] = display[c].map(lambda x: f"{x:.8f}")
        for c in ["Free USDT Value", "Locked USDT Value", "USDT Value"]:
            display[c] = display[c].map(lambda x: f"{x:,.2f}")
        st.dataframe(display, use_container_width=True, hide_index=True)

    if account_mode == "Master → Sub-account":
        st.success("Sub-account balance is being read from Binance's master-account sub-account asset endpoint.")
    elif agentic_confirmed:
        st.success("Agentic/Sub-account label enabled. The API key itself must belong to that account.")
    else:
        st.info("Direct mode shows the account represented by the API key.")
else:
    st.error("❌ Binance account balance is not connected.")
    if active_error:
        st.code(active_error, language="text")
    st.markdown(
        '<div class="small-muted"><b>-2015</b>: verify HMAC key type, matching secret, '
        'IP allowlist, and required USER_DATA/account permission. Never paste API secrets into chat.</div>',
        unsafe_allow_html=True
    )

# -------------------- Footer --------------------
st.divider()
st.markdown(
    '<div class="small-muted" style="text-align:center">'
    'GUARDAGENT OS v5.0 • AI Command Center • Real-time market intelligence • Binance account monitoring • '
    '<b>SAFE MODE / NO LIVE ORDERS</b>'
    '</div>',
    unsafe_allow_html=True
)


# -------------------- Auto refresh --------------------
if st_autorefresh is not None:
    st_autorefresh(interval=1500, key="guardagent_v5_refresh")
else:
    st.caption("Install streamlit-autorefresh for automatic 1.5s UI refresh.")

# Refresh private account data slowly to avoid API hammering.
if account_mode == "Master → Sub-account":
    if subaccount_email and time.time() - st.session_state.subaccount_last_check > 60:
        refresh_subaccount(subaccount_email, force=True)
else:
    if time.time() - st.session_state.account_last_check > 60:
        refresh_account(force=True)
