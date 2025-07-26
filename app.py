import os
import random
import requests
from flask import Flask, request, Response, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

VECS_URL = "https://raw.githubusercontent.com/Belfagor2005/vavoo/refs/heads/main/data.json"
PING_URL = "https://www.vavoo.tv/api/box/ping2"

def gerar_vavoo_auth():
    try:
        veclist = requests.get(VECS_URL, timeout=10).json()
    except Exception:
        return None

    for _ in range(50):
        vec = {"vec": random.choice(veclist)}
        try:
            r = requests.post(PING_URL, json=vec, timeout=5).json()
            token = r.get("signed") or r.get("data", {}).get("signed") or r.get("response", {}).get("signed")
            if token:
                return token
        except:
            continue
    return None

@app.route("/stream/<canal_id>")
def canal(canal_id):
    if not canal_id:
        return "Erro: parâmetro ?id= está ausente", 400

    auth_token = gerar_vavoo_auth()
    if not auth_token:
        return "Erro ao gerar token vavoo_auth", 500

    stream_url = f"https://vavoo.to/live2/play/{canal_id}.ts?n=1&b=5&vavoo_auth={auth_token}"

    print(stream_url)
    
    headers = {
        "User-Agent": "VAVOO/2.6",
        "Referer": "https://www.vavoo.tv/",
        "Origin": "https://www.vavoo.tv/",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Range": "bytes=0-"
    }

    try:
        r = requests.get(stream_url, headers=headers, stream=True, timeout=10)
        if r.status_code != 200:
            return f"Erro ao acessar o canal: HTTP {r.status_code}", r.status_code

        return Response(
            r.iter_content(chunk_size=8192),
            content_type=r.headers.get("Content-Type", "video/mp2t"),
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Range",
                "Accept-Ranges": "bytes"
            }
        )
    except Exception as e:
        return f"Erro ao conectar ao stream: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
