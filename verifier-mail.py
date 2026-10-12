#!/usr/bin/env python3
"""
Contrôle du mail Regain — à lancer APRÈS CHAQUE MODIFICATION.

POURQUOI CE FICHIER
-------------------
Le 12/10/2026, deux fois de suite, une modification a emporté un morceau que le
propriétaire avait validé et que personne n'avait demandé de retirer :
  * « ce sera votre outil autant que le mien »  (parti avec la question du prix)
  * « notre aventure »                          (parti avec un changement de clôture)

Sa réaction : « arrête d'enlever des choses que je t'ai pas dites !! on refait à
chaque fois c'est chiant ! »

➡️ La règle : une demande nomme UN élément. On édite cet élément, et rien d'autre.
➡️ Et on ne se fie pas à sa mémoire : ce script relit le fichier et le PROUVE.

Sortie : 0 si tout va bien, 1 sinon.
"""
import re
import sys
import pathlib

FICHIER = pathlib.Path(__file__).parent / "mail-regain.html"

# ── Ce qui DOIT rester. Chaque ligne est une phrase validée par le propriétaire.
#    Si l'une disparaît, le script échoue : elle a été retirée sans qu'on le demande.
PROTEGE = {
    "l'auteur se nomme":              "Je m'appelle Thomas",
    "le projet est nommé":            "Je lance <strong style=\"color:#1e2822;\">Regain</strong>",
    "ce que fait Regain (1)":         "relance les devis rest&eacute;s sans r&eacute;ponse",
    "ce que fait Regain (2)":         "rattrape les appels manqu&eacute;s",
    "la cible du métier":             "les deux fuites qui co&ucirc;tent le plus cher",
    "il ne cherche pas des clients":  "Je ne cherche pas des clients",
    "le nombre de places":            "dix entreprises du paysage",
    "le mot ambassadrices":           "ambassadrices",
    "l'échange : la remise":          "&minus;50 % sur le tarif final, &agrave; vie",
    "l'échange : le retour":          "Votre retour passe dans la version suivante",
    "leur produit":                   "Ce sera votre outil autant que le mien",
    "pas de paiement au début":       "Rien &agrave; payer avant qu'il ait relanc&eacute; un vrai devis",
    "l'aventure":                     "faire partie de notre aventure",
    "l'invitation à cliquer":         "cliquez sur le lien ci-dessous",
    "la prise de contact":            "premi&egrave;re prise de contact",
    "ce qui suit":                    "Je vous expliquerai tout en d&eacute;tail",
    "le libellé du bouton":           "Je veux en faire partie",
    "la signature":                   ">Thomas</strong>",
    "la sortie de liste":             "r&eacute;pondez simplement &laquo; stop &raquo;",
    "l'en-tête du mail":              "__REGEX__" + r"uppercase[^>]*>\s*Regain\s*</span>",
    "le lien vers la prise de contact": "https://paysage.nj-secure.fr/prise-de-contact.html",
    "le pré-en-tête":                 "construit avec dix entreprises du m&eacute;tier",
}

# ── Ce qui ne doit JAMAIS apparaître : ça inquiète, ou c'est une faute.
INTERDIT = {
    "un accès à ouvrir":        r"ouvre\s+l.acc",
    "un mailto au lieu d'une page": r"mailto:",
    "le mot accès":             r"\bacc[eè]s\b",
    "un compte":                r"\bcompte\b",
    "une inscription":          r"\binscription\b",
    "un contrat":               r"\bcontrat\b",
    "un engagement":            r"\bengagement\b",
    "un abonnement":            r"\babonnement\b",
    "un montant en euros":      r"\d+[\s,.]?\d*\s*&euro;|&euro;\s*par mois",
    "une échéance inventée":    r"quelques semaines|dans \d+ (jours|semaines|mois)",
    "un infinitif à la place":  r"\bcliquer\b|\br[ée]pondre\b\s+simplement\s+&agrave;",
    "une question de prix":     r"ce qui vous para[iî]trait juste",
}


def texte_visible(html: str) -> str:
    """Le texte que le destinataire lit, balises retirées."""
    t = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", t).strip()


def main() -> int:
    if not FICHIER.exists():
        print(f"⛔ {FICHIER} est introuvable")
        return 1

    html = FICHIER.read_text(encoding="utf-8")
    erreurs: list[str] = []

    print("═" * 66)
    print("CONTRÔLE DU MAIL — éléments validés")
    print("═" * 66)
    for quoi, marque in PROTEGE.items():
        if marque.startswith("__REGEX__"):
            present = re.search(marque[len("__REGEX__"):], html, re.S) is not None
        else:
            present = marque in html
        if present:
            print(f"   ✅ {quoi}")
        else:
            print(f"   ⛔ {quoi}  ← DISPARU, personne ne l'a demandé")
            erreurs.append(quoi)

    print()
    print("─" * 66)
    print("MOTS INTERDITS")
    print("─" * 66)
    for quoi, motif in INTERDIT.items():
        trouve = re.search(motif, html, re.I)
        if trouve:
            extrait = html[max(0, trouve.start() - 45): trouve.end() + 35].replace("\n", " ")
            print(f"   ⛔ {quoi}  →  …{extrait.strip()}…")
            erreurs.append(quoi)
        else:
            print(f"   ✅ {quoi} — absent")

    print()
    print("─" * 66)
    print("MESURES")
    print("─" * 66)
    visible = texte_visible(html)
    mots_visibles = len([m for m in visible.split() if m])
    print(f"   Texte visible   : {len(visible)} caractères, ~{mots_visibles} mots")
    print(f"   Liens           : {len(re.findall(r'href=', html))}")
    liens = set(re.findall(r'href="([^"]+)"', html))
    print(f"   Destinations    : {'toutes vers la prise de contact ✅' if liens == {'https://paysage.nj-secure.fr/prise-de-contact.html'} else '⚠️ ' + str(liens)}")
    print(f"   Taille fichier  : {len(html)} caractères")

    print()
    if erreurs:
        print(f"⛔ {len(erreurs)} PROBLÈME(S) : {', '.join(erreurs)}")
        print("➡️ Remets ce qui a disparu, ou demande au propriétaire avant de retirer.")
        return 1
    print("✅ Tout est là. Rien d'interdit. Le mail peut partir.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
