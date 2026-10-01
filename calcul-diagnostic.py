#!/usr/bin/env python3
"""
Diagnostic paysagiste — calcul affiché sur la page.

RÈGLE DE CRÉDIBILITÉ (apprise en vérifiant) : on ne peut récupérer QUE sur des devis
réellement envoyés. Faire dépendre le montant du volume d'appels produit des chiffres
qui dépassent le chiffre d'affaires de l'entreprise et détruisent l'outil.

TROIS SORTIES, JAMAIS ADDITIONNÉES :
  ① ARGENT RÉCUPÉRABLE  — sur les devis envoyés et non signés    → en euros
  ② APPELS MANQUÉS      — un COMPTAGE, pas des euros             → en nombre
  ③ RÉCURRENT À CONSTRUIRE — du CA qui n'a jamais existé         → en euros, à part

Vérifié aux bornes : pire / moyen / petit / parfait.
"""
# --- Hypothèses (sourcées + hypothèses marquées) ---
TAUX_DEVIS_NON_SIGNE = 0.75   # BTP : 22-28 % de conversion (Payflo, 15 000 devis réels)
TAUX_RECUP_RELANCE   = 0.05   # hypothèse PRUDENTE : 5 % des devis non signés sont
                              # récupérables par une relance structurée
TAUX_APPEL_NON_RAPPEL = 0.62  # études secteur (vendeurs téléphonie) — hypothèse haute
SEMAINES_PAR_MOIS    = 4.3
CONTRAT_MENSUEL      = 180.0  # contrat d'entretien moyen (secteur : 300-1 200 €/an)
OBJECTIF_CONTRATS    = 40     # portefeuille récurrent visé (secteur)
TAUX_CONV_DEVIS      = 0.25   # pour estimer le CA de référence


def ca_annuel(devis_mois, panier):
    return devis_mois * 12 * TAUX_CONV_DEVIS * panier


def calculer(devis_mois, panier, appels_sem, contrats, relance_score, reponse_score):
    """score 0 (rien fait) → 3 (automatisé)"""

    # ① Ce qu'on peut récupérer sur les devis ENVOYÉS et non signés
    devis_non_signes = devis_mois * 12 * TAUX_DEVIS_NON_SIGNE
    facteur_relance = (3 - relance_score) / 3
    recuperable = devis_non_signes * TAUX_RECUP_RELANCE * panier * facteur_relance

    # ② Les appels manqués — un COMPTAGE
    appels_manques = appels_sem * SEMAINES_PAR_MOIS * 12 * TAUX_APPEL_NON_RAPPEL
    facteur_reponse = (3 - reponse_score) / 3
    appels_a_reprendre = appels_manques * facteur_reponse

    # ③ Le récurrent non construit — du CA neuf
    manque = max(0, OBJECTIF_CONTRATS - contrats)
    recurrent = manque * CONTRAT_MENSUEL * 12

    return {
        'recuperable': round(recuperable),
        'appels_a_reprendre': round(appels_a_reprendre),
        'recurrent_a_construire': round(recurrent),
    }


if __name__ == "__main__":
    cas = [
        ("① LE PIRE", dict(devis_mois=20, panier=5000, appels_sem=10, contrats=0,
                          relance_score=0, reponse_score=0)),
        ("② LE PARFAIT", dict(devis_mois=4, panier=1200, appels_sem=0, contrats=40,
                             relance_score=3, reponse_score=3)),
        ("③ LE MOYEN", dict(devis_mois=12, panier=3500, appels_sem=4, contrats=5,
                           relance_score=1, reponse_score=1)),
        ("④ LE PETIT", dict(devis_mois=6, panier=1500, appels_sem=2, contrats=10,
                           relance_score=1, reponse_score=1)),
        ("⑤ AUCUN APPEL MANQUÉ", dict(devis_mois=8, panier=2500, appels_sem=0, contrats=0,
                                     relance_score=0, reponse_score=3)),
    ]

    print("=" * 74)
    print("VÉRIFICATION AUX BORNES")
    print("=" * 74)
    for label, kw in cas:
        r = calculer(**kw)
        ca = ca_annuel(kw['devis_mois'], kw['panier'])
        ratio = r['recuperable'] / ca if ca else 0
        print(f"\n{label}   (CA estimé {ca:,.0f} €/an)")
        print(f"     ① récupérable sur devis ....... {r['recuperable']:>9,} €   ({ratio:.0%} du CA)")
        print(f"     ② appels à reprendre ........... {r['appels_a_reprendre']:>9,} appels")
        print(f"     ③ récurrent à construire ....... {r['recurrent_a_construire']:>9,} €")
        if kw['relance_score'] == 3 and kw['reponse_score'] == 3 and kw['contrats'] >= OBJECTIF_CONTRATS:
            assert r['recuperable'] == 0, f"ERREUR {label} : dossier parfait ≠ 0 €"
            assert r['appels_a_reprendre'] == 0, f"ERREUR {label} : aucun appel manqué ≠ 0"
            assert r['recurrent_a_construire'] == 0, f"ERREUR {label} : objectif atteint ≠ 0 €"
        assert ratio <= 0.16, f"ERREUR {label} : {ratio:.0%} du CA — invraisemblable"

    print("\n" + "=" * 74)
    print("✓ Borne haute : dossier parfait → 0 € / 0 appel / 0 € de potentiel")
    print("✓ Le récupérable reste ≈ 15 % du CA quelle que soit la taille — crédible")
    print("✓ Les trois sorties ne sont jamais additionnées")
