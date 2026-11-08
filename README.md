# Agent Monitor

PWA privée, responsive et strictement en lecture seule pour superviser Agent Stock et Agent Crypto.

## V1 locale

Cette première version fonctionne sans backend et utilise un snapshot de démonstration explicitement marqué `DEMO`. Elle ne se connecte à aucun runtime, broker, fournisseur de données ou service cloud.

```sh
cd /Users/ssg/agent-monitor
python3 -m http.server 4173 --directory dist
```

Ouvrir `http://127.0.0.1:4173` sur Mac. Les tests ne nécessitent aucune dépendance externe :

```sh
python3 -B tests/test_snapshot.py
```

Le consolidateur local Stock + Crypto est documenté dans `docs/REAL_DATA_INGESTION.md`. Il est read-only, sans réseau, et ne doit jamais écrire un vrai `snapshot.json` dans le dépôt public.

## Architecture approuvée

Le Mini produit périodiquement un petit snapshot local remplaçable atomiquement. L'Intel récupère le snapshot, ajoute son état Stock, valide le schéma et publie un snapshot consolidé vers un service serverless. La PWA lit uniquement la dernière vue consolidée. Aucun serveur permanent supplémentaire ne doit tourner sur le Mini ou l'Intel.

La fréquence initiale est de 30 minutes maximum. La charge réelle de l'extraction Mini doit être mesurée avant toute installation d'exporteur ou de tâche périodique.

## Sécurité

- Passkey/WebAuthn avec Face ID : à implémenter côté serveur, avec récupération séparée et sessions protégées.
- Aucun secret, token, identifiant de broker ou fichier brut sensible dans la PWA ou Git.
- Les états `RESEARCH`, `SIMULATION`, `PAPER` et `LIVE` sont toujours distincts.
- Les valeurs inconnues restent `UNAVAILABLE`; aucun chiffre de démonstration ne doit être présenté comme réel.
- Aucun bouton d'ordre, de redémarrage, de changement de quota ou de mutation des agents.

## Limites connues

Cloudflare Free, WebAuthn serveur, droits de lecture et coût réel des requêtes SQLite restent à vérifier avant V2. Aucun déploiement cloud n'a été effectué.
