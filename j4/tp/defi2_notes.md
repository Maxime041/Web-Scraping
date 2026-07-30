# Défi 2 : OSINT sur un domaine que je connais

Domaine analysé : **euforiayacht.com**, l'entreprise où je suis alternant. Rapport dans
`rapport_euforiayacht.com.json`, produit par le même script que le TD 4.1.

Le sujet demande un domaine qu'on connaît personnellement, et propose l'entreprise de stage. C'est
le cas idéal ici, parce que je peux comparer ce que le rapport sort avec ce que je sais déjà de la
maison. Sur un domaine inconnu, je n'aurais aucun moyen de dire ce qui est une découverte.

```
python td41_domaine.py euforiayacht.com
```

## Ce que contient le rapport

| Champ | Valeur |
| --- | --- |
| IP | 92.222.139.190 |
| registrar | OVH, SAS |
| création | 2009-05-25 |
| expiration | 2027-05-25 |
| pays | FR |
| serveurs de noms | DNS200.ANYCAST.ME, NS200.ANYCAST.ME |
| serveur web | Apache |
| X-Powered-By | **PHP/7.4** |
| HSTS | absent |
| CSP | absent |
| X-Frame-Options | absent |
| sous-domaines | 5 |

## Tout est chez OVH, et c'est un hébergement mutualisé

Trois éléments concordent. Le registrar est OVH, les serveurs de noms sont des `ANYCAST.ME` qui
appartiennent à OVH, et le nom inverse de l'IP est `cluster028.hosting.ovh.net`.

Ce dernier détail est le plus parlant. Le mot `cluster` et le mot `hosting` indiquent une offre
d'**hébergement mutualisé**, pas un serveur dédié. Le site partage donc sa machine avec d'autres
clients d'OVH.

Le domaine est déposé depuis 2009, ce qui donne 17 ans d'ancienneté, et il est valide jusqu'en
2027.

## Les sous-domaines trouvés

```
www.euforiayacht.com
brokerage.euforiayacht.com
img.newsletter.euforiayacht.com
r.newsletter.euforiayacht.com
```

Sur les cinq lignes du rapport, l'une est le domaine lui-même, il reste donc **4 sous-domaines**.

Je connaissais `www`, qui est le site public. Les **trois autres, je ne les avais pas identifiés**
avant de lancer le script, alors que je travaille dans l'entreprise.

`brokerage` est une activité de courtage de bateaux, séparée du site principal. J'ai vérifié qu'il
répond, il renvoie bien un 200.

Les deux `newsletter` sont plus instructifs. Le sous-domaine `img.newsletter` sert à héberger les
images des campagnes d'e-mailing, et `r.newsletter` est presque certainement le domaine de
redirection utilisé pour tracer les clics dans les courriels. Ces deux noms révèlent donc qu'un
**outil d'e-mailing** est en place, et ce n'est écrit nulle part sur le site.

C'est l'intérêt de crt.sh. Ces trois sous-domaines n'apparaissent dans aucun menu du site, mais
comme un certificat TLS a été demandé pour chacun, ils sont publiés dans les journaux de
Certificate Transparency et donc consultables par n'importe qui.

Le fait que je sois alternant dans l'entreprise et que je découvre quand même trois adresses sur
quatre en dit long. Quelqu'un d'extérieur obtient en une requête une cartographie que je n'avais
pas en interne.

## Le serveur web est identifié, et c'est un problème

Réponse à la question du sujet, oui, et deux fois plutôt qu'une.

```
Server        : Apache
X-Powered-By  : PHP/7.4
```

Le premier en-tête annonce le serveur web, le second annonce le langage **et sa version**.

**Pourquoi c'est utile à un attaquant.** PHP 7.4 n'est plus maintenu depuis novembre 2022. Il ne
reçoit donc plus aucun correctif de sécurité. Un attaquant qui lit cet en-tête sait immédiatement
que le site tourne sur une version abandonnée depuis plus de trois ans, et il peut chercher les
failles publiées depuis cette date en sachant qu'aucune n'a été corrigée.

Sans cet en-tête, il devrait deviner la version en testant des comportements, ce qui est lent et
bruyant dans les journaux du serveur. Là, l'information est donnée d'entrée.

C'est la différence avec TMDB analysé au TD 4.1, qui n'expose **aucun** `X-Powered-By`. Rien n'y
fuite sur la couche applicative.

À cela s'ajoute l'absence des trois protections d'en-tête. Pas de HSTS, donc le HTTPS n'est pas
imposé au navigateur. Pas de CSP, donc rien n'encadre les scripts chargés. Pas de
`X-Frame-Options`, donc la page peut être insérée dans une iframe sur un autre site.

Le `robots.txt` complète le tableau. Il contient un bloc `# START YOAST BLOCK`, ce qui identifie un
site **WordPress** équipé de l'extension Yoast SEO. La ligne `Disallow:` y est vide, donc tout est
autorisé au crawl.

## Y a-t-il de la préprod exposée ?

Non, et c'est la bonne nouvelle du rapport. Aucun sous-domaine ne s'appelle `test`, `dev`,
`staging`, `preprod` ou `recette`. Les quatre trouvés correspondent tous à des usages de
production.

Le contraste avec le TD 4.1 est net, puisque TMDB expose de son côté `api-test` et `www-test`.

Le risque d'un tel sous-domaine, quand il existe, tient à ce qu'il est presque toujours moins
protégé que la production. On y trouve des mots de passe faibles, des données réelles copiées pour
les tests, des messages d'erreur détaillés et des versions logicielles plus anciennes. C'est une
porte d'entrée qui donne souvent accès aux mêmes données que le site officiel.

## Ce qu'un auditeur externe apprendrait en 5 minutes

Le site est hébergé chez OVH sur une offre mutualisée, ce que révèle le nom `cluster028.hosting.ovh.net`,
avec un domaine déposé depuis 2009 chez le même prestataire. Il tourne sous WordPress avec
l'extension Yoast, sur Apache et **PHP 7.4**, une version qui ne reçoit plus de correctif de
sécurité depuis novembre 2022, information donnée gratuitement par l'en-tête `X-Powered-By`.
Aucune des trois protections d'en-tête courantes n'est activée, ni HSTS, ni CSP, ni
`X-Frame-Options`. Enfin, les journaux de certificats révèlent trois sous-domaines absents du site
public, dont deux liés à un outil d'e-mailing, ce qui renseigne sur les outils utilisés en
interne. Rien de tout cela n'a nécessité autre chose que des registres publics.

## Les fichiers

`rapport_euforiayacht.com.json` pour le rapport, produit par `td41_domaine.py`.
