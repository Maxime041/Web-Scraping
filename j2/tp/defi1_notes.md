# Défi 1 : cookie forensics en conditions réelles

J'ai fait cette analyse le 28/07/2026 sur `https://www.doctolib.fr/hematologue/nice`, après
avoir cliqué sur « Accepter » dans la bannière.

Je me suis appuyé sur deux choses : ce que j'ai lu dans DevTools > Application > Cookies, et la
politique cookies de Doctolib
([le PDF officiel](https://media.doctolib.com/image/upload/v1776951636/legal/B2C-CookiePolicy-Update_APR25-FR.pdf)),
qui m'a permis de comparer ce que Doctolib annonce et ce qu'il dépose vraiment.

Un point d'attention sur DevTools : il faut bien regarder tous les domaines listés dans le
panneau de gauche, et pas seulement celui du site sur lequel on se trouve. C'est justement en
dépliant les autres que j'ai vu le cookie posé sur `.doctolib.com` alors que je visitais
`doctolib.fr`.

---

## Question 1 : trouver 3 cookies de domaine tiers

**Je n'en ai trouvé aucun.** Les 14 cookies déposés après le clic sur « Accepter » sont répartis
sur 3 domaines, et les 3 appartiennent à Doctolib : `www.doctolib.fr` (10 cookies),
`.doctolib.fr` (3) et `.doctolib.com` (1).

Pas de `google-analytics.com`, pas de `doubleclick.net`, pas de `facebook.com`. J'ai d'abord cru
que la page n'avait pas fini de charger, donc j'ai insisté : j'ai cliqué sur « Afficher la
carte » pour déclencher Google Maps, puis j'ai ouvert une fiche de praticien. Toujours rien. Le
consentement pour Maps est même stocké chez Doctolib, dans un cookie `google_maps_consent_1.0`.

### Sauf que la politique, elle, parle bien de partenaires tiers

En lisant le PDF, je vois des partenaires que je n'ai jamais vus apparaître dans DevTools :

| Partenaire annoncé | À quoi il sert | Pourquoi je ne l'ai pas vu |
| --- | --- | --- |
| Meta | relier une action sur le site à une pub Doctolib | il se déclenche seulement si on arrive en cliquant sur une pub |
| Datadog RUM | mesurer les performances du site | pas déclenché sur une simple visite |
| Adjust SDK | relier les actions aux téléchargements de l'appli | ça concerne l'application mobile, pas le site |

Ce que j'en retiens : ce n'est pas parce qu'on ne voit aucun cookie tiers dans DevTools qu'il
n'y a pas de tiers dans le circuit. Ici ils sont conditionnés à un parcours précis. Si je
m'étais arrêté à l'onglet Cookies, j'aurais conclu à tort qu'il n'y a aucun partenaire.

Ça reste cohérent avec le métier de Doctolib. Ils hébergent des données de santé, donc brancher
une régie publicitaire directement sur `doctolib.fr` serait beaucoup plus risqué pour eux.

### Le même constat sur Maiia

Je me suis dit que Doctolib était peut-être un cas particulier, donc j'ai testé Maiia, qui
annonce clairement Facebook Pixel et LinkedIn Insight dans son panneau de consentement. J'ai
cliqué sur « Tout accepter » et j'ai regardé ce qui arrivait.

Le pixel Facebook s'active bien, un cookie `_fbp` apparaît. Mais il est posé sur `.maiia.com`,
pas sur `facebook.com`. Donc même sur un site qui travaille avec des régies publicitaires, je ne
trouve pas de cookie déposé sur un domaine tiers.

L'explication est assez logique : les navigateurs bloquent de plus en plus les cookies tiers,
donc les régies ont changé de méthode. Le pixel écrit maintenant un cookie sur le site visité,
puis renvoie l'identifiant à Meta par une requête réseau. Le suivi entre sites existe toujours,
il ne passe simplement plus par un cookie tiers.

Du coup la question du sujet est un peu dépassée. Aujourd'hui, regarder `_fbp`, `_pk_id` ou
`altid` apprend beaucoup plus que chercher un domaine tiers qu'on ne trouvera pas.

### Les 3 cookies qui ressemblent le plus à du tracking

Puisqu'il n'y a pas de cookie tiers, j'ai analysé les 3 cookies de Doctolib qui font le même
travail de suivi.

| Nom | Domaine | Durée de vie | Valeur | Options |
| --- | --- | --- | --- | --- |
| `altid` | `www.doctolib.fr` | 13 mois (expire le 01/09/2027) | encodée, du JSON avec un caractère `%` à la place des guillemets : `{"id":"3ff58b2b-24c7-4fc4-8256-cb5ac8158bbb"}` | Secure, SameSite=Lax |
| `a7did` | `www.doctolib.fr` | 7 jours (expire le 04/08/2026) | même format, autre identifiant | Secure, SameSite=Lax |
| `__cf_bm` | `.doctolib.com` | 30 minutes | illisible, 228 octets | HttpOnly, Secure, SameSite=None |

`altid` est celui qui me dérange le plus : c'est un identifiant unique qui reste 13 mois sur ma
machine. C'est pile le maximum recommandé par la CNIL pour ce type de traceur, donc c'est
autorisé, mais on est à la limite haute. À noter que Chrome plafonne de toute façon tous les
cookies à 400 jours, ce qui tombe à peu près sur la même durée.

`a7did` fonctionne pareil mais sur 7 jours.

`__cf_bm` est le cas le plus intéressant, pour deux raisons qui se cumulent. D'abord il n'est
pas posé par Doctolib mais par Cloudflare, qui s'occupe de bloquer les robots. Ensuite il est
sur `.doctolib.com` alors que je suis en train de visiter `doctolib.fr`, donc sur un autre nom
de domaine. Et son option `SameSite=None` confirme qu'il est fait exprès pour circuler d'un site
à l'autre. C'est le seul cookie du relevé réglé comme ça.

Les cookies `acid_*` (`acid_booking_traffic_and_cvr`, `acid_search_result_page_spe`,
`acid_smart_ranking_booking_behaviour`) servent à faire de l'A/B testing sur 30 minutes. Leurs
noms disent clairement ce qui est mesuré, et leur valeur contient un compteur de visites.

### Ce qui est annoncé et ce que j'ai vraiment vu

J'ai comparé les durées écrites dans le PDF avec les dates d'expiration que j'ai relevées :

| Cookie | Durée annoncée | Date que j'ai vue | Résultat |
| --- | --- | --- | --- |
| `ssid` | 13 mois | 28/08/2027 | correct |
| `altid` | 13 mois | 01/09/2027 | correct |
| `a7did` | 7 jours | 04/08/2026 | correct |
| `astid` et `esid` | Session | Session | correct |
| `locale` | 3 mois | 28/10/2026 | correct |
| `didomi_token` | 6 mois | 27/01/2027 | correct |
| `euconsent-v2` | 6 mois | 27/01/2027 | correct |
| `__cf_bm` | 30 minutes | 30 minutes | correct |
| les `acid_*` | Session | 30 minutes | plus court qu'annoncé |

Rien qui joue en défaveur de l'utilisateur. J'ai quand même noté deux petites choses : les
`acid_*` durent 30 minutes alors qu'ils sont annoncés en « Session », et le PDF écrit le cookie
`eu-consent-v2` alors qu'en vrai il s'appelle `euconsent-v2`, sans tiret. C'est le nom standard
de l'IAB, donc c'est bien le PDF qui se trompe.

### Ce qu'on accepte vraiment en cliquant « Accepter »

Le cookie `didomi_token` est du JSON encodé en base64. Une fois décodé :

```json
{
  "user_id": "19fa8bff-a85a-68b1-bf0f-d135a2366e44",
  "created": "2026-07-28T12:43:01.637Z",
  "updated": "2026-07-28T12:47:04.823Z",
  "version": 2,
  "purposes": {
    "enabled": ["analytics-P8YGj7DH", "analytics-NGqxWbmn", "displayta-V8kMenYa",
                "displayta-VrPPVnHh", "mesureda-DETQz67A", "adsperfor-zxYrhLTd"]
  },
  "vendors": { "enabled": ["c:doctolibf-4YCRxfz4"] }
}
```

Ces 6 codes correspondent aux 6 finalités que propose la bannière (il y en a une septième, les
cookies obligatoires, mais elle est marquée « Requis » et on ne peut pas la refuser). Les
préfixes sont des abréviations du nom de la finalité :

| Code dans le cookie | Finalité dans la bannière |
| --- | --- |
| `mesureda-…` | mesure d'audience |
| `analytics-…` (il y en a deux) | mesure des campagnes de prévention, et analyse avec données de santé |
| `displayta-…` (il y en a deux) | personnalisation des contenus, et des campagnes de prévention |
| `adsperfor-…` | mesure des campagnes publicitaires |

Le compte tombe juste (6 finalités, 6 codes activés). Par contre, savoir lequel des deux
`analytics-` correspond à quelle finalité, c'est une déduction de ma part à partir des préfixes,
je ne peux pas le prouver.

Deux choses ressortent de ce décodage.

La première, c'est que `vendors.enabled` ne contient qu'une seule entrée : Doctolib lui-même.
J'autorise donc 6 finalités, mais une seule entreprise. Le cookie `euconsent-v2` le confirme :
c'est la chaîne standard de l'IAB, et elle est presque uniquement composée de `A`, ce qui
correspond à des zéros. Aucune régie de la liste IAB n'est autorisée.

La deuxième, c'est que j'accepte l'analyse de données personnelles de santé. La bannière est
explicite là-dessus : ça couvre les rendez-vous que je prends sur Doctolib, pour faire des
statistiques et améliorer leurs services, en incluant les outils d'intelligence artificielle.
C'est de loin le point le plus important des 6, et c'est celui qu'on accepte sans le lire.

---

## Question 2 : quel cookie la stratégie 2 doit reproduire

**C'est `didomi_token`, sur le domaine `.doctolib.fr`.**

Je ne l'ai pas deviné, je l'ai vérifié. J'ai ouvert une fenêtre de navigation privée pour partir
d'une session vide, j'ai ajouté le cookie directement dans DevTools, puis j'ai rechargé la page
pour voir si la bannière revenait :

| Cookie que j'injecte | Bannière |
| --- | --- |
| aucun (pour comparer) | visible |
| `euconsent-v2` tout seul | visible |
| `didomi_token` tout seul | absente |

`euconsent-v2` ne suffit pas. C'est normal quand on y réfléchit : cette chaîne sert à prévenir
les régies publicitaires, ce n'est pas là que Didomi range sa propre décision. C'est
`didomi_token` que Didomi relit au chargement pour savoir s'il doit afficher la bannière, et le
PDF le décrit d'ailleurs comme le cookie qui stocke le consentement par finalité et par
partenaire.

Le relevé DevTools m'explique aussi pourquoi l'injection est possible. `didomi_token` et
`euconsent-v2` sont les deux seuls cookies du lot qui n'ont ni `HttpOnly`, ni `Secure`, ni
`SameSite`. Ils sont donc lisibles et modifiables depuis le navigateur, et Selenium peut les
écrire sans problème. À l'inverse, `_doctolib_session` et `__cf_bm` sont en `HttpOnly` : je ne
peux pas les fabriquer moi-même.

Pour la valeur, le plus simple est de réutiliser le token récupéré après avoir cliqué une fois :

```python
driver.get("https://www.doctolib.fr")          # il faut déjà être sur le domaine
driver.add_cookie({
    "name": "didomi_token",
    "value": "eyJ1c2VyX2lkIjoiMTlmYThiZmYt...",   # le token récupéré après acceptation
    "domain": ".doctolib.fr",
    "path": "/",
})
driver.get("https://www.doctolib.fr/hematologue/nice")   # recharger pour qu'il soit relu
```

Deux détails m'ont bloqué au début. On ne peut pas ajouter un cookie pour un domaine sans y être
déjà, et il faut recharger la page après l'injection, sinon Didomi a déjà pris sa décision.

### Sur Maiia c'est encore plus simple

Maiia utilise tarteaucitron, et son cookie de consentement est stocké en clair :

```
tarteaucitron = !facebookpixel=true!linkedininsighttag=true!matomotagmanager=true!screeb=true
```

Pas d'encodage, pas de signature, pas d'identifiant : juste une liste de services avec `true` ou
`false`. Pour injecter un consentement sur Maiia, je peux écrire cette chaîne à la main, et même
choisir service par service en passant certains à `false`. Le cookie dure 12 mois.

En comparant avant et après le clic, j'ai remarqué que le cookie existe déjà à l'arrivée sur le
site, avec la valeur `!facebookpixel=wait!linkedininsighttag=wait!matomotagmanager=wait!screeb=wait`.
Le `wait` veut dire que je n'ai pas encore choisi. C'est plus lisible que chez Doctolib, où le
`didomi_token` est aussi présent avant le clic mais où il faut le décoder pour s'en rendre compte.

La comparaison est parlante : `didomi_token` fait 456 octets de base64 avec un identifiant
utilisateur et des dates, `tarteaucitron` fait 90 octets que n'importe qui peut lire. Deux
solutions différentes, deux niveaux d'opacité opposés, pour exactement la même fonction.

### Pourquoi l'injection est plus solide que le clic

Le clic dépend du texte du bouton et de la façon dont la page est construite. Je m'en suis rendu
compte sur le TP : le XPath du sujet, `contains(text(),"Accepter")`, ne marche pas sur Doctolib,
parce que le mot « Accepter » est dans un `<span>` à l'intérieur du bouton et que `text()` ne
regarde que le texte direct. Il faut écrire `contains(.,"Accepter")` ou viser l'identifiant
`didomi-notice-agree-button`.

Surtout, le clic peut rater sans qu'on s'en aperçoive. J'ai testé en laissant la bannière
ouverte : les cartes sont bien dans la page, donc `WebDriverWait` réussit et aucune erreur n'est
levée. Sauf que les cartes cachées derrière la fenêtre de consentement renvoient un texte vide,
parce que Selenium ne lit que ce qui est visible à l'écran. J'aurais exporté des fiches sans nom
ni adresse sans avoir le moindre message d'erreur. C'est le pire cas de figure : le script ne
plante pas, il produit des données fausses.

L'injection, elle, ne dépend d'aucun élément visuel. Elle marche même si Didomi refait le design
de sa bannière, et elle évite d'attendre que la fenêtre apparaisse puis disparaisse.

Sa limite, c'est que le token dure 6 mois et qu'il a un numéro de version (`"version": 2`), donc
il faudra le récupérer à nouveau de temps en temps. Le clic, lui, reste valable tant qu'il y a
un bouton à cliquer.

---

## Question 3 : comparaison avec Maiia

J'ai choisi Maiia parmi les trois sites proposés, parce que c'est un concurrent direct de
Doctolib sur la prise de rendez-vous médicaux.

| Site | Cookies avant consentement | Solution utilisée | Cookie de consentement | Format de la valeur |
| --- | --- | --- | --- | --- |
| Doctolib | 7 | Didomi | `didomi_token` | base64, 456 octets |
| Maiia | 13 | tarteaucitron | `tarteaucitron` | texte en clair, 90 octets |

Les noms ne sont donc pas les mêmes, et c'est la réponse à la question : le nom du cookie dépend
de la solution de consentement choisie, pas du site. Doctolib passe par Didomi, une solution
commerciale, alors que Maiia utilise tarteaucitron, une solution française open source. Deux
noms différents, et deux formats de valeur qui n'ont rien à voir.

### Maiia dépose beaucoup plus de cookies

13 cookies dès l'arrivée, contre 7 chez Doctolib, et avant même d'avoir cliqué sur quoi que ce
soit :

| Cookie | Domaine | Durée | À quoi il sert |
| --- | --- | --- | --- |
| `datadome` | `.maiia.com` | 12 mois | DataDome, blocage des robots. Secure et SameSite=None |
| `dtCookie`, `rxVisitor`, `dtSa`, `dtPC`, `rxvt` | `.maiia.com` | session à 12 mois | Dynatrace, mesure des performances |
| `TS017272e8`, `TSPD_101`, `TS2d35c511027` et les autres | `www.maiia.com` | session | F5 BigIP, répartition de charge |
| `tarteaucitron` | `www.maiia.com` | 12 mois | le consentement lui-même |

Et son panneau de consentement annonce de vraies régies publicitaires, ce que Doctolib ne fait
pas du tout : Matomo Tag Manager, Facebook Pixel, LinkedIn Insight et Screeb pour les sondages.
Après avoir tout accepté, deux familles de cookies apparaissent :

Ceux de Matomo : `_pk_id.5.0208` (13 mois), `_pk_ref.5.0208` (6 mois) et `_pk_ses.5.0208`
(30 minutes). Le `_pk_ref` stocke la page d'où je viens, et dans mon relevé il contient
`https://www.google.com/`. Matomo garde donc en mémoire que je suis arrivé depuis Google.

Et celui de Facebook : `_fbp`, posé sur `.maiia.com` comme je l'expliquais plus haut.

La différence de philosophie avec Doctolib est nette. Chez Doctolib, la liste des destinataires
ne contient que Doctolib. Chez Maiia, on partage avec Meta, LinkedIn, Matomo et Screeb. Et Maiia
dépose Dynatrace, DataDome et F5 avant que l'utilisateur ait donné son avis.

---

## Ce que j'ai appris

Ce qu'on accepte vraiment en cliquant « Tout accepter » sur Doctolib : 6 finalités pour une
seule entreprise, mais l'une d'elles couvre l'analyse de mes données de santé, mes rendez-vous
compris, et sert aussi à entraîner des outils d'IA. Le fait de décoder le `didomi_token` m'a
permis de le vérifier au lieu de le supposer.

Ce qui est annoncé n'est pas ce qui est déposé. La politique de Doctolib cite Meta, Datadog et
Adjust, et je n'ai vu aucun des trois. Regarder uniquement l'onglet Cookies ne suffit pas, il
faut croiser avec le document officiel.

Pourquoi l'injection de cookie est plus solide que le clic : les deux cookies de consentement
sont justement les seuls sans `HttpOnly`, `Secure` ni `SameSite`, donc les seuls que je peux
écrire moi-même. Alors que le clic peut rater en silence et me faire exporter des données
fausses.

Sur le suivi entre domaines, enfin : ni Doctolib ni Maiia n'en font par cookie. Les deux seuls
cookies réglés en `SameSite=None`, donc capables de circuler d'un site à l'autre, sont `__cf_bm`
chez Doctolib et `datadome` chez Maiia, et ce sont deux services anti-robots, pas de la
publicité. Le suivi publicitaire existe bien chez Maiia, avec Meta et LinkedIn, mais il passe
par un cookie posé sur le site lui-même comme `_fbp`. C'est ce déplacement du tiers vers le
first-party qui rend la question 1 du sujet compliquée à traiter telle qu'elle est posée.
