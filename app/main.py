# =====================================================================
#  Acme Reports Service - INTENTIONALLY VULNERABLE. DO NOT USE IN PROD.
# =====================================================================
import hashlib
import os
import pickle
import base64
import sqlite3
import subprocess

import requests
import yaml
from flask import Flask, request, render_template_string, jsonify, make_response

app = Flask(__name__)
app.secret_key = "acme-flask-secret-key-do-not-share"          # hardcoded secret
GITHUB_TOKEN = "ghp_FAKEdemoTokenAcme0000000000000000000000"   # fake token for secrets scanning
ENABLE_RCE = os.environ.get("ENABLE_RCE_ENDPOINTS") == "true"

DB = "/tmp/reports.db"


def init_db():
    con = sqlite3.connect(DB)
    con.execute("CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY, owner TEXT, title TEXT, body TEXT)")
    con.execute("DELETE FROM reports")
    con.executemany("INSERT INTO reports (owner, title, body) VALUES (?,?,?)", [
        ("alice", "Q3 revenue", "Revenue up 12%"),
        ("bob", "Q3 churn", "Churn down 3%"),
        ("admin", "Board salaries", "CONFIDENTIAL"),
    ])
    con.commit()
    con.close()


@app.route("/")
def index():
    return """<h1>Acme Reports</h1>
    <a href="/reports?owner=alice">/reports?owner=alice</a><br>
    <a href="/greet?name=world">/greet?name=world</a>"""


# SAST + DAST: SQL injection
@app.route("/reports")
def reports():
    owner = request.args.get("owner", "")
    con = sqlite3.connect(DB)
    rows = con.execute(f"SELECT id, title, body FROM reports WHERE owner = '{owner}'").fetchall()
    return jsonify(rows)


# SAST + DAST: Server-side template injection / XSS
@app.route("/greet")
def greet():
    name = request.args.get("name", "guest")
    if not ENABLE_RCE:
        return "<h2>Hello " + name + "!</h2>"                    # safe mode: still reflected XSS
    return render_template_string("<h2>Hello " + name + "!</h2>")


# SCA REACHABLE: PyYAML 5.3.1 FullLoader RCE (CVE-2020-14343)
@app.route("/reports/import", methods=["POST"])
def import_report():
    if not ENABLE_RCE:
        return "disabled", 403
    data = yaml.load(request.data, Loader=yaml.FullLoader)
    return jsonify({"imported": str(data)[:200]})


# SAST: insecure deserialization
@app.route("/session/restore", methods=["POST"])
def restore_session():
    if not ENABLE_RCE:
        return "disabled", 403
    obj = pickle.loads(base64.b64decode(request.form["state"]))
    return jsonify({"restored": str(obj)})


# SAST: command injection
@app.route("/reports/export")
def export():
    if not ENABLE_RCE:
        return "disabled", 403
    fmt = request.args.get("format", "csv")
    out = subprocess.check_output("echo exporting as " + fmt, shell=True)
    return out


# SAST: SSRF (requests = reachable)
@app.route("/fetch")
def fetch():
    url = request.args.get("url", "https://example.com")
    r = requests.get(url, timeout=3, verify=False)               # TLS verification disabled
    return r.text[:500]


# SAST: weak hashing
@app.route("/hash")
def weak_hash():
    pw = request.args.get("pw", "")
    return hashlib.md5(pw.encode()).hexdigest()


# DAST: insecure cookie
@app.route("/login")
def login():
    resp = make_response("logged in")
    resp.set_cookie("session_id", "12345")                        # no Secure / HttpOnly / SameSite
    return resp


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    if ENABLE_RCE:
        app.run(host="0.0.0.0", port=port, debug=True)   # debug mode on (Werkzeug debugger = RCE)
    else:
        app.run(host="0.0.0.0", port=port)
