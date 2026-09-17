# Clone MAL — connexion OAuth2 à MyAnimeList

Application web Flask qui se connecte à l'API MyAnimeList (OAuth2 + PKCE)
pour afficher la vraie liste d'animes de l'utilisateur connecté : couverture,
statut (en cours, terminé...), épisodes vus, note.

## Pourquoi ce projet

L'objectif était d'apprendre le fonctionnement d'OAuth2 — le mécanisme
d'authentification utilisé par la plupart des grosses API (Spotify, Google,
GitHub...) — à travers un cas réel. Spotify a été écarté en cours de route :
leur Web API nécessite désormais un compte Premium pour créer une
application, ce qui bloquait le projet pour un compte gratuit. MyAnimeList a
été choisi comme alternative : API OAuth2 gratuite et sans restriction.

## Le flux OAuth2 (Authorization Code + PKCE)

1. **Redirection vers MyAnimeList** — l'utilisateur clique "Se connecter",
   l'appli génère un `code_verifier` aléatoire et redirige vers la page
   d'autorisation MyAnimeList.
2. **L'utilisateur autorise** — il se connecte avec son propre compte MAL et
   accepte l'accès. Son mot de passe ne transite jamais par cette appli.
3. **Retour avec un code** — MyAnimeList redirige vers `/callback` avec un
   code à usage unique.
4. **Échange contre un jeton** — le serveur échange ce code (+ le
   `code_verifier` de l'étape 1) contre un `access_token`, utilisé ensuite
   pour appeler l'API au nom de l'utilisateur.

Particularité de MyAnimeList : leur implémentation PKCE n'accepte que la
méthode `plain` — le `code_challenge` envoyé à l'étape 1 est exactement la
même chaîne que le `code_verifier` renvoyé à l'étape 4 (pas de hachage
SHA256 comme sur la plupart des autres API utilisant PKCE).

## Stack technique

- **Flask** — routes `/`, `/login`, `/callback`, `/logout`
- **requests** — appels HTTP vers les endpoints OAuth et l'API MAL
- **python-dotenv** — `client_id`/`client_secret` hors du code source
- **pytest** — tests sur la génération du `code_verifier` (longueur,
  alphabet conforme à la RFC 7636, imprévisibilité)

## Installation

1. Crée une application sur [myanimelist.net/apiconfig](https://myanimelist.net/apiconfig)
   (App Type: `web`, Redirect URL: `http://127.0.0.1:5000/callback`)
2. Copie `.env.example` vers `.env` et renseigne ton `MAL_CLIENT_ID` et
   `MAL_CLIENT_SECRET`
3. Installe les dépendances :
```
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```
4. Lance le serveur :
```
python app.py
```
5. Ouvre `http://127.0.0.1:5000` et connecte-toi avec ton compte MyAnimeList.

## Lancer les tests

```
pytest
```

Les tests portent uniquement sur `pkce.py` (logique pure, sans réseau ni
`.env` requis) : longueur du `code_verifier`, alphabet conforme, et
imprévisibilité d'un appel à l'autre.

## Structure du projet

```
clone-mal/
├── app.py                # routes Flask, flux OAuth2 (login/callback)
├── pkce.py                 # génération du code_verifier (RFC 7636)
├── test_app.py               # tests sur pkce.py
├── templates/index.html        # page de connexion / grille d'animes
└── requirements.txt
```

## Limitations connues

- Le rafraîchissement automatique du jeton (`refresh_token`, valable un
  mois) n'est pas implémenté — après expiration de l'`access_token`
  (une heure), il faut simplement se reconnecter.
