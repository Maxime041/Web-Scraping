# Défi 2 : analyser les performances de crawl

Le défi demande de mesurer l'impact de `CONCURRENT_REQUESTS` sur le spider AlloCiné, en se
limitant à 100 films. Le mien en récupère 50, je suis dans les clous.

## Comment j'ai mesuré

J'ai lancé le spider du TD 3.1 avec les 4 valeurs demandées, sans toucher au projet :

```
scrapy crawl films -L INFO -s CONCURRENT_REQUESTS=1
```

Puis pareil avec 4, 8 et 16. Je relève le temps, le nombre d'items et le nombre de réponses dans
les statistiques de fin de crawl.

Le sujet propose `-L WARNING`, mais dans ce cas les statistiques ne s'affichent pas, elles sont
loggées en INFO. Mes premières mesures donnaient 0 item partout avant que je comprenne. J'ai
aussi ajouté `-s FEEDS={}` pour ne pas réécrire `films.json` et `films.csv` à chaque essai.

## Première série, avec les réglages du projet

| CONCURRENT_REQUESTS | temps | items/s |
| --- | --- | --- |
| 1 | 68,5 s | 0,73 |
| 4 | 67,6 s | 0,74 |
| 8 | 66,8 s | 0,75 |
| 16 | 66,1 s | 0,76 |

Il ne se passe rien. Multiplier la concurrence par 16 fait gagner 3,5 %, c'est du bruit de mesure.

La raison est simple : le projet a `DOWNLOAD_DELAY = 1.0`. Avec 56 requêtes et une seconde entre
chacune, le crawl ne peut pas descendre sous 56 secondes, quel que soit le nombre de requêtes
lancées en parallèle. Ce n'est pas la concurrence qui limite, c'est le délai.

## Deuxième série, sans le délai

Pour voir la vraie courbe, j'ai refait la série en désactivant le délai et l'auto-throttle, le
temps de la mesure :

```
scrapy crawl films -L INFO -s CONCURRENT_REQUESTS=8 -s DOWNLOAD_DELAY=0 -s AUTOTHROTTLE_ENABLED=False
```

| CONCURRENT_REQUESTS | temps | items/s | gain |
| --- | --- | --- | --- |
| 1 | 3,0 s | 16,95 | |
| 4 | 2,2 s | 22,74 | +34 % |
| 8 | 1,7 s | 28,80 | +27 % |
| 16 | 1,7 s | 29,24 | +1,5 % |

Le projet garde bien son `DOWNLOAD_DELAY = 1.0`, ces réglages sont passés en ligne de commande.

## À partir de quelle valeur le gain devient négligeable ?

À partir de 8. De 1 à 4 je gagne 34 %, de 4 à 8 encore 27 %, mais de 8 à 16 seulement 1,5 %, soit
0,04 seconde.

Le crawl ne fait que 56 requêtes. Au delà de 8 en parallèle, il n'y a plus assez de travail en
attente pour remplir les créneaux libres, et ce qui limite devient le temps de réponse du serveur.

## Pourquoi AUTOTHROTTLE peut battre une valeur fixe élevée ?

Parce qu'une valeur fixe est aveugle, alors qu'AutoThrottle mesure.

`CONCURRENT_REQUESTS = 16` envoie 16 requêtes en parallèle en permanence, que le serveur suive ou
non. Sur un site plus fragile, il ralentit puis finit par renvoyer des 429 ou des 503. Le
`RetryMiddleware` rejoue alors chaque requête jusqu'à 3 fois, donc on fait plus de requêtes pour
le même résultat, et on finit plus lent qu'avec une concurrence modérée. Avec en plus le risque
de se faire bloquer.

AutoThrottle regarde le temps de réponse réel et ajuste le délai en continu : si le serveur
ralentit, il ralentit aussi, s'il répond vite, il accélère.

Je n'ai pas pu le vérifier sur AlloCiné. À 16 requêtes simultanées sans délai, les statistiques
affichent 56 réponses en 200, aucun retry, aucune erreur. Le site est assez gros pour absorber ça
sans broncher.

## Le ratio items sur réponses

Il vaut 0,89 dans tous mes essais, soit 50 items pour 56 réponses. Les 6 requêtes qui ne
produisent rien sont le `robots.txt` et les 5 pages de liste, seules les 50 fiches donnent un item.

Un ratio sous 0,5 voudrait dire que plus de la moitié des requêtes sont perdues. Sur AlloCiné, la
cause la plus probable serait que les sélecteurs de la fiche ont cassé : on télécharge les 50
pages et `parse_film()` n'émet plus rien. C'est réaliste, au TD 3.1 j'ai constaté que 4 des 7
sélecteurs du sujet ne renvoyaient déjà plus rien. Les autres causes possibles sont trop de pages
de navigation par rapport aux fiches, ou des redirections et des erreurs.

C'est donc un bon indicateur de santé : si ce ratio s'effondre alors que le code n'a pas changé,
c'est que le site a bougé.
