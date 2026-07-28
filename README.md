# README - Cours Web Scraping

Ce dépôt contient les travaux dirigés (TD) et les travaux pratiques du cours de Web Scraping (Jour 1 : `requests` + BeautifulSoup, Jour 2 : Selenium).

---

## 1. Travaux Dirigés (`j1/td/`)

- `j1/td/td1.py` : Premières requêtes HTTP avec `requests` et parsing HTML avec `BeautifulSoup`.
- `j1/td/td2.py` : Extraction multi-pages d'articles du Blog du Modérateur avec pagination.
- `j1/td/articles.csv` : Fichier CSV d'export associé au TD2.

---

## 2. TP1 - Scraper Blog du Modérateur (`j1/tp1/`)

### Étapes du sujet (Parties 1 à 5)

- **Partie 1 - Exploration & setup** : J'ai inspecté le fichier `robots.txt` et validé le cadre éthique en répondant aux questions du sujet :
  - **Le scraping de la section `/feed/` est-il autorisé ?** Non, il est explicitement interdit (`Disallow: /feed/`) par le fichier `robots.txt`.
  - **1. Ai-je le droit ?** Oui, le `robots.txt` autorise l'accès aux pages HTML d'archives et le projet reste dans un cadre éducatif.
  - **2. Est-ce personnel ?** Non, ce sont uniquement des données éditoriales publiques (titres, dates, catégories, chapeaux).
  - **3. Suis-je discret ?** Oui, le scraper utilise un User-Agent bien identifiable (`IPSSI-scraper`) et respecte une pause de 1,5 seconde entre chaque requête.
- **Partie 2 - Scraper une page** : J'ai codé la fonction `get_page()` dans `j1/tp1/main.py` pour récupérer le HTML et `parse_articles()` pour extraire les 5 champs de chaque carte d'article. Tout est correctement structuré sous forme de liste de dictionnaires Python.
- **Partie 3 - Pagination (200 articles)** : J'ai créé la boucle `scrape_all()` qui navigue sur les pages `/page/N/` avec une pause de 1,5 s entre les requêtes. La fonction intègre un système de retry avec backoff exponentiel et la gestion du statut 429.
- **Partie 4 - Persistance CSV + SQLite** : J'ai développé `sauver_csv()` pour l'export en UTF-8 dans `j1/tp1/articles.csv` et `sauver_sqlite()` pour l'insertion dans `j1/tp1/articles.db`. La base SQLite gère le dédoublonnage natif grâce à la contrainte UNIQUE sur l'URL.
- **Partie 5 - Robustesse & finalisation** : J'ai mis en place l'interface CLI via `argparse` dans `main()` pour pouvoir lancer le script en une commande avec options (`--max`, `--csv`, `--db`). Le code utilise des f-strings et une list-comprehension refactorisée.

---

## 3. Pour aller plus loin -- Défis autonomes

- **Défi 1** (`j1/tp1/scraper_trashtalk.py` & `j1/tp1/defi1_selecteurs.md`) : J'ai adapté le scraper sur le site TrashTalk (basket) en réutilisant les fonctions du script principal. On obtient bien le fichier CSV avec les 4 sélecteurs analysés dans le document Markdown.
- **Défi 2** (`j1/tp1/diff_scrapes.py` & `j1/tp1/defi2_notes.md`) : J'ai écrit le script de comparaison entre deux fichiers CSV pour détecter les nouveautés, les disparitions et les articles stables. La comparaison donne des résultats réels et répond aux questions sur la fréquence de crawl.
- **Défi 3** (`j1/tp1/benchmark_throttling.py` & `j1/tp1/defi3_notes.md`) : Le script mesure les temps d'exécution selon le nombre de pages et le délai de pause appliqué. Le tableau récapitule les mesures réelles obtenues sur ma machine comme demandé.

---

# Jour 2 - Selenium

## 4. TD 2.1 - Doctolib (`j2/tp/`)

J'ai choisi de chercher un hématologue à Nice, donc l'adresse `https://www.doctolib.fr/hematologue/nice`.

### Les étapes du sujet

**Étape 1, lancer et naviguer.** J'ai repris `webdriver.Chrome()` avec les options anti-détection du sujet, `--disable-blink-features=AutomationControlled` et `excludeSwitches`. Je n'ai rien eu à installer pour chromedriver, Selenium Manager s'en occupe tout seul.

