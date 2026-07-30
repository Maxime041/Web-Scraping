# Atelier 2 : les sélecteurs utilisés

Cible : `lachainemeteo.com`, 5 villes (Paris, Marseille, Lyon, Toulouse, Nice).
Voie 1 du sujet : Selenium en headless, avec `WebDriverWait` sur les éléments injectés.

La capture `capture_nice.png` montre la page de Nice telle que Selenium la voit après
acceptation du consentement.

## Pourquoi Selenium et pas requests

J'ai testé `requests` d'abord. Le HTML brut contient bien des températures, mais ni les
conditions, ni le créneau horaire, ni le bloc de détail : tout ça est injecté en JavaScript
après le chargement. Et surtout, une modale de consentement recouvre la page.

## Les sélecteurs, par champ

| Champ demandé | Page | Sélecteur | Exemple |
| --- | --- | --- | --- |
| température actuelle | aujourdhui | `[class*='quarter']`, 1re ligne finissant par `°` | `31°` |
| min du jour | aujourdhui | `.tt-tempe-min` | `26°` |
| max du jour | aujourdhui | `.tt-tempe-max` | `33°` |
| conditions | aujourdhui | `[class*='quarter']`, 1re ligne finissant par `.` | `Ensoleillé.` |
| heure de la mesure | aujourdhui | `[class*='forecast']`, dernière ligne | `Actualisé à 07h45 - Prochaine mise à jour à 11h00` |
| humidité | heure-par-heure | `.humidity .value` | **inexploitable, voir plus bas** |

Le bloc `[class*='quarter']` se lit ligne par ligne, dans cet ordre :

```
De 9h à 12h        <- créneau
31°                <- température
Ressenti 33°
Calme
Rafales
15 km/h
Ensoleillé.        <- conditions
Sans précipitations.
Aucun risque de pluie
Indice UV
5
Modéré
```

Je ne prends donc pas un sélecteur par valeur, mais je découpe le texte du bloc : la première
ligne qui finit par `°` est la température, la première qui finit par un point est la condition.
C'est plus robuste que de viser des classes générées comme `tempeFeltPrepondFactor`.

## Le piège du consentement

La modale « Faites un choix pour vos données » est dans une **iframe**, et son contenu n'est pas
disponible tout de suite. Deux conséquences.

Le XPath sur `//button[contains(., "ACCEPTER")]` ne trouve rien depuis la page principale, il
faut basculer dans l'iframe avec `switch_to.frame()`. Et comme l'iframe n'est pas prête au même
moment d'un lancement à l'autre, un essai unique échoue une fois sur deux. D'où la boucle de
`accepter_consentement()`, qui réessaie la page puis chaque iframe pendant 25 secondes.

Tant que la modale est affichée, `[class*='quarter']` existe dans le DOM mais son `.text` est
**vide**. Le script ne plante pas, il produit des champs vides. C'est exactement le piège
rencontré sur Doctolib au Jour 2 : Selenium ne lit que le texte visible à l'écran. J'ai perdu
plusieurs essais à conclure « pas d'humidité sur cette page » alors que je lisais simplement une
page masquée.

C'est pour ça que le script attend deux choses et pas une : la présence du bloc, puis le fait que
son texte ne soit plus vide.

```python
bloc = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='quarter']")))
WebDriverWait(driver, 20).until(lambda d: bloc.text.strip() != "")
```

## L'humidité n'est pas récupérable

Le sélecteur existe, `.humidity .value` sur la page heure par heure, et il renvoie bien `44%`.
Mais c'est un faux positif, et je m'en suis aperçu en comparant les villes :

- les **53 créneaux** de la page affichent tous `44%` ;
- Paris et Nice affichent la même valeur au même moment.

Ce n'est donc pas une mesure, c'est un remplissage affiché avant chargement. La page cite
d'ailleurs l'humidité parmi les paramètres réservés aux abonnés, avec la pression et la
visibilité. Sans compte payant, la vraie valeur n'est jamais chargée.

J'ai donc laissé le champ vide dans `meteo.json`. Livrer `44%` pour les cinq villes aurait donné
un fichier qui a l'air complet mais qui est faux, ce qui est pire qu'un champ vide.

## Résultat

4 champs sur 5 renseignés pour les 5 villes, dans `meteo.json`.

| ville | temp. | min | max | conditions |
| --- | --- | --- | --- | --- |
| Paris | 23° | 22° | 31° | Ciel couvert. |
| Marseille | 26° | 23° | 30° | Beau temps peu nuageux. |
| Lyon | 26° | 24° | 38° | Ensoleillé. |
| Toulouse | 23° | 21° | 34° | Ciel couvert. |
| Nice | 31° | 26° | 33° | Ensoleillé. |
