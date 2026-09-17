import os
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for

from pkce import generer_code_verifier

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-change-me")

CLIENT_ID = os.environ["MAL_CLIENT_ID"]
CLIENT_SECRET = os.environ["MAL_CLIENT_SECRET"]
REDIRECT_URI = os.environ.get("REDIRECT_URI", "http://127.0.0.1:5000/callback")

AUTHORIZE_URL = "https://myanimelist.net/v1/oauth2/authorize"
TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
API_BASE = "https://api.myanimelist.net/v2"


@app.route("/")
def accueil():
    token = session.get("access_token")
    if not token:
        return render_template("index.html", connecte=False, erreur=request.args.get("erreur"))

    reponse = requests.get(
        f"{API_BASE}/users/@me/animelist",
        params={"fields": "list_status", "limit": 30, "sort": "list_updated_at"},
        headers={"Authorization": f"Bearer {token}"},
    )

    if reponse.status_code != 200:
        session.clear()
        return render_template("index.html", connecte=False, erreur="Session expirée, reconnecte-toi.")

    animes = reponse.json().get("data", [])
    return render_template("index.html", connecte=True, animes=animes)


@app.route("/login")
def login():
    code_verifier = generer_code_verifier()
    session["code_verifier"] = code_verifier

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "code_challenge": code_verifier,
        "code_challenge_method": "plain",
        "redirect_uri": REDIRECT_URI,
    }
    return redirect(f"{AUTHORIZE_URL}?{urlencode(params)}")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    code_verifier = session.get("code_verifier")

    if not code or not code_verifier:
        return redirect(url_for("accueil", erreur="Connexion annulée ou expirée."))

    reponse = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": REDIRECT_URI,
        },
    )

    if reponse.status_code != 200:
        return redirect(url_for("accueil", erreur="Échec de l'échange du code contre un jeton."))

    jetons = reponse.json()
    session["access_token"] = jetons["access_token"]
    session["refresh_token"] = jetons.get("refresh_token")
    session.pop("code_verifier", None)

    return redirect(url_for("accueil"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("accueil"))


if __name__ == "__main__":
    app.run(debug=True)