**Étape 2, la bannière cookies.** J'ai gardé la stratégie 1, celle qui clique sur le bouton Accepter. Le XPath du sujet ne marche pas sur Doctolib, pour deux raisons. D'abord le bouton a un identifiant précis, `didomi-notice-agree-button`. Ensuite le mot « Accepter » est dans un `<span>` à l'intérieur du bouton, et `contains(text(),"Accepter")` ne regarde que le texte direct : il faut écrire `contains(.,"Accepter")`. J'ai aussi ajouté un screenshot si le bouton n'est pas trouvé. Les stratégies 2 et 3 sont laissées en commentaire comme dans le sujet.

J'ai voulu savoir ce qui se passait si la bannière restait ouverte, et le résultat est piégeux. Les 17 cartes sont bien dans la page, donc `WebDriverWait` réussit et aucune erreur n'est levée. Mais les cartes cachées derrière la fenêtre de consentement renvoient un texte vide, parce que Selenium ne lit que ce qui est visible à l'écran. J'obtiens un `doctolib.json` avec des fiches sans nom ni adresse, et sans le moindre message d'erreur. Le script ne plante pas, il produit des données fausses en silence.

**Étape 3, attendre les résultats.** `WebDriverWait(driver, 15)` avec `EC.presence_of_element_located` sur les cartes. Il n'y a aucun `time.sleep()` fixe dans le déroulé principal, le seul qui reste est dans la boucle de scroll, comme dans le code du sujet. Si l'attente échoue, un screenshot est enregistré dans `j2/tp/screenshots/` avant de lever l'erreur.

**Étape 4, le scroll.** J'ai gardé `scroll_to_bottom()` telle quelle. Elle compare la hauteur de la page avant et après pour s'arrêter dès qu'elle ne grandit plus.

**Étape 5, extraire les 5 champs.** `extraire_medecins()` renvoie `nom_specialite`, `adresse`, `type_consultation`, `prochains_creneaux` et `url_fiche`, et l'export part dans `j2/tp/doctolib.json`. J'obtiens 10 médecins, le sujet en demande au moins 5.

### Les sélecteurs que j'ai dû changer

Ceux du PDF ne fonctionnent plus, le site a changé de design (classes Tailwind et design system « Oxygen »). Je les ai retrouvés dans DevTools :

| Champ | Sélecteur du sujet | Ce que j'ai mis |
| --- | --- | --- |
| carte médecin | `div[data-test='search-result-card']` | `div.dl-card:has(h2)`, le `:has(h2)` écarte les 3 encarts qui ne sont pas des fiches |
| nom | `h2, h3, [class*='name']` | `h2`, en gardant la 1re ligne car le titre contient parfois « Consultation vidéo » en dessous |
| spécialité | pas prévu dans le sujet | `div.flex.flex-col.w-full p` |
| adresse | `[class*='address']` | `div.flex.gap-8:has(> div > svg[aria-label='Adresse'])` |
| créneaux | `[class*='slot']` | `div[data-test-id='availabilities-container'] button` |
| url de la fiche | `a[href*='/praticien/']` | `a[href]`, parce que les adresses sont du type `/hematologue/nice/nom-prenom` et pas `/praticien/` |

À part ces sélecteurs, le code est celui du sujet, je n'ai ni ajouté ni retiré de fonction.

### Ce que j'observe dans les données

`type_consultation` vaut `["Cabinet"]` sur les 10 fiches. Aucun hématologue de Nice ne propose la téléconsultation. La mention « Consultation vidéo disponible » existe bien sur Doctolib, je l'ai vue sur la page des médecins généralistes de Nice, mais pas ici.

`prochains_creneaux` est vide la plupart du temps, parce que les hématologues n'ouvrent pas la prise de rendez-vous en ligne. Quand il y a une information, je récupère le texte du bouton, par exemple `"Prochain RDV le 3 septembre 2026"`.

Les résultats contiennent aussi des établissements (CHU de Nice, Centre Antoine Lacassagne) et un pédiatre. C'est bien ce que Doctolib affiche pour cette recherche, je n'ai pas filtré.

### Pourquoi Selenium et pas requests avec BeautifulSoup

La page de résultats est construite en JavaScript. Le HTML que renvoie `requests` ne contient ni les fiches de praticiens ni les créneaux. Il faut un vrai navigateur pour exécuter le JavaScript, cliquer sur la bannière de consentement et déclencher le chargement des disponibilités. `requests` ne sait faire aucune des trois.

