import base64
import json
import urllib.request

URL = "http://localhost:8080/instance/connect/bromodachis"
APIKEY = "bromodachisbmzxlxtser3h2027"

req = urllib.request.Request(URL, headers={"apikey": APIKEY})
with urllib.request.urlopen(req, timeout=20) as r:
    data = json.loads(r.read())

b64 = data["base64"].split(",", 1)[1]
with open("qr.png", "wb") as f:
    f.write(base64.b64decode(b64))
print("QR saved to qr.png")
print("Status:", data.get("status"))
