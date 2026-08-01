"""API Free Fire Info — compatible avec la commande `ffinfo`.

Endpoints :
  GET /                       -> site web (recherche par UID)
  GET /health                 -> statut
  GET /api/servers            -> liste des serveurs supportés
  GET /api/ffinfo?uid=&server= -> JSON complet (brut + résumé texte)
  GET /api/ffinfo/text?uid=&server= -> texte brut façon commande ffinfo
  GET /api/profile-image?uid= -> image de profil (proxy)
"""

import os

import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

from ffdata import (
    PET_NAMES,
    SERVERS,
    UPSTREAM_IMAGE_URL,
    UPSTREAM_INFO_URL,
    build_summary,
    credit_status,
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app)


def _bad(message, code=400):
    return jsonify({"success": False, "error": message}), code


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "active",
            "service": "Free Fire Info API",
            "version": "1.1.0",
            "endpoints": {
                "info": "/api/ffinfo?uid=<uid>&server=<server>",
                "text": "/api/ffinfo/text?uid=<uid>&server=<server>",
                "image": "/api/profile-image?uid=<uid>",
                "servers": "/api/servers",
            },
        }
    )


@app.route("/api/servers", methods=["GET"])
def servers():
    return jsonify({"success": True, "servers": sorted(SERVERS.keys())})


def _fetch(uid, server_key):
    resp = requests.get(
        UPSTREAM_INFO_URL,
        params={"server": SERVERS[server_key], "uid": uid},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def _resolve_params():
    """Accepte ?uid=&server= ou le format de la commande : ?q=uid | SERVER."""
    uid = (request.args.get("uid") or "").strip()
    server_key = (request.args.get("server") or "").strip().upper()

    raw = (request.args.get("q") or "").strip()
    if raw and "|" in raw:
        left, right = raw.split("|", 1)
        uid = uid or left.strip()
        server_key = server_key or right.strip().upper()

    return uid, server_key


@app.route("/api/ffinfo", methods=["GET"])
def ffinfo():
    uid, server_key = _resolve_params()
    if not uid or not server_key:
        return _bad(
            "UID et serveur requis. Exemple : /api/ffinfo?uid=1234567890&server=IND"
        )
    if not uid.isdigit():
        return _bad("UID invalide : uniquement des chiffres.")
    if server_key not in SERVERS:
        return _bad(
            "Serveur invalide. Disponibles : " + ", ".join(sorted(SERVERS.keys()))
        )

    try:
        data = _fetch(uid, server_key)
    except requests.RequestException:
        return _bad("Impossible de récupérer les données Free Fire.", 502)
    except ValueError:
        return _bad("Réponse invalide du service Free Fire.", 502)

    if not data or not data.get("basicinfo"):
        return _bad("Joueur introuvable.", 404)

    basic = data["basicinfo"]
    pet = data.get("petinfo") or {}
    credit = (data.get("creditscoreinfo") or {}).get("creditscore")

    return jsonify(
        {
            "success": True,
            "uid": uid,
            "server": server_key,
            "profileImage": f"/api/profile-image?uid={uid}",
            "player": {
                "nickname": basic.get("nickname"),
                "level": basic.get("level"),
                "likes": basic.get("liked"),
                "region": basic.get("region"),
                "brRank": basic.get("rank"),
                "csRank": basic.get("csrank"),
                "petName": PET_NAMES.get(pet.get("id"), "Unknown"),
                "clan": (data.get("clanbasicinfo") or {}).get("clanname"),
                "creditScore": credit,
                "creditStatus": credit_status(credit),
            },
            "summary": build_summary(data, server_key),
            "raw": data,
        }
    )


@app.route("/api/ffinfo/text", methods=["GET"])
def ffinfo_text():
    payload = ffinfo()
    if isinstance(payload, tuple):
        body, code = payload
        return Response(
            body.get_json()["error"], status=code, mimetype="text/plain; charset=utf-8"
        )
    return Response(
        payload.get_json()["summary"], mimetype="text/plain; charset=utf-8"
    )


@app.route("/api/profile-image", methods=["GET"])
def profile_image():
    uid = (request.args.get("uid") or "").strip()
    if not uid.isdigit():
        return _bad("UID invalide.")
    try:
        resp = requests.get(UPSTREAM_IMAGE_URL, params={"uid": uid}, timeout=10)
        resp.raise_for_status()
    except requests.RequestException:
        return _bad("Image de profil indisponible.", 502)
    return Response(
        resp.content,
        mimetype=resp.headers.get("Content-Type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=600"},
    )


@app.errorhandler(404)
def not_found(_e):
    return _bad("Endpoint introuvable.", 404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