### Les fichiers

`j2/tp/doctolib_scraper.py` pour le scraper, `j2/tp/doctolib.json` pour l'export (10 médecins et 5 champs chacun), et `j2/tp/screenshots/doctolib_erreur.png`.

Cette capture vient d'un vrai échec : le sélecteur de cartes du sujet ne trouvait plus rien. C'est justement elle qui m'a permis de voir que la page s'affichait correctement avec 17 résultats et que le problème venait du sélecteur. Le scraper réenregistre cette capture dans deux cas, si le bouton cookies est introuvable ou si les cartes ne se chargent pas.

---

## 5. TD 2.2 - Les Echos (`j2/tp/`)

Cible : la page d'accueil de `https://www.lesechos.fr`.

### Les étapes du sujet

**Étape 1, tester d'abord avec requests.** Le test affiche `0 balises de titre trouvees`. En regardant la réponse de plus près, ce n'est pas une page vide mais un HTTP 403, une page `Access Denied` d'Akamai. J'ai vérifié que ce n'était pas juste une histoire de User-Agent : même en me faisant passer pour un Chrome complet, c'est toujours 403. Selenium est donc bien nécessaire.

**Étape 2, Selenium et le mode headless.** J'ai gardé `make_driver(headless)` et le chronométrage du sujet sans y toucher, à part le User-Agent en headless dont je parle plus bas. Les Echos affiche une bannière Didomi, mais je n'ai pas eu besoin de la cliquer : j'ai vérifié, les 46 blocs d'articles sont lisibles sans l'accepter.

**Étape 3, extraire les 5 champs.** `extraire_articles()` exporte `titre`, `rubrique`, `chapeau`, `heure_publi` et `premium` dans `j2/tp/lesechos.json`. J'obtiens 46 articles, le sujet en demande au moins 10.

### Les sélecteurs que j'ai dû changer

Le point important de ce TD, c'est que la page d'accueil contient deux blocs d'articles différents, et qu'aucun des deux ne porte toutes les informations :

| Bloc | Sélecteur | Ce qu'il contient |
| --- | --- | --- |
| les cartes « à la une » | `article` (41 blocs) | titre, rubrique et badge premium, mais pas d'heure |
| le fil d'actu à droite | `div[type='article']` (5 blocs) | titre, heure et badge premium, mais pas de rubrique |

D'où mon sélecteur `"article, div[type='article']"`, qui prend les deux. Pour le détail des champs :

| Champ | Sélecteur du sujet | Ce que j'ai mis |
| --- | --- | --- |
| titre | `h2, h3, [class*='title']` | `h1, h2, h3` avec `.split("\n")[0]`, car le titre contient parfois « Premium » sur une 2e ligne |
| rubrique | `[class*='rubrique'], [class*='section'], [class*='category']` | `[data-testid='hubpage-links'] a` |
| chapeau | `p, [class*='chapo'], [class*='intro']` | `p`, que j'ai gardé même s'il n'y en a aucun, voir plus bas |
| heure_publi | `time, [class*='date']` | `div[class*='sc-1h4katp-1'] span`, parce qu'il n'y a aucune balise `<time>` sur la page |
| premium | `[class*='premium'], [class*='abonne'], svg[class*='lock']` | `[data-testid='subscribe-badge']` |

Les classes CSS des Echos sont générées par styled-components, du genre `sc-19z4l96-2 fjNtrn`. Elles sont illisibles et elles changeront à la prochaine mise en ligne du site. Je me suis donc appuyé le plus possible sur les attributs stables comme `data-testid` et `type="article"`, sauf pour l'heure où je n'avais rien d'autre que la classe.

### Ce que j'observe dans les données

Le champ `chapeau` est vide sur les 46 articles. La page d'accueil des Echos n'affiche aucun texte d'accroche, uniquement des titres : `document.querySelectorAll('article p')` renvoie zéro élément. Pour le récupérer il faudrait ouvrir les 46 articles un par un, ce qui sort du cadre du TD.

`heure_publi` n'est remplie que pour 6 articles et `rubrique` pour 38, puisque chaque bloc ne porte qu'une partie de l'information.

34 articles sur 46 sont premium, ce qui colle bien au modèle du journal.

