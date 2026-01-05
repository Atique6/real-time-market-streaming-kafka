import json
import time
import threading
import websocket
from confluent_kafka import Producer

# --- Binance combined trade WebSocket ---
BINANCE_SOCKET_URL = "wss://stream.binance.com:9443/stream?streams="

# --- Popular trading pairs we track ---
symbols = [
    "btcusdt", "ethusdt", "bnbusdt", "solusdt", "xrpusdt",
    "adausdt", "dogeusdt", "avaxusdt", "trxusdt", "linkusdt"
]

# Build the combined trades stream URL
streams = "/".join([f"{symbol}@trade" for symbol in symbols])
FULL_SOCKET_URL = BINANCE_SOCKET_URL + streams

# --- Kafka producer config ---
producer = Producer({'bootstrap.servers': 'localhost:9092'})

# Message counters for simple throughput stats
msg_count = 0
window_start = time.time()


# --- WebSocket callbacks ---
def on_message(ws, message):
    global msg_count, window_start
    msg_count += 1

    # Simple throughput monitor every 5000 messages
    if msg_count % 5000 == 0:
        now = time.time()
        elapsed = now - window_start
        rps = 5000 / elapsed if elapsed > 0 else 0
        print(f"\n📊 [Stats] Last 5000 msgs in {elapsed:.2f}s  {rps:.2f} msg/sec")
        window_start = now

    try:
        data = json.loads(message)
        stream = data.get("stream", "")
        symbol = stream.split("@")[0]   # e.g. "btcusdt"

        # Send to Kafka topic "binance"
        # We do NOT specify a partition, so Kafka uses the default partition 0.
        producer.produce(
            topic="binance",
            key=symbol,
            value=json.dumps(data),
        )
        producer.poll(0)  # Non blocking flush of internal queue

    except Exception as e:
        print(f"❌ Kafka send error: {e}")


def on_open(ws):
    print(f"✅ Connected to Binance WebSocket. Tracking: {', '.join(symbols)}")


def on_close(ws, code, msg):
    print("⚠️ WebSocket closed. Will reconnect...")


# --- Keep the WebSocket connection alive and auto reconnect ---
def run_forever():
    while True:
        try:
            ws = websocket.WebSocketApp(
                FULL_SOCKET_URL,
                on_open=on_open,
                on_message=on_message,
                on_close=on_close,
            )
            ws.run_forever()
        except Exception as e:
            print(f"💥 Error in WebSocket loop: {e}")
        time.sleep(5)  # wait a bit before reconnecting


if __name__ == "__main__":
    run_forever()
