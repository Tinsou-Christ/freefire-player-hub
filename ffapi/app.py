"""API Christus Store — Free Fire Info (compatible avec la commande `ffinfo`).

Endpoints :
  GET /                            -> site web (recherche par UID)
  GET /health                      -> statut
  GET /api/servers                 -> liste des serveurs supportés
  GET /api/ffinfo?uid=&server=     -> JSON complet (brut + résumé texte)
  GET /api/ffinfo/text?uid=&server= -> texte brut façon commande ffinfo
  GET /api/profile-image?uid=      -> image de profil (proxy)
"""

import os

import requests
from flask import Flask, Response, jsonify, request, send_from_directory
from flask_cors import CORS

from ffdata import (
    COMMUNITY_API_KEY,
    COMMUNITY_INFO_URL,
    SERVER_LABELS,
    SERVERS,
    UPSTREAM_IMAGE_URL,
    UPSTREAM_INFO_URL,
    USER_AGENT,
    build_summary,
    credit_status,
    normalize_keys,
    pet_name,
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/static")
CORS(app)


def _bad(message, code=400, **extra):
    payload = {"success": False, "error": message}
    payload.update(extra)
    return jsonify(payload), code


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "status": "active",
            "service": "Christus Store — Free Fire Info API",
            "version": "2.0.0",
            "sources": _source_names(),
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
    return jsonify(
        {
            "success": True,
            "servers": sorted(SERVERS.keys()),
            "labels": SERVER_LABELS,
        }
    )


# ---------------------------------------------------------------- upstream


def _source_names():
    names = ["ffapii"]
    if COMMUNITY_API_KEY:
        names.append("freefirecommunity")
    return names


def _looks_valid(payload):
    return bool(isinstance(payload, dict) and payload.get("basicinfo"))


def _get_json(url, params, headers=None):
    resp = requests.get(
        url,
        params=params,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json", **(headers or {})},
        timeout=20,
    )
    resp.raise_for_status()
    return normalize_keys(resp.json())


def _fetch(uid, server_key):
    """Essaie chaque source jusqu'à obtenir des données valides."""
    region = SERVERS[server_key]
    attempts = [
        ("ffapii", UPSTREAM_INFO_URL, {"server": region, "uid": uid}, None),
    ]
    if COMMUNITY_API_KEY:
        attempts.append(
            (
                "freefirecommunity",
                COMMUNITY_INFO_URL,
                {"region": region, "uid": uid},
                {"x-api-key": COMMUNITY_API_KEY},
            )
        )

    errors = []
    for name, url, params, headers in attempts:
        try:
            data = _get_json(url, params, headers)
        except requests.HTTPError as exc:
            detail = ""
            if exc.response is not None:
                detail = (exc.response.text or "")[:200]
            errors.append(f"{name}: HTTP {getattr(exc.response, 'status_code', '?')} {detail}")
            continue
        except requests.RequestException as exc:
            errors.append(f"{name}: {type(exc).__name__}")
            continue
        except ValueError:
            errors.append(f"{name}: réponse non-JSON")
            continue

        if _looks_valid(data):
            return data, name, errors

        message = data.get("message") or data.get("error") if isinstance(data, dict) else None
        errors.append(f"{name}: {message or 'aucune donnée joueur'}")

    return None, None, errors


def _resolve_params():
    """Accepte ?uid=&server= ou le format de la commande : ?q=uid | SERVER."""
    uid = (request.args.get("uid") or "").strip()
    server_key = (request.args.get("server") or request.args.get("region") or "").strip().upper()

    raw = (request.args.get("q") or "").strip()
    if raw and "|" in raw:
        left, right = raw.split("|", 1)
        uid = uid or left.strip()
        server_key = server_key or right.strip().upper()
    elif raw and not uid:
        uid = raw

    return uid, server_key


@app.route("/api/ffinfo", methods=["GET"])
def ffinfo():
    uid, server_key = _resolve_params()
    if not uid:
        return _bad("UID requis. Exemple : /api/ffinfo?uid=1234567890&server=IND")
    if not uid.isdigit():
        return _bad("UID invalide : uniquement des chiffres.")
    if not server_key:
        server_key = "IND"
    if server_key not in SERVERS:
        return _bad("Serveur invalide. Disponibles : " + ", ".join(sorted(SERVERS.keys())))

    data, source, errors = _fetch(uid, server_key)

    if data is None:
        joined = " | ".join(errors) or "aucune source disponible"
        if any("aucune donnée joueur" in e for e in errors):
            return _bad(
                f"Joueur introuvable sur le serveur {server_key}. Vérifiez l'UID et la région.",
                404,
                details=errors,
            )
        return _bad(
            "Les serveurs Free Fire sont momentanément indisponibles. Réessayez dans un instant.",
            502,
            details=errors,
            hint=(
                "Ajoutez la variable d'environnement FF_API_KEY "
                "(clé gratuite freefirecommunity) pour activer la source de secours."
            ),
            upstream=joined,
        )

    basic = data.get("basicinfo") or {}
    pet = data.get("petinfo") or {}
    credit = (data.get("creditscoreinfo") or {}).get("creditscore")

    return jsonify(
        {
            "success": True,
            "uid": uid,
            "server": server_key,
            "source": source,
            "profileImage": f"/api/profile-image?uid={uid}",
            "player": {
                "nickname": basic.get("nickname"),
                "level": basic.get("level"),
                "likes": basic.get("liked"),
                "region": basic.get("region"),
                "brRank": basic.get("rank"),
                "csRank": basic.get("csrank"),
                "petName": pet_name(pet.get("id")),
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
    return Response(payload.get_json()["summary"], mimetype="text/plain; charset=utf-8")


@app.route("/api/profile-image", methods=["GET"])
def profile_image():
    uid = (request.args.get("uid") or "").strip()
    if not uid.isdigit():
        return _bad("UID invalide.")
    try:
        resp = requests.get(
            UPSTREAM_IMAGE_URL,
            params={"uid": uid},
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return send_from_directory(STATIC_DIR, "logo.png")
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