Je n'ai pas mis de scroll, contrairement au TD 2.1. J'ai vérifié, la page ne charge rien de plus : 46 blocs avant et 46 après 5 scrolls. Il n'y a pas de chargement progressif ici.

Il reste 1 doublon, un article qui apparaît dans les deux blocs. Le code du sujet ne prévoit pas de dédoublonnage, donc je ne l'ai pas ajouté.

### Pourquoi Selenium et pas requests avec BeautifulSoup

Ici ce n'est pas une question de JavaScript, c'est un blocage au niveau du CDN. Akamai renvoie 403 à toute requête faite avec `requests`, quel que soit le User-Agent, parce qu'il regarde aussi l'empreinte TLS et l'ordre des en-têtes HTTP. Seul un vrai navigateur passe.

### Le gain en headless : aucun, alors que le sujet annonce 2 à 3 fois

Voici mes mesures en relançant le script plusieurs fois :

| Essai | Normal | Headless | Gain affiché |
| --- | --- | --- | --- |
| 1 | 2,7 s | 2,3 s | 1,2x |
| 2 | 2,3 s | 3,0 s | 0,8x |
| 3 | 2,7 s | 2,7 s | 1,0x |

Il n'y a aucun gain. Le rapport passe d'un côté et de l'autre de 1,0x selon les essais, le headless est parfois plus rapide et parfois plus lent. C'est du bruit de mesure. Un seul chargement de page ne permet pas de conclure, il faudrait faire la moyenne sur plusieurs dizaines de pages.

L'explication me paraît logique : sur un seul chargement, le temps est surtout pris par le réseau (DNS, TLS, téléchargement, exécution du JavaScript), pas par l'affichage. Le headless économise le dessin des pixels, ce qui est négligeable ici, et il paie en plus le démarrage d'une deuxième instance de Chrome. Le gain de 2 à 3 fois se verrait sur un scraping de plusieurs centaines de pages, ou sur une machine sans carte graphique.

J'ai aussi rencontré un piège intéressant. En headless, Chrome annonce `HeadlessChrome` dans son User-Agent, et Akamai renvoie la page `Access Denied` : le scraper plantait sur le `WebDriverWait`. J'ai ajouté une ligne dans `make_driver()` pour forcer un User-Agent normal quand `headless=True`, et ça passe. C'est un bon exemple de ce que raconte le Défi 2 du sujet, le mode headless rend le navigateur plus facile à détecter.

### Les fichiers

`j2/tp/lesechos_scraper.py` pour le scraper et `j2/tp/lesechos.json` pour l'export (46 articles et 5 champs chacun).

---

## 6. Pour aller plus loin - Défis autonomes (Jour 2)

### Défi 1 - Cookie forensics en conditions réelles

L'analyse complète est dans `j2/tp/defi1_notes.md`. Je l'ai faite dans DevTools, onglet Application puis Cookies, et je l'ai croisée avec la [politique cookies officielle de Doctolib](https://media.doctolib.com/image/upload/v1776951636/legal/B2C-CookiePolicy-Update_APR25-FR.pdf) pour comparer ce qui est annoncé et ce qui est vraiment déposé. Voici les trois réponses en résumé.

**Trouver 3 cookies de domaine tiers.** Je n'en ai trouvé aucun. Les 14 cookies déposés après « Accepter » sont tous sur `www.doctolib.fr`, `.doctolib.fr` ou `.doctolib.com`. J'ai insisté en chargeant Google Maps puis une fiche de praticien, toujours rien. Par contre la politique, elle, cite bien Meta, Datadog RUM et Adjust SDK : ils ne se déclenchent que si on arrive depuis une pub ou depuis l'appli mobile. C'est ce que je retiens du défi, ce qui est annoncé n'est pas ce qui est déposé, et l'onglet Cookies seul ne suffit pas. À défaut de cookies tiers, j'ai analysé les 3 qui ressemblent le plus à du tracking, dont `altid`, un identifiant unique qui reste 13 mois, soit le maximum recommandé par la CNIL, et `__cf_bm`, posé par Cloudflare sur `.doctolib.com` alors que je visite `doctolib.fr`, et réglé en `SameSite=None` pour pouvoir circuler entre sites. J'ai aussi comparé les durées annoncées et les durées réelles, elles sont correctes partout. Enfin, en décodant le `didomi_token` je vois que « Tout accepter » active 6 finalités pour une seule entreprise, Doctolib, dont une qui couvre l'analyse de mes données de santé, mes rendez-vous compris, y compris pour des outils d'intelligence artificielle.

