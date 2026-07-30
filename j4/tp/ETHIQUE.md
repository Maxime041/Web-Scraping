# Cadre éthique et légal du TP OSINT

Le sujet demande de répondre aux trois questions pour **chaque** TD. Les trois sections sont
ci-dessous.

---

## TD 4.1 : empreinte technique de themoviedb.org

### 1. Ai-je le droit ?

Oui, et les quatre sources se justifient une par une.

Le **WHOIS** est un registre public, imposé par l'ICANN pour tout nom de domaine. C'est
précisément sa fonction de pouvoir être consulté.

**crt.sh** publie les journaux de Certificate Transparency, un mécanisme obligatoire depuis 2018.
Toute autorité de certification doit déclarer publiquement les certificats qu'elle émet, pour que
les fraudes soient détectables. La transparence est le but du dispositif, pas un effet de bord.

Les **en-têtes HTTP** sont ce que le serveur envoie de lui-même à tout visiteur. Mon `requests.head()`
est une requête plus légère que la visite d'un internaute normal.

Le **robots.txt** est publié pour être lu par les robots. Je l'ai ouvert directement,
<https://www.themoviedb.org/robots.txt>, et il ne contient aucun bloc `User-agent: *`. Ses 93
règles ciblent des robots d'IA, rien ne vise notre User-Agent, donc notre accès est autorisé.

Tout est donc passif, sans authentification, sans contournement et sans scan de port. Je n'ai
pas visité les sous-domaines de test que crt.sh révèle, alors que c'était techniquement à portée.
C'est précisément la limite que fixe l'article 323-1 du code pénal cité par le sujet. Constater
qu'un nom existe est légal, aller voir ce qu'il y a derrière ne l'est plus.

### 2. Est-ce personnel ?

Non. Le rapport ne contient que des données techniques, une adresse IP de CDN, des noms de
serveurs DNS, des noms de sous-domaines, des en-têtes HTTP et un nom de registrar.

### 3. Suis-je discret ?

Oui, et c'est mesurable.

Le **User-Agent est identifiable** avec une adresse de contact, `IPSSI-OSINT (+cours@ipssi.fr)`.
Aucune usurpation d'un navigateur.

Il y a un `time.sleep(1)` avant l'analyse, comme demandé par le sujet, et un backoff exponentiel
sur les tentatives crt.sh que j'ai ajoutées, ce qui évite de marteler leur API quand elle renvoie
un 502.

### Base légale RGPD

Intérêt légitime, article 6.1.f, pour une veille concurrentielle documentée dans le cadre d'une évaluation
avant acquisition. Comme aucune donnée personnelle n'est traitée, la question ne se pose de toute
façon pas en pratique.

---

## TD 4.2 : fiche de renseignement sur TotalEnergies

### 1. Ai-je le droit ?

Pour deux sources sur trois, oui sans réserve. La troisième pose un vrai problème.

**SIRENE**, via l'API `recherche-entreprises.api.gouv.fr`, est un registre officiel ouvert. Publier
le SIREN, la dénomination et l'adresse du siège des entreprises est une obligation légale de
transparence. L'État met même une API à disposition pour y accéder, sans clé et sans inscription.

**Wikipédia** est publié sous licence CC BY-SA, qui autorise explicitement la réutilisation. Son
`robots.txt`, <https://fr.wikipedia.org/robots.txt>, autorise bien l'accès aux pages `/wiki/`.

**Google News, en revanche, interdit l'URL du sujet.** J'ai lu son `robots.txt`,
<https://news.google.com/robots.txt> :

```
User-agent: *
Disallow: /
Allow: /$
Allow: /?
Allow: /home$
Allow: /topics/
Allow: /publications/
Allow: /stories/
Allow: /about$
```

Tout est interdit sauf une liste blanche courte, et `/rss/search` n'y figure pas.

Le sujet se contredit donc lui-même. Sa règle 4 impose « robots.txt respecté pour chaque cible »,
et le code qu'il fournit à la source 3 va contre cette règle.

Je l'ai signalé plutôt que de le masquer. La correction serait simple, interroger directement les
flux RSS des journaux, comme `lemonde.fr/rss/une.xml`, qui sont publiés par les éditeurs
précisément pour être lus par des programmes.

### 2. Est-ce personnel ?

Cette fois, en partie oui, et c'est la vraie différence avec le TD 4.1.

L'infobox Wikipédia récupérée contient **des noms de personnes physiques** :

| Champ | Contenu |
| --- | --- |
| Direction | Patrick Pouyanné (président-directeur général) |
| Fondateurs | Ernest Mercier |
| Personnages clés | Thierry Desmarest |

Ce sont des données à caractère personnel au sens du RGPD, puisqu'elles identifient des personnes.

Trois éléments les rendent acceptables ici.

Ce sont des **données déjà publiques**, publiées par les personnes concernées ou par leur
entreprise dans le cadre de leurs obligations légales. Le nom du dirigeant d'une société cotée est
une information que la loi oblige à publier.

Elles relèvent de la **fonction professionnelle**, pas de la vie privée. Je collecte « le PDG de
TotalEnergies s'appelle Patrick Pouyanné », pas son adresse, son téléphone ou ses habitudes.

