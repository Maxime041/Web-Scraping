# README - Cours Web Scraping (Jour 1)

Ce dépôt contient les travaux dirigés (TD) et le travail pratique (TP1) du Jour 1 du cours de Web Scraping.

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
