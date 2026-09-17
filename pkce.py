import secrets
import string


def generer_code_verifier(longueur=128):
    """MAL n'accepte que la méthode PKCE 'plain' : le code_challenge envoyé
    à l'étape 1 est exactement la même chaîne que le code_verifier renvoyé
    à l'étape 4 (pas de hachage SHA256 comme sur la plupart des autres API).
    L'alphabet utilisé est celui autorisé par la RFC 7636 pour un code_verifier."""
    alphabet = string.ascii_letters + string.digits + "-._~"
    return "".join(secrets.choice(alphabet) for _ in range(longueur))
