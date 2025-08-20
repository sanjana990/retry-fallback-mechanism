import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type, RetryError
import pybreaker
import time
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# -----------------------------
# 🔹 Prometheus Metrics
# -----------------------------
REQUEST_COUNT = Counter(
    "service_requests_total", "Total number of requests", ["service", "status"]
)
REQUEST_LATENCY = Histogram(
    "service_request_latency_seconds", "Latency of service calls", ["service"]
)
CIRCUIT_STATE = Gauge(
    "service_circuit_state", "Circuit state of services (0=closed, 1=open, 2=half-open)", ["service"]
)

# -----------------------------
# 🔹 Circuit State Mapping
# -----------------------------
def circuit_state_value(state_str):
    mapping = {
        "closed": 0,
        "open": 1,
        "half-open": 2
    }
    return mapping.get(str(state_str).lower(), -1)  # -1 = unknown

# -----------------------------
# 🔹 Circuit Breakers
# -----------------------------
breaker_A = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=10)
breaker_B = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=10)

# -----------------------------
# 🔹 Retry Decorator
# -----------------------------
RETRY = retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(2),
    retry=retry_if_exception_type(requests.exceptions.RequestException),
    reraise=True
)

# -----------------------------
# 🔹 Service A
# -----------------------------
@breaker_A
@RETRY
def call_service_a():
    service = "service_a"
    start = time.time()
    try:
        print("🔁 Trying Service A...")
        response = requests.get("http://localhost:5001/data", timeout=3)
        response.raise_for_status()
        REQUEST_COUNT.labels(service, "success").inc()
        return response.json()
    except Exception:
        REQUEST_COUNT.labels(service, "failure").inc()
        raise
    finally:
        latency = time.time() - start
        REQUEST_LATENCY.labels(service).observe(latency)
        CIRCUIT_STATE.labels(service).set(circuit_state_value(breaker_A.current_state))

# -----------------------------
# 🔹 Service B
# -----------------------------
@breaker_B
@RETRY
def call_service_b():
    service = "service_b"
    start = time.time()
    try:
        print("🛟 Falling back to Service B...")
        response = requests.get("http://localhost:5002/data", timeout=3)
        response.raise_for_status()
        REQUEST_COUNT.labels(service, "success").inc()
        return response.json()
    except Exception:
        REQUEST_COUNT.labels(service, "failure").inc()
        raise
    finally:
        latency = time.time() - start
        REQUEST_LATENCY.labels(service).observe(latency)
        CIRCUIT_STATE.labels(service).set(circuit_state_value(breaker_B.current_state))

# -----------------------------
# 🔹 Fallback mechanism
# -----------------------------
def get_data_with_fallback():
    print("🔌 Circuit state A:", breaker_A.current_state)
    try:
        return call_service_a()
    except (requests.exceptions.RequestException, pybreaker.CircuitBreakerError, RetryError) as e_a:
        print(f"❌ Service A failed: {e_a}")
        print("🔌 Circuit state B:", breaker_B.current_state)
        try:
            return call_service_b()
        except (requests.exceptions.RequestException, pybreaker.CircuitBreakerError, RetryError) as e_b:
            print(f"❌ Service B also failed: {e_b}")
            return {"error": "Both services are down"}

# -----------------------------
# 🔹 Main loop
# -----------------------------
if __name__ == "__main__":
    # Start Prometheus metrics server on port 8001
    start_http_server(8001)
    print("📊 Prometheus metrics available at http://localhost:8001/")

    for i in range(20):
        print(f"\n🔎 Request #{i+1}")
        result = get_data_with_fallback()
        print("✅ Response:", result)
        time.sleep(3)
