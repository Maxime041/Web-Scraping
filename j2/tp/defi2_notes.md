# Défi 2 : empreinte anti-bot de mon driver

J'ai repris le code du sujet et je l'ai lancé sur `https://bot.sannysoft.com`, qui teste une
trentaine de propriétés JavaScript et les affiche en vert quand elles ont l'air normales, en
rouge quand elles trahissent un navigateur piloté.

J'ai fait trois passages, et les captures sont dans `j2/tp/screenshots/` :

- `bot_normal.png`, sans aucun flag anti-détection
- `bot_stealth.png`, avec les deux flags du sujet
- `bot_headless.png`, les mêmes flags mais en mode headless, comme le demande la dernière question

---

## Question 1 : quels champs passent de rouge à vert

Un seul.

| Test | Sans flag | Avec les flags |
| --- | --- | --- |
| WebDriver (New) | rouge, `present (failed)` | vert, `missing (passed)` |
| tous les autres | déjà verts | toujours verts |

Le libellé change en même temps que la couleur : on passe de `present` à `missing`. J'ai vérifié
la valeur en direct, `navigator.webdriver` vaut `true` sans les flags et `false` avec.

Sur les 31 tests que compte la page, il n'y en a qu'un seul en rouge quand je lance Chrome sans
rien configurer : `WebDriver (New)`. C'est le test qui lit `navigator.webdriver`, une propriété
que Chrome met à `true` dès qu'il est piloté par un outil comme Selenium.

Tout le reste est vert dès le départ : le User-Agent, les langues, le nombre de plugins, WebGL,
la liste des tests PHANTOM et HEADCHR. Autrement dit, un Chrome piloté ressemble déjà beaucoup à
un Chrome normal, parce que c'est un vrai Chrome. Il n'y a qu'un seul drapeau planté par le
driver, et les deux options du sujet servent uniquement à le retirer.

Le passage en mode furtif ne corrige donc qu'une seule ligne du tableau.

---

## Question 2 : le champ webdriver est-il encore détecté en mode furtif

Non. Avec `--disable-blink-features=AutomationControlled` et
`excludeSwitches: ["enable-automation"]`, le test passe au vert et la page ne trouve plus rien à
signaler : zéro test en rouge sur 31.

Mais je ne pense pas qu'il faille en conclure grand-chose, et j'ai de quoi le prouver avec mon
propre TP.

Ce que teste sannysoft, ce sont des propriétés lisibles en JavaScript depuis la page. Le site
regarde ce que le navigateur veut bien raconter sur lui-même. Les vraies protections
industrielles travaillent en amont, avant même que la page ne s'affiche : elles regardent
l'empreinte TLS de la connexion, l'ordre des en-têtes HTTP, l'adresse IP, le rythme des
requêtes, les mouvements de souris.

Deux exemples tirés du TP :

Sur Les Echos, `requests` reçoit un 403 d'Akamai quel que soit le User-Agent que je déclare.
Aucun JavaScript n'a été exécuté à ce moment-là, donc aucun des tests de sannysoft n'aurait pu
prévoir ce blocage. La détection se fait au niveau de la connexion elle-même.

Toujours sur Les Echos, mon Chrome headless avec les deux flags du sujet, celui-là même qui
affiche 100 % de vert sur sannysoft, se faisait renvoyer une page `Access Denied`.

Donc être tout vert sur sannysoft veut simplement dire qu'aucune propriété JavaScript évidente
ne trahit le driver. Ça ne veut pas dire qu'on passe partout.

---

## Question 3 : quels nouveaux champs deviennent rouges en headless

Trois, alors que j'ai gardé exactement les mêmes flags anti-détection.

| Test | Résultat en headless | Ce que ça veut dire |
| --- | --- | --- |
| User Agent (Old) | rouge | le User-Agent contient `HeadlessChrome/150.0.0.0` au lieu de `Chrome/150.0.0.0` |
| HEADCHR_UA | rouge, `FAIL` | c'est le test qui cherche justement le mot « Headless » dans le User-Agent |
| CHR_MEMORY | rouge, `FAIL` | test lié à `performance.memory` |

À noter au passage : le test `WebDriver (New)` reste vert en headless, avec exactement le même
libellé qu'en mode normal, `missing (passed)`. Le headless ne change donc rien sur ce point, les
trois lignes rouges sont bien nouvelles.

### Les trois viennent en fait du User-Agent

J'ai voulu vérifier si mon correctif du TD 2.2, où je force un User-Agent normal en headless,
suffisait à faire disparaître ces trois lignes rouges. J'ai relancé le même test en ajoutant
`--user-agent=...` avec une chaîne de Chrome classique.

Résultat : **zéro test en rouge**. Les trois repassent au vert, y compris `CHR_MEMORY`.

`CHR_MEMORY` ne parle pourtant pas de User-Agent, donc j'ai vérifié directement la valeur de
`performance.memory` dans les deux cas : elle vaut `object` aussi bien en headless qu'en mode
normal. L'API est donc bien présente des deux côtés. Ce n'est pas une capacité qui manque en
headless, c'est le test de sannysoft qui se base sur le User-Agent déclaré pour décider s'il doit
échouer.

En clair, en headless, une seule chaîne de caractères fait basculer trois lignes du tableau. Et
c'est cohérent avec ce que j'ai vécu sur Les Echos : dès que j'ai forcé le User-Agent, Akamai a
laissé passer le navigateur headless.

---

## Ce que j'en retiens

Chrome piloté par Selenium n'a qu'un seul vrai défaut visible en JavaScript, `navigator.webdriver`,
et les deux options du sujet suffisent à le faire disparaître.

Le mode headless est le vrai problème, pas le pilotage. Il se dénonce tout seul en écrivant
`HeadlessChrome` dans son User-Agent, ce qui est facile à corriger, mais qui explique pourquoi
un scraper qui marche en mode normal peut se faire bloquer dès qu'on le passe en headless.

Et un tableau vert sur un site de test ne prouve pas grand-chose. Mes deux blocages du TP se
sont produits avant l'exécution du moindre JavaScript, sur des critères que sannysoft ne
regarde même pas.

---

## Les fichiers

`j2/tp/defi2_bot_detection.py` pour le code, et les trois captures dans `j2/tp/screenshots/` :
`bot_normal.png`, `bot_stealth.png` et `bot_headless.png`.
