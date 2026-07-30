# TD 4.1 : empreinte technique d'un domaine

Cible : **themoviedb.org**. Rapport dans `rapport_themoviedb.org.json`, produit par
`td41_domaine.py`.

## Pourquoi cette cible

Le sujet demande d'évaluer l'exposition technique d'un concurrent. TMDB, The Movie Database, est
une base de données de films avec une API publique.

Deux raisons pratiques en plus. C'est un domaine en `.org`, dont le WHOIS est complet, alors que
les `.fr` passent par l'AFNIC et renvoient souvent des champs vides. 

## Ce que le rapport contient

| Champ | Valeur |
| --- | --- |
| IP | 143.204.194.2 |
| registrar | MarkMonitor, Inc. |
| création | 2008-09-15 |
| expiration | 2027-09-15 |
| pays | US |
| serveurs de noms | 4 serveurs `awsdns` en `.net`, `.co.uk`, `.org`, `.com` |
| serveur web | openresty |
| HSTS | présent |
| CSP | absent |
| X-Frame-Options | absent |
| sous-domaines | 13 |

## Tout est hébergé chez Amazon

Les quatre serveurs de noms sont des `awsdns`, donc Route 53. L'IP appartient à CloudFront, ce que
confirme son nom inverse, `server-143-204-194-2.cdg54.r.cloudfront.net`. Le `cdg` est le code de
l'aéroport de Roissy, donc le point de présence qui m'a répondu est à Paris.

L'IP a changé entre deux exécutions du script, de `143.204.194.119` à `143.204.194.2`. C'est normal
sur un CDN, `socket.gethostbyname()` renvoie l'adresse du nœud le plus proche, qui tourne.

Le serveur web annoncé est `openresty`, c'est-à-dire du Nginx. Il n'y a pas de `X-Powered-By`, donc
rien ne fuit sur le langage applicatif derrière.

## Ce que révèlent les sous-domaines

```
api-bunny        api            api-test
developer        developers
assets           media          files
blog             www.blog
status
www-test
```

Quatre choses se lisent dans cette liste.

**L'API est un produit à part entière**, pas une annexe du site. Elle a son propre sous-domaine
`api`, son portail `developer`, et son propre environnement de test `api-test`. Une entreprise qui
isole ainsi son API a des clients externes qui en dépendent.

**Le contenu statique est éclaté sur trois hôtes**, `assets`, `media` et `files`. C'est la
séparation classique quand on sert des images d'affiches en volume, pour les mettre derrière un CDN
et éviter d'envoyer les cookies avec chaque image.

**`developer` et `developers` coexistent**, au singulier et au pluriel. Deux certificats pour deux
noms qui font la même chose, c'est la trace d'une migration où l'ancien nom a été gardé en
redirection.

**Deux environnements de test portent un certificat public**, `api-test` et `www-test`.

## Ce que dit le robots.txt

Le fichier fait 2382 caractères, avec **93 lignes `User-agent`** et **un seul `Disallow`**. Il n'y
a aucun bloc `User-agent: *`.

Les 93 agents listés sont des robots d'IA, comme AI2Bot, Amazonbot, anthropic-ai ou Applebot. TMDB les
bloque tous en groupe avec le `Disallow` unique, et ne dit rien aux autres visiteurs. Comme aucune
règle ne vise notre User-Agent, notre accès est autorisé.

Le fichier est consultable ici, <https://www.themoviedb.org/robots.txt>

C'est un choix de politique intéressant à relever. L'entreprise protège son catalogue contre
l'entraînement de modèles, mais laisse la porte ouverte aux crawlers classiques.

## Trois corrections apportées au code du sujet

**La date d'expiration sortait cassée**, avec la valeur `"[datetime."`. Le WHOIS renvoie parfois
une liste de dates, et le `str(...)[:10]` du sujet tronquait la représentation de la liste. J'ai
ajouté une fonction `date_whois()` qui prend le premier élément si c'est une liste. La bonne valeur
est 2027-09-15.

**crt.sh est instable.** Sur quatre appels consécutifs j'ai eu un 502, un timeout, puis un 200 avec
605 entrées. Le code du sujet ne réessayait pas. J'ai mis le retry avec backoff exponentiel du
Jour 1.

**Une erreur était comptée comme une donnée.** En cas d'échec, le sujet renvoie
`[f"ERREUR: {e}"]`, et comme `nb_sous_domaines` fait un `len()` de cette liste, le rapport
annonçait « 1 sous-domaine trouvé » alors qu'il n'en avait trouvé aucun. Je renvoie maintenant une
liste vide.

## Pour lancer l'analyse

```
python td41_domaine.py themoviedb.org
```

## Les fichiers

`td41_domaine.py` pour le script, `rapport_themoviedb.org.json` pour le rapport.

Les trois réponses aux questions du sujet sont dans `ETHIQUE.md`.
