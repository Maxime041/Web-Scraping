# Défi 1 : spider sur un site de ma région

## Le site choisi

J'ai pris **Nice Presse**, un média local, et sa rubrique actu régionale :
`https://nicepresse.com/page/actu-regionale/`.

Le `robots.txt` de Nice Presse autorise la page, je l'ai vérifié avec le même moteur que Scrapy.
Le projet est dans `j3/tp/nicepresse/`, l'export dans `articles.csv`.

## Ce que j'ai vérifié au scrapy shell avant d'écrire le spider

**La pagination est réelle.** Le bouton « En voir plus » ressemble à un chargement JavaScript,
mais en regardant le HTML c'est un vrai lien :

```html
<div class="main-pagination pagination-more" data-type="load-more">
  <a href="https://nicepresse.com/page/actu-regionale/page/2/" class="ts-button load-button">
    En voir plus
  </a>
</div>
```

J'ai testé les pages 2 et 3 : elles renvoient bien du contenu nouveau. Je peux donc utiliser la
récursion classique du cours, `yield response.follow(suivant, callback=self.parse)`, sans avoir
besoin de Selenium.

**Le titre change de balise mais garde sa classe.** Les 3 premiers articles de chaque page ont
leur titre dans un `h2`, les 10 suivants dans un `h4`. En revanche tous portent la classe
`post-title`. Le sélecteur `article .post-title a` attrape donc les 13 d'un coup.

**La date est sur la fiche, pas sur la liste.** La page de rubrique n'affiche aucune date. Sur
l'article, il y a une vraie balise `<time datetime="2026-06-26T19:03:01+02:00">`. J'ai donc fait
un crawl à deux niveaux, comme pour AlloCiné.

## Le spider

`parse()` récupère les 13 cartes de la page et programme une requête vers chaque fiche, en
passant le titre avec `cb_kwargs`. Puis il suit le lien « En voir plus » jusqu'à la page 3.
`parse_article()` lit la date et émet l'item.

L'`ArticleItem` a 3 champs, `titre`, `url` et `date`. Le `CleanPipeline` fait le trim des textes
et coupe la date à `2026-06-26`, sans l'heure ni le fuseau.

Un détail que je n'ai pas eu à coder : 3 articles se répètent sur chaque page, c'est le bloc « à
la une » qui reste en haut. Scrapy les a filtrés tout seul, les statistiques affichent
`dupefilter/filtered: 6`. Avec `requests` il aurait fallu gérer ça à la main.

## Résultat

33 articles dans `articles.csv`, 33 URLs distinctes, aucun champ vide, et des dates qui s'étalent
du 11/05/2026 au 30/06/2026. Le crawl prend 45 secondes pour 37 requêtes.

```
2026-06-26  Région PACA : un bébé de 18 mois meurt de chaud, laissé seul...
2026-06-25  Les députés du groupe d'Eric Ciotti quittent l'hémicycle...
2026-06-24  Région PACA. Les maires d'Aix-Marseille-Provence négocient...
```

## Les 5 lignes demandées : différences avec AlloCiné

1. **AlloCiné est un catalogue, Nice Presse est un flux.** AlloCiné classe des fiches stables dans
   un ordre figé, alors qu'un site d'actualité change plusieurs fois par jour. Relancer mon spider
   demain ne donnera pas les mêmes 33 articles.
2. **Les données utiles sont réparties sur deux niveaux**, le titre sur la liste et la date sur la
   fiche. Chez AlloCiné aussi il faut ouvrir la fiche, mais parce qu'elle contient plus de
   détails, pas parce que la liste est incomplète.
3. **Il faut viser la classe plutôt que la balise.** Sur AlloCiné, `h2.meta-title` marche pour les
   10 films d'une page. Ici la balise change entre `h2` et `h4` selon la position dans la grille,
   seule la classe `post-title` est commune.
4. **La pagination se déguise.** Chez AlloCiné les liens de pages sont visibles et numérotés. Ici
   le bouton « En voir plus » a tout d'un chargement JavaScript, alors que c'est un lien normal.
   Il faut ouvrir le HTML pour trancher, l'apparence de la page ne suffit pas.
5. **La structure est finalement plus prévisible que je ne le pensais**, parce que le site tourne
   sous WordPress : de vraies balises `<article>`, des classes stables comme `post-title`, une
   balise `<time>` standard. AlloCiné, avec ses classes maison, est en fait moins standardisé.

**Pourquoi ces différences ?** AlloCiné est une base de données affichée par un gabarit unique,
donc régulier par construction, mais avec des classes propriétaires. Nice Presse est un CMS grand
public, donc son HTML suit les conventions de WordPress, ce qui le rend lisible même sans
connaître le site. Ce qui varie chez lui, c'est la mise en page éditoriale (grille à 3 puis 10
articles), pas le vocabulaire HTML.

## Les fichiers

`j3/tp/nicepresse/` pour le projet et `j3/tp/nicepresse/articles.csv` pour l'export.

Pour le lancer, depuis `j3/tp/nicepresse/` :

```
scrapy crawl articles -L INFO
```
