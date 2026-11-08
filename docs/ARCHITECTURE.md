# Architecture V1

## Flux retenu

```text
Crypto Mini --(petit JSON local, remplacement atomique, <= 30 min)--> Intel
Stock Intel ----------------------------------------------------------> Intel aggregator
Intel aggregator --(snapshot consolidé, auth serveur, sans secrets)--> Cloudflare Worker/KV or D1
PWA iPhone/Mac --(passkey/WebAuthn, lecture seule)-------------------> cloud API
```

Le Mini n'héberge pas de serveur permanent et ne contacte pas la PWA. L'Intel est le seul point de consolidation et de publication. La PWA ne contacte jamais directement Alpaca, IBKR, Binance, OpenAI, JEV ou les runtimes.

## Snapshot

Le contrat est `schema/snapshot.schema.json`. Une publication remplace l'état courant ; les historiques utiles (transactions, résultats mûrs, incidents) seront traités séparément après validation du stockage. Les valeurs sans preuve sont `null` avec `status: UNAVAILABLE` et une raison.

## Sécurité et non-régression

La V1 ne contient pas d'authentification serveur ni d'exporteur réel : ces fonctions sont volontairement bloquées jusqu'à validation. WebAuthn doit être implémenté côté Worker avec challenge serveur, vérification d'origine, expiration de session, récupération hors bande et cookies HttpOnly/Secure/SameSite. Les clés et certificats restent hors Git.

## Garde-fous d'intégration

Avant un exporteur réel : mesurer le temps CPU, RSS, I/O, requêtes SQLite et impact sur le runtime Mini sur une fenêtre bornée ; vérifier les droits de lecture ; utiliser un timeout ; écrire dans un fichier temporaire puis `rename` ; ne jamais bloquer le moteur ; journaliser `last_success`, `duration_ms`, `source_revision` et les raisons d'absence.
