# Diagnostic paysagiste

Page-outil publique : **6 questions, 40 secondes, un chiffre.**

Un paysagiste répond à 6 questions et découvre ce que ses devis non relancés
et ses appels manqués lui coûtent réellement.

**Aucune fonctionnalité serveur.** Une page autonome, un formulaire, un email.

---

## Comment le lien arrive chez le prospect

Le lien peut être pré-rempli avec ses chiffres :

```
index.html?d=14&p=3200&a=6&c=8&v=Hyères
```

| Paramètre | Sens | Bornes |
|---|---|---|
| `d` | devis envoyés par mois | 1 – 40 |
| `p` | panier moyen en € | 300 – 15 000 |
| `a` | appels manqués par semaine | 0 – 25 |
| `c` | contrats d'entretien en cours | 0 – 80 |
| `v` | la ville, affichée dans le bandeau | texte libre |

Le prospect ouvre sa page et voit **son** chiffre, sans qu'on ait parlé.
Un bandeau lui dit que les chiffres sont pré-remplis et qu'il peut les corriger.

---

## Le calcul

Trois sorties, **jamais additionnées** :

1. **Récupérable sur les devis non signés** — de l'argent laissé sur la table, en euros
2. **Appels à reprendre** — un comptage, en nombre
3. **Récurrent d'entretien à construire** — du chiffre d'affaires neuf, en euros

**La règle de crédibilité :** on ne peut récupérer que sur des devis **réellement envoyés**.
Le montant affiché reste autour de **15 % du CA annuel** — au-delà, il cesse d'être crédible.
**Un dossier parfait expose 0 €.**

`calcul-diagnostic.py` porte la même logique, vérifiée aux bornes
(pire / moyen / petit / parfait) **avant** d'être portée dans la page.

---

## Les hypothèses, assumées

| Hypothèse | Valeur | Origine |
|---|---|---|
| 1 devis sur 4 signé | 75 % non signés | secteur BTP — 15 000 devis réels |
| Récupérable par relance | **5 %** | **notre hypothèse, volontairement basse** |
| Appelants qui ne rappellent pas | 62 % | études télécom — **à prendre avec prudence** |
| Contrat d'entretien | 180 €/mois | milieu de la fourchette du secteur |
| Portefeuille visé | 40 contrats | repère du secteur |

Ces taux sont des **repères de marché**, pas les chiffres du prospect.
Ils sont affichés sur la page, en clair.

---

## Où vont les leads

Le formulaire poste vers **FormSubmit**, qui relaie vers une boîte Gmail.
**Aucun serveur, aucune base de données.**

⚠️ **La première soumission déclenche un email d'activation** — il faut cliquer le lien
une fois, sinon les leads suivants ne partent pas.

---

## Vérification

La page a été **jouée dans un vrai navigateur**, pas relue :

- 4 profils déroulés de bout en bout (pire / moyen / petit / parfait)
- borne haute vérifiée : dossier parfait → **0 € exposé**
- lien pré-rempli testé, bandeau affiché, champs corrigés
- syntaxe JavaScript contrôlée
- **0 erreur JS**

Le script de vérification : `verifier.mjs`.

---

## Ce que cette page ne fait pas

- elle ne stocke rien
- elle n'envoie aucun email au prospect (c'est le rôle du message qui porte le lien)
- elle ne remplace pas une comptabilité : le montant est une estimation
