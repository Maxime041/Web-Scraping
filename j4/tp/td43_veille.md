# TD 4.3 : veille automatisée avec Scrapy

Projet dans `veille/`, exports dans `veille/mentions.csv` et `veille/veille.db`.
Cible surveillée : **Airbus**.

## Pourquoi Airbus

Le sujet met `CIBLE = "TotalEnergies"` avec le commentaire « modifiable ». J'ai dû le modifier,
pour une raison mesurée et pas par préférence.

J'ai compté les mentions dans les 5 flux du sujet avant d'écrire quoi que ce soit, et
**0 article sur 94 parle de TotalEnergies**. Le fichier `mentions.csv` et la base seraient sortis
vides.

Ce n'est pas un défaut de la cible. Ces 5 flux sont des flux « une », c'est-à-dire les derniers
titres de la page d'accueil des médias. Une entreprise précise n'y apparaît que si elle fait
l'actualité du jour.

J'ai donc cherché une cible qui fonctionne, en testant 35 entreprises sur les 94 articles.

| Entreprise | Articles | Médias |
| --- | --- | --- |
| Apple | 4 | 1 |
| OpenAI, Google | 3 | 1 |
| Microsoft | 2 | 1 |
| Airbus, Orange, Bouygues, Tesla | 1 | 1 |
| TotalEnergies | 0 | 0 |

Aucune ne dépasse 4 articles, et toutes les mieux placées sont concentrées sur un seul média,
01net, qui est un site tech. J'ai retenu **Airbus** parce que le sujet la cite en exemple, qu'elle
est au CAC40 comme il le demande, et qu'elle existe dans SIRENE et sur Wikipédia.

## Le mot-clé thématique que j'ai écarté

J'ai testé `incendie`, qui donnait **26 articles**, soit bien plus que n'importe quelle
entreprise. Mais je l'ai écarté après avoir regardé les scores :

| Cible | Articles | Neutres (0) | Négatifs (1) | Positifs (2) |
| --- | --- | --- | --- | --- |
| incendie | 26 | 25 | 0 | 1 |
| Airbus | 1 | 0 | 0 | 1 |

Avec `incendie`, **25 articles sur 26 sortent à 0**. C'est logique, le vocabulaire du sujet est
celui de l'entreprise, `amende`, `faillite`, `perquisition`, `acquisition`, `nomination`. Aucun de
ces mots n'apparaît dans un article sur un feu de forêt.

## Ce que le crawl donne

Deux passages lancés à quelques minutes d'intervalle.

| Indicateur | Valeur |
| --- | --- |
| réponses 200 | 9 |
| redirection 301 suivie | 1 |
| erreur 403 ignorée | 1 (Les Echos) |
| items émis par passage | 1 |
| lignes en base après 2 passages | **1** |

La mention trouvée est « Airbus bat un record historique avec un vol de plus de 24 heures », sur
01net, **score 2**. Le score est juste, `record` fait partie des mots positifs et l'article est
effectivement favorable.

**La contrainte `UNIQUE(url)` fonctionne.** Deux passages ont émis 1 item chacun, et la base
contient toujours 1 ligne. C'est le `INSERT OR IGNORE` du pipeline combiné à la contrainte qui
évite le doublon.

## Le flux des Echos renvoie 403

`https://www.lesechos.fr/rss/rss_une.xml` répond `403 Forbidden`.

Je n'ai pas remplacé ce flux, pour deux raisons. Il vient du sujet, et Scrapy le gère
proprement, le `HttpErrorMiddleware` logge l'erreur et le crawl continue avec les 4 autres flux.

```
[scrapy.spidermiddlewares.httperror] INFO: Ignoring response <403 https://www.lesechos.fr/rss/rss_une.xml>
```

On perd donc un flux économique sur cinq, ce qui explique en partie le peu de mentions
d'entreprises.


## Pour lancer le crawl

```
scrapy crawl rss_spider -L INFO
```

Le pipeline affiche `[OSINT] N mentions en base` en fin de crawl.

## Pour analyser la base

La commande donnée par le sujet :

```
python -c "
import sqlite3
cx = sqlite3.connect('veille.db')
rows = cx.execute('SELECT titre, source, score_alerte FROM mentions ORDER BY score_alerte DESC').fetchall()
print(f'{len(rows)} mentions trouvees')
for r in rows[:5]:
    print(f'  [{r[2]}] {r[0][:60]} ({r[1]})')
cx.close()
"
```

## Les fichiers

`veille/veille/items.py` pour le `MentionItem`, `veille/veille/spiders/rss_spider.py` pour le
spider, `veille/veille/pipelines.py` pour les deux pipelines, `veille/veille/settings.py` pour
la configuration, et les exports `veille/mentions.csv` et `veille/veille.db`.

Les trois réponses aux questions du sujet sont dans `ETHIQUE.md`.
