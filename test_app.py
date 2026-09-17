import string

from pkce import generer_code_verifier

ALPHABET_AUTORISE = set(string.ascii_letters + string.digits + "-._~")


def test_longueur_par_defaut():
    assert len(generer_code_verifier()) == 128


def test_longueur_personnalisee():
    assert len(generer_code_verifier(64)) == 64


def test_alphabet_conforme_rfc7636():
    verifier = generer_code_verifier(200)
    assert set(verifier).issubset(ALPHABET_AUTORISE)


def test_deux_appels_donnent_des_valeurs_differentes():
    # Un code_verifier prévisible casserait toute la protection PKCE.
    premier = generer_code_verifier()
    second = generer_code_verifier()
    assert premier != second