La **finalité est cohérente.** On construit une fiche d'entreprise. Le nom du dirigeant fait partie de ce
qu'on attend d'une telle fiche.

L'adresse du siège relevée dans SIRENE, 562 avenue du Parc de l'Île à Nanterre, est une adresse
d'entreprise, pas de personne. Elle ne pose pas de question.

### 3. Suis-je discret ?

Oui, et c'est très léger.

Le script envoie **trois requêtes en tout**, une par source, et sur trois hôtes différents. Chaque
serveur en voit donc une seule.

Le User-Agent est identifiable avec une adresse de contact, `IPSSI-OSINT (+cours@ipssi.fr)`.

Il y a un `time.sleep(1)` entre chaque source, conformément à la consigne du sujet. Il est un peu
symbolique ici puisque les trois appels visent des serveurs différents, mais il ne coûte rien et il
respecte la règle.

### Base légale RGPD

Intérêt légitime, article 6.1.f, pour la partie qui concerne des données personnelles, à savoir les
noms des dirigeants. La finalité est une veille sur une entreprise cotée, les données sont déjà
publiques et limitées à la sphère professionnelle, et le volume reste minimal. Aucune donnée
sensible au sens de l'article 9 n'est collectée.

---

## TD 4.3 : veille presse sur Airbus

### 1. Ai-je le droit ?

Oui, et c'est le TD le plus clair des trois sur ce point.

Un **flux RSS est fait pour être lu par un programme**. Un éditeur qui publie un fichier XML à une
adresse fixe, avec les titres et les résumés de ses articles, le fait précisément pour que des
lecteurs de flux, des agrégateurs et des robots le consomment. C'est la différence avec le TD 4.2,
où le sujet passait par Google News dont le `robots.txt` interdit l'accès. Ici on interroge
directement les éditeurs.

`ROBOTSTXT_OBEY = True` est activé dans le `custom_settings` du spider. J'ai ouvert les cinq
fichiers pour vérifier, aucun n'interdit son flux RSS :

- <https://www.lemonde.fr/robots.txt>
- <https://www.lesechos.fr/robots.txt>
- <https://www.lefigaro.fr/robots.txt>
- <https://www.bfmtv.com/robots.txt>
- <https://www.01net.com/robots.txt>

Un cas mérite d'être mentionné. **Les Echos renvoie un 403** sur son flux, alors que son
`robots.txt` ne l'interdit pas. Ce n'est donc pas un refus exprimé par les règles, c'est un
filtrage technique. Scrapy logge l'erreur et passe au flux suivant. Je n'ai ni contourné ni
insisté.

Il reste une limite de fond, je ne collecte que **titres et résumés**, tels que l'éditeur les
publie dans son flux. Je ne récupère pas le texte intégral des articles, qui lui est protégé par
le droit d'auteur. C'est une différence importante avec un scraping du contenu des pages.

### 2. Est-ce personnel ?

Non, et c'est voulu par le filtrage lui-même.

Le spider ne garde que les articles qui mentionnent **Airbus**, c'est-à-dire une personne morale.
Les champs stockés sont un titre, une URL, un nom de média, une date et un résumé. Rien qui
identifie une personne physique.

Il y a une réserve honnête à poser, un titre de presse **peut** contenir un nom de personne, par
exemple celui d'un dirigeant mis en cause. Je ne le maîtrise pas, puisque je ne choisis pas les
titres. Deux éléments limitent la portée du problème. Ces titres sont **déjà publiés** par des
médias professionnels, donc l'information est publique par nature. Et je ne fais aucun traitement
sur les personnes, pas de recherche par nom, pas de recoupement, pas de profil.

Si le but de la veille était de suivre une **personne** plutôt qu'une entreprise, la réponse
changerait complètement. On entrerait dans un traitement de données personnelles à part entière,
avec information des personnes concernées et durée de conservation à définir.

### 3. Suis-je discret ?

Oui, et c'est le TD où c'est le plus encadré, parce que Scrapy s'en charge.

Le `custom_settings` du spider fixe trois choses :

```python
"ROBOTSTXT_OBEY": True,
"DOWNLOAD_DELAY": 1.0,
"RANDOMIZE_DOWNLOAD_DELAY": True,
"USER_AGENT": "IPSSI-OSINT-veille (+cours@ipssi.fr)",
```

Une seconde entre chaque requête, avec une variation aléatoire pour ne pas produire un rythme
mécanique, et un User-Agent identifiable avec une adresse de contact.

Le volume est très faible, **5 requêtes par passage**, une par flux, réparties sur 5 domaines
différents. Chaque éditeur en voit donc une seule. Un flux RSS est en plus un fichier léger,
conçu pour être appelé régulièrement.

Un point sur la répétition. Une veille est faite pour être relancée, et c'est ce que je conseille
pour accumuler des mentions. Relancer quelques fois par jour reste raisonnable, c'est le rythme
d'un lecteur de flux ordinaire. Ce qui ne le serait pas, c'est une boucle qui interroge les mêmes
flux toutes les dix secondes, sans que le contenu ait eu le temps de changer.

### Base légale RGPD

Intérêt légitime, article 6.1.f, pour une veille médiatique sur une entreprise cotée, dans un cadre
pédagogique documenté. Aucune donnée personnelle n'est ciblée ni recherchée.
