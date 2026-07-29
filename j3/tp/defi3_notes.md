# Défi 3 : SQL et interprétation financière

Requêtes faites sur `bourse.db`, la base remplie par le spider du TD 3.2. Elle contient
26 actions, relevées le 29/07/2026 vers 12h31.

J'ai tout lancé avec le client `sqlite3` :

```
sqlite3 bourse.db
```

L'export demandé est dans `j3/tp/boursorama/analyse_bourse.csv`.

## Top 5 des hausses

```sql
SELECT libelle, variation, cours
FROM actions
ORDER BY variation DESC LIMIT 5;
```

| libellé | variation | cours |
| --- | --- | --- |
| ALTEN | +20,06 % | 80,20 |
| SOPRA STERIA | +12,54 % | 193,80 |
| KERING | +12,32 % | 281,35 |
| BUREAU VERITAS | +8,13 % | 29,54 |
| ATOS GROUP | +5,64 % | 33,72 |

## Top 5 des baisses : la requête ne peut pas marcher

```sql
SELECT libelle, variation, cours
FROM actions
ORDER BY variation ASC LIMIT 5;
```

| libellé | variation | cours |
| --- | --- | --- |
| MEDINCELL | +1,35 % | 25,58 |
| UBISOFT | +1,35 % | 5,55 |
| ERAMET | +1,38 % | 42,76 |
| EURAZEO | +1,39 % | 46,72 |
| MERCIALYS | +1,50 % | 12,16 |

**Aucune de ces valeurs n'est en baisse.** Je l'ai vérifié :

```sql
SELECT MIN(variation) AS var_min,
       MAX(variation) AS var_max,
       SUM(variation < 0) AS nb_negatives
FROM actions;
```

| var_min | var_max | nb_negatives |
| --- | --- | --- |
| 1.35 | 20.06 | 0 |

La raison n'est pas dans le SQL, elle est dans les données. L'URL du TD 3.2,
`/bourse/actions/palmares/france/`, affiche le palmarès des **plus fortes hausses**. Ma base ne
contient donc que des gagnants, et cette requête me sort les plus petites hausses.

Pour répondre vraiment à la question, il faudrait scraper aussi la page des baisses et ajouter
une colonne pour distinguer les deux palmarès. Le sujet ne le demande pas, je le note mais je ne
l'ai pas fait.

## Volumes anormalement élevés

Le sujet propose cette requête, dont le commentaire parle de médiane mais dont le SQL calcule
une moyenne :

```sql
SELECT libelle, volume, cours
FROM actions
WHERE volume > (SELECT AVG(volume) * 2 FROM actions)
ORDER BY volume DESC;
```

| libellé | volume | cours |
| --- | --- | --- |
| STELLANTIS | 2 600 089 | 5,23 |
| BUREAU VERITAS | 1 134 567 | 29,54 |
| TOTALENERGIES | 766 066 | 75,09 |

**La différence entre moyenne et médiane n'est pas anodine ici.**

```sql
SELECT ROUND(AVG(volume)) AS moyenne,
       (SELECT volume FROM actions ORDER BY volume
        LIMIT 1 OFFSET (SELECT COUNT(*) FROM actions) / 2) AS mediane
FROM actions;
```

| moyenne | médiane |
| --- | --- |
| 278 217 | 71 571 |

La moyenne vaut près de 4 fois la médiane. C'est STELLANTIS, avec ses 2,6 millions de titres
échangés, qui la tire vers le haut à lui tout seul.

En utilisant la vraie médiane, le seuil passe de 556 434 à 143 142, et la requête remonte
**10 valeurs au lieu de 3** :

```sql
SELECT libelle, volume, cours
FROM actions
WHERE volume > (
    SELECT volume FROM actions ORDER BY volume
    LIMIT 1 OFFSET (SELECT COUNT(*) FROM actions) / 2
) * 2
ORDER BY volume DESC;
```

