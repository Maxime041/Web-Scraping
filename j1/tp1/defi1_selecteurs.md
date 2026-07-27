# Défi 1 - Sélecteurs CSS & Analyse (TrashTalk.co)

Site d'actualités choisi : **TrashTalk** (`https://trashtalk.co/category/news-nba/`) - Médias basket & NBA.

---

## 1. Sélecteurs CSS & Logique d'extraction

- **Carte / Conteneur** : `div`
- **Titre** : `a[href*='/20']` (texte extrait avec `.get_text(strip=True)`)
- **URL** : Attribut `['href']` du lien
- **Date** : Extraite du slug de l'URL (`/YYYY/MM/DD/` -> `YYYY-MM-DD`)
- **Catégorie** : `a[href*='/category/']` dans le conteneur

---

## 2. Analyse comparative (3 phrases)

1. Le scraping de TrashTalk est légèrement plus complexe que celui du Blog du Modérateur car le site n'utilise pas de balises sémantiques `<article>`.
2. Le sélecteur du titre reste similaire (une balise lien `<a>` englobant le titre de l'article).
3. La date s'est révélée plus simple à extraire directement depuis le format de l'URL (`/YYYY/MM/DD/...`) plutôt qu'en cherchant une balise `<time>`.
