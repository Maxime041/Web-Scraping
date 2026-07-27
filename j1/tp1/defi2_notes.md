# Défi 2 - Détecter les nouveautés entre deux crawls

## Résultats d'exécution réels

Comparaison entre `articles.csv` et `trashtalk_articles.csv` :
- **Nouveaux**  : 14
- **Disparus**  : 9
- **Stables**   : 0

---

## Question de réflexion

1. **Combien d'articles nouveaux apparaissent en 24h sur ce site ?**
   - Le Blog du Modérateur publie en moyenne **5 à 10 articles par jour ouvrable**.

2. **Quel intervalle de crawl garantit de ne manquer aucune publication sans dépasser 1 crawl/heure ?**
   - Un crawl **toutes les 4 à 6 heures** (ou 1 à 2 fois par jour) garantit de récupérer 100% des nouveaux articles publiés sans manquer aucun contenu tout en respectant une fréquence très modérée (< 1 crawl/heure).
