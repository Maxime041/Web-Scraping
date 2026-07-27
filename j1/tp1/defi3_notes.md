# Défi 3 - Benchmark honnête du throttling

## Tableau des mesures réelles d'exécution

| Pages | DELAY 0.5s | DELAY 1.0s | DELAY 2.0s |
|-------|------------|------------|------------|
| **2** | 1.3 s      | 2.2 s      | 4.3 s      |
| **5** | 3.1 s      | 5.6 s      | 10.6 s     |
| **10**| 6.5 s      | 11.3 s     | 21.3 s     |

---

## Questions de réflexion

1. **Au-delà de quel délai le scraping de 200 articles dépasse 30 minutes ?**
   - 200 articles représentent 25 pages. Pour dépasser 30 minutes (1800 secondes), il faudrait un délai supérieur à **72 secondes par requête** (environ 1 min 12 s par page).

2. **Pour respecter une politique < 1 req/2 s, combien d'heures pour 500 articles ?**
   - 500 articles représentent 63 pages. À raison de ~2,1 secondes par requête, le scraping total prend environ **132 secondes**, soit **0,037 heure** (environ 2 min 12 s).

3. **Conclusion : quel compromis vitesse/discrétion choisiriez-vous en production ?**
   - Un délai de **1,0 à 1,5 seconde** entre chaque requête est le compromis idéal en production pour garantir la discrétion et éviter les blocages (HTTP 429) tout en restant très rapide.