Elle ajoute KERING, CAPGEMINI, UBISOFT, RENAULT, FORVIA, ALTEN et SOPRA STERIA. C'est le
comportement attendu d'une médiane : elle résiste aux valeurs extrêmes, la moyenne non. Sur des
volumes boursiers, où un seul titre peut représenter 10 fois le volume des autres, la médiane est
le bon outil.

## Export CSV

Avec les commandes du sujet :

```
.headers on
.mode csv
.output analyse_bourse.csv
SELECT * FROM actions ORDER BY variation DESC;
.output stdout
```

J'ai ajouté `.headers on`, sinon le fichier sort sans ligne d'en-tête et les colonnes ne sont
plus identifiables. Résultat, 26 lignes et 7 colonnes :

```
id,libelle,cours,variation,volume,isin,scraped_at
1,ALTEN,80.2,20.06,177371,1rPATE,"2026-07-29 10:31:17"
2,"SOPRA STERIA",193.8,12.54,144458,1rPSOP,"2026-07-29 10:31:17"
```

## Confrontation avec l'actualité du jour

Le sujet demande de vérifier si une nouvelle explique les mouvements. J'ai cherché sur les deux
plus fortes hausses, et dans les deux cas j'ai trouvé une explication nette, publiée le jour
même.

### Cas 1 : ALTEN, +20,06 %

C'est la plus forte hausse du SBF 120 ce 29 juillet. Le groupe d'ingénierie a publié ses
résultats du premier semestre le matin même, avec une croissance supérieure aux attentes et un
relèvement de ses objectifs pour 2026 : +6,5 % d'activité en France et +1,5 % à l'international.

Le détail qui explique l'ampleur du mouvement : le consensus des analystes tablait sur +1,2 % en
France et **une baisse** de 0,3 % à l'international. L'écart entre l'attendu et le réalisé est
donc énorme, d'où la réaction du marché. Invest Securities a confirmé sa recommandation à l'achat
et relevé son objectif de cours de 128 à 132 euros.

### Cas 2 : SOPRA STERIA, +12,54 %

Même schéma, même jour. Publication des résultats semestriels : chiffre d'affaires en hausse de
4,1 % à 2,96 milliards d'euros, résultat net +3,0 % à 146,3 millions, marge opérationnelle à
9,6 % contre 9,2 % un an plus tôt.

Surtout, le groupe a relevé son objectif de croissance organique 2026, de 1,0-2,0 % à 2,0-2,5 %.
La hausse s'inscrit dans un mouvement plus large, l'action ayant pris 32,3 % en quatre séances.
La presse financière relie cette réaction au contexte du secteur, secoué juste avant par les
avertissements de plusieurs entreprises technologiques américaines : dans ce climat, des
résultats solides sont d'autant mieux accueillis.


## Sources

- [Alten : la croissance du groupe d'ingénierie prend le marché de vitesse, l'action flambe de 20 % (BFM Bourse)](https://www.tradingsat.com/alten-FR0000071946/actualites/alten-la-croissance-du-groupe-d-ingenierie-alten-prend-le-marche-de-vitesse-l-action-flambe-de-20-1167693.html)
- [Alten grimpe en Bourse, porté par une croissance supérieure aux attentes (ABC Bourse)](https://www.abcbourse.com/marches/alten-grimpe-en-bourse-porte-par-une-croissance-superieure-aux-attentes-et-des_700564)
- [Sopra Steria bondit en Bourse après avoir relevé sa prévision de croissance pour 2026 (ABC Bourse)](https://www.abcbourse.com/marches/sopra-steria-bondit-en-bourse-apres-avoir-releve-sa-prevision-de-croissance-pour_700560)
- [Sopra Steria relève son objectif annuel de croissance du CA (Boursorama)](https://www.boursorama.com/bourse/actualites/sopra-steria-releve-son-objectif-annuel-de-croissance-du-ca-50c550608967d24e603d500873b6dc7e)
