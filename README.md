# Flask Service Monitoring with Prometheus & Grafana  

## 📌 Overview  
This project demonstrates how to **monitor Python Flask services** using **Prometheus** metrics and visualize them with **Grafana**.  

It includes:  
- REST API endpoints exposed via Flask  
- Custom **Prometheus metrics** (request count, success/failure, latency, circuit breaker state, etc.)  
- **Histogram-based latency tracking**  
- **Integration with Prometheus** for scraping metrics  
- (Optional) **Grafana dashboards** for visualization  

---

## ⚙️ Features  

- **Request Metrics**  
  - `service_requests_total` → total requests (labeled by `service` and `status`)  
  - `service_requests_created` → timestamp of last request  
- **Latency Metrics**  
  - `service_request_latency_seconds` → histogram of request durations  
- **Circuit Breaker Metrics**  
  - `service_circuit_state` → tracks service state (0=Closed, 1=Open, 2=Half-Open)  
- **Python Runtime Metrics** (via `prometheus_client`)  
  - `python_gc_objects_collected_total` → garbage collector stats  
  - `python_info` → Python runtime version  

---

## 🛠️ Tech Stack  
- **Backend**: Python, Flask  
- **Monitoring**: Prometheus  
- **Visualization**: Grafana (optional)  
- **Metrics Exporter**: `prometheus_client`  

---

## 🚀 Setup & Run  

### 1. Clone Repository  
```bash
git clone https://github.com/your-username/flask-prometheus-monitoring.git
cd flask-prometheus-monitoring
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Flask Service  
Start the Flask application:  

```bash
python app.py
```
By default, it will run at:

API Base URL → http://localhost:5000

Metrics Endpoint → http://localhost:5000/metrics

### 4. Run Prometheus  
Make sure you have Prometheus installed. Then start Prometheus with your config file:  

```bash
./prometheus --config.file=prometheus.yml
```

By default, Prometheus runs at:

http://localhost:9090

You should now be able to query metrics like:

service_requests_total → total API requests

service_request_latency_seconds_bucket → request latency histogram

service_circuit_state → circuit breaker state


### 5. Setup Grafana (Optional but Recommended)  

1. **Install Grafana**  
   👉 [Download Grafana](https://grafana.com/grafana/download)  

2. **Run Grafana Server**  
   ```bash
   ./bin/grafana-server
  ```

3. **Open Grafana at** → [http://localhost:3000](http://localhost:3000)  
   (default login: admin/admin)

4. **Add Prometheus as a data source** → [http://localhost:9090](http://localhost:9090)

5. **Import or create dashboards to visualize metrics:**  
   - Request rate  
   - Error rate  
   - Latency histograms  
   - Circuit breaker states

