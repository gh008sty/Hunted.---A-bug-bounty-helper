from flask import Flask, render_template, request, jsonify
import requests
import random
import urllib.parse

app = Flask(__name__)

# --- Payloads and User-Agent Pool ---
sql_payloads = ["' OR '1'='1", "' OR 1=1 --", "' OR 1=1#", "\" OR \"1\"=\"1", "admin'--", "admin' #"]
xss_payloads = ["<script>alert('XSS')</script>", "'><script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "javascript:alert('XSS')", "<svg onload=alert('XSS')>"]
directories = ["admin", "backup", "login", "config", "test", "uploads"]
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
]

# --- Helper Functions ---
def get_headers():
    return {'User-Agent': random.choice(user_agents)}

# --- SQL Injection Scanner ---
def sql_injection_scanner(target):
    results = []
    for payload in sql_payloads:
        test_url = target + payload
        try:
            response = requests.get(test_url, headers=get_headers(), timeout=10)
            if response.status_code == 200 and "syntax error" not in response.text.lower():
                results.append(f"Potential SQL Injection: {test_url}")
        except Exception as e:
            results.append(f"Error testing payload '{payload}': {e}")
    return results

# --- XSS Scanner ---
def xss_scanner(target):
    results = []
    for payload in xss_payloads:
        encoded_payload = urllib.parse.quote(payload)
        test_url = target + encoded_payload
        try:
            response = requests.get(test_url, headers=get_headers(), timeout=10)
            if payload in response.text:
                results.append(f"Potential XSS: {test_url}")
        except Exception as e:
            results.append(f"Error testing payload '{payload}': {e}")
    return results

# --- Directory Brute-Forcing ---
def directory_bruteforce(target):
    results = []
    for directory in directories:
        test_url = f"{target.rstrip('/')}/{directory}/"
        try:
            response = requests.get(test_url, headers=get_headers(), timeout=10)
            if response.status_code == 200:
                results.append(f"Directory found: {test_url}")
        except Exception as e:
            results.append(f"Error accessing {test_url}: {e}")
    return results

# --- Flask Routes ---
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    target = request.form.get('target')
    scan_type = request.form.get('scan_type')

    if not target:
        return jsonify({"error": "Target URL is required!"})

    if scan_type == "sql":
        results = sql_injection_scanner(target)
    elif scan_type == "xss":
        results = xss_scanner(target)
    elif scan_type == "directory":
        results = directory_bruteforce(target)
    else:
        results = ["Invalid scan type selected."]

    return jsonify({"results": results})

# --- Run the Flask App ---
if __name__ == '__main__':
    app.run(debug=True)