**Le cookie à reproduire pour la stratégie 2.** C'est `didomi_token`, sur `.doctolib.fr`. Je l'ai vérifié en comparant trois sessions neuves : sans cookie la bannière est visible, avec `euconsent-v2` seul elle est encore visible, avec `didomi_token` seul elle disparaît. Le relevé DevTools explique pourquoi ça marche : `didomi_token` et `euconsent-v2` sont les deux seuls cookies sans `HttpOnly`, `Secure` ni `SameSite`, donc les seuls que je peux écrire moi-même, contrairement à `_doctolib_session` et `__cf_bm`.

**Comparaison avec un autre site.** J'ai pris Maiia, parce que c'est un concurrent direct de Doctolib. Les noms de cookies ne sont pas les mêmes, parce qu'ils dépendent de la solution de consentement et pas du site : Doctolib passe par Didomi, Maiia par tarteaucitron, une solution française open source. Maiia dépose 13 cookies avant tout consentement contre 7 chez Doctolib, avec Dynatrace, DataDome et F5, et c'est le seul des deux à faire appel à de vraies régies publicitaires : Facebook Pixel, LinkedIn Insight et Matomo. Son cookie de consentement est stocké en clair, `!facebookpixel=true!linkedininsighttag=true!…`, là où Doctolib encode en base64.

Ce qui ressort de tout ça : ni Doctolib ni Maiia ne déposent de cookie sur un domaine tiers. Même sur Maiia après avoir tout accepté, le pixel Facebook écrit son cookie `_fbp` sur `.maiia.com` et pas sur `facebook.com`. Le suivi publicitaire existe toujours, mais il est passé du cookie tiers à un cookie posé sur le site lui-même, complété par un appel réseau. C'est ce qui rend la question 1 du sujet compliquée à traiter telle qu'elle est posée.

### Défi 2 - Empreinte anti-bot de mon driver

Le code est dans `j2/tp/defi2_bot_detection.py` et l'analyse complète dans `j2/tp/defi2_notes.md`. J'ai lancé les trois configurations sur `https://bot.sannysoft.com` et gardé une capture de chacune dans `j2/tp/screenshots/` : `bot_normal.png`, `bot_stealth.png` et `bot_headless.png`.

**Quels champs passent de rouge à vert.** Un seul, `WebDriver (New)`. Sur les 31 tests de la page, c'est le seul qui est rouge quand je lance Chrome sans rien configurer. Il lit `navigator.webdriver`, la propriété que Chrome met à `true` quand il est piloté. Tout le reste est déjà vert au départ, ce qui se comprend : un Chrome piloté reste un vrai Chrome, il n'y a qu'un drapeau planté par le driver, et les deux options du sujet servent juste à l'enlever.

**Le champ webdriver est-il encore détecté en mode furtif.** Non, il passe au vert et la page ne signale plus rien du tout. Mais ça ne prouve pas grand-chose, et j'ai de quoi le montrer avec mon propre TP. Sannysoft ne teste que des propriétés lisibles en JavaScript depuis la page. Les vraies protections regardent l'empreinte TLS, l'ordre des en-têtes et l'adresse IP, donc avant même que le JavaScript ne s'exécute. Sur Les Echos, `requests` reçoit un 403 d'Akamai quel que soit le User-Agent, et mon Chrome headless avec ces mêmes flags, celui qui affiche 100 % de vert sur sannysoft, se faisait renvoyer une page `Access Denied`.

**Quels champs deviennent rouges en headless.** Trois, avec pourtant les mêmes flags : `User Agent` (il contient `HeadlessChrome`), `HEADCHR_UA` (le test qui cherche justement ce mot) et `CHR_MEMORY`. J'ai vérifié si mon correctif du TD 2.2, forcer un User-Agent normal, suffisait à les corriger : les trois repassent au vert, y compris `CHR_MEMORY`. Comme `performance.memory` existe dans les deux modes, j'en déduis que ce test se base sur le User-Agent déclaré et pas sur une vraie différence de capacité. Une seule chaîne de caractères fait donc basculer trois lignes du tableau, ce qui explique aussi pourquoi Akamai a laissé passer mon headless dès que j'ai forcé le User-Agent.

---

## 7. Installation

```bash
pip install -r requirements.txt
```
