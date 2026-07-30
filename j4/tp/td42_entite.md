# TD 4.2 : cartographie d'une entité publique

Entité : **TotalEnergies**. Fiche dans `fiche_entite.json`, produite par `td42_entite.py`.

## Pourquoi cette entité

Le sujet demande une entreprise du CAC40 ou une institution publique, et cite TotalEnergies en
exemple. Je l'ai gardée pour deux raisons. Les trois sources répondent, et sa page Wikipédia est
très fournie, ce qui donne une infobox riche à analyser.

## Ce que donnent les trois sources

| Source | Résultat |
| --- | --- |
| SIRENE | SIREN, dénomination, adresse du siège, code NAF, date de création, tranche d'effectif |
| Wikipédia | 24 entrées d'infobox et le paragraphe d'introduction |
| Google News | 10 articles avec titre, source, date et lien |

L'infobox contient des champs utiles pour une fiche de renseignement, comme `Création` (1924),
`Ancien nom` (Compagnie française des pétroles), `Dates clés` (privatisation en 1993, absorption de
Petrofina en 1999), `Forme juridique`, `Siège social`, `Direction`, `Actionnaires`, `Filiales`.

## Deux corrections dans le code du sujet

**L'API SIRENE du sujet n'existe plus.** L'adresse `api.annuaire-entreprises.data.gouv.fr` ne
résout pas en DNS, l'erreur renvoyée était un `NameResolutionError`. La nouvelle adresse est
`recherche-entreprises.api.gouv.fr/search`, et elle renvoie exactement les mêmes noms de champs,
donc une seule ligne à changer.

**L'introduction Wikipédia commençait au milieu d'une phrase** :

```
dont Argedis, Servauto (Total Belgique), AS24, Elan, Elf, Hutchinson, Sunpower...
```

Le sélecteur `#mw-content-text p` attrapait un paragraphe situé **dans l'infobox**, qui vient avant
le vrai texte dans le document. J'ai ajouté `section >` pour ne garder que les paragraphes enfants
directs d'une section :

```python
for p in soup.select("#mw-content-text section > p"):
```

On obtient maintenant la bonne phrase, « TotalEnergies SE, ancienne Compagnie française des
pétroles (CFP), puis Total, est une multinationale française... »

## Le SIREN trouvé n'est pas celui de la maison mère

Le code du sujet interroge l'API avec `limit=1`, donc il garde le premier des **632 résultats**. Ce
premier résultat est **TOTALENERGIES MARKETING FRANCE**, SIREN 531680445, une filiale de
distribution basée à Nanterre.

Les 10 premiers résultats sont tous des filiales, Charging Services, Renouvelables France, Proxi
Nord Ouest, Solar France, Lubrifiants. La maison mère n'apparaît pas dans le haut de la liste.

Augmenter `limit` ne suffit donc pas. Ce qui marche, c'est de préciser la **forme juridique** dans
la recherche. En cherchant `TotalEnergies SE`, le premier résultat devient :

```
542051180 | TOTALENERGIES SE (TOTALENERGIE SE) | categorie GE
```

Le `GE` signifie grande entreprise. Pour obtenir le groupe plutôt qu'une filiale :

```
python td42_entite.py TotalEnergies SE
```

## Ce que la presse ramène

Les 10 articles récupérés méritent d'être regardés de près.

| Source | Sujet réel |
| --- | --- |
| Les Echos | projet d'extraction de gaz, activité de l'entreprise |
| Le Monde.fr | appel d'une décision de justice |
| Jeune Afrique | stratégie des majors pétrolières |
| ladepeche.fr | bénéfices et prix des carburants |
| Cyclism'Actu | Tony Gallopin et le Tour de France |
| Velo-Club | avenir de l'équipe cycliste |
| TotalEnergies.com | webzine des actionnaires |

Trois observations.

**Deux articles sur dix parlent de vélo.** TotalEnergies sponsorise une équipe cycliste, donc son
nom apparaît dans la presse sportive sans rapport avec son activité. Un filtre par mot-clé ne peut
pas faire la différence.

**Un article vient du site de l'entreprise elle-même.** Le webzine des actionnaires publié sur
TotalEnergies.com se retrouve dans un flux de presse. Ce n'est pas une source indépendante.

**Le reste est pertinent** et couvre la justice, les résultats financiers et la stratégie
industrielle.

## Pour lancer le script

```
python td42_entite.py TotalEnergies
```

## Les fichiers

`td42_entite.py` pour le script et `fiche_entite.json` pour la fiche.

Les trois réponses aux questions du sujet sont dans `ETHIQUE.md`.
