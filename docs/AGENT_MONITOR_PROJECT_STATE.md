# Agent Monitor — project checkpoint

## Checkpoint — 2026-11-09 — consolidateur local read-only, DEMO publique

### État actuel

Dépôt séparé local : `/Users/ssg/agent-monitor`, branche `main`, publié dans `https://github.com/f-duck/agent-monitor`. La PWA est une interface responsive strictement en lecture seule. GitHub Pages reste DEMO-only ; un consolidateur local accepte maintenant des snapshots Stock/Crypto réels sans réseau et produit un snapshot `LIVE_READ_ONLY` ou `STALE` hors du dépôt public.

### Dernier commit validé

Commit local de reprise : le hash exact est celui de `git rev-parse HEAD` et est remis dans le handoff final ; le checkpoint est versionné avec ce commit.

### Réalisé dans ce checkpoint

- Interface PWA iPhone/Mac : vue globale, états Stock/Crypto, santé, activité, alertes, métriques, chantiers et roadmap.
- Distinction `RESEARCH`, `SIMULATION`, `PAPER`, `LIVE` dans le contrat.
- Politique `UNAVAILABLE` pour toute valeur non mesurée ; aucun chiffre réel fictif.
- Snapshot consolidé versionné `1.0` et schéma JSON minimal.
- Données de démonstration explicitement signalées à l'écran et dans le snapshot.
- Tests locaux sans dépendance externe.
- Documentation d'architecture et de sécurité.
- Jeu de données DEMO enrichi : décisions, ordres vs exécutions, positions, portefeuilles Simulation/Paper, PnL, drawdown, budgets, quotas OpenAI/JEV/EODHD/Alpaca, diagnostics, alertes, commits et roadmap.
- GitHub Pages configuré depuis `gh-pages`; le dépôt public ne contient que du code et des données fictives.
- Consolidateur local `monitor/consolidate_snapshot.py` + CLI `scripts/consolidate_snapshot_v1.py` : validation de timestamps, statut `LIVE_READ_ONLY`/`STALE`/`UNAVAILABLE`, tagging par agent, absence de PnL consolidé trompeur et remplacement atomique.
- PWA : essaie `snapshot.json` local en premier, puis retombe sur la fixture DEMO ; aucun `snapshot.json` réel n'est committé.

### Fichiers/modules

- `dist/index.html`, `dist/styles.css`, `dist/app.js`, `dist/manifest.json` : PWA statique.
- `schema/snapshot.schema.json`, `schema/demo-snapshot.json` : contrat et fixture DEMO.
- `tests/test_snapshot.py` : contrôle du contrat, des données DEMO représentatives et des marqueurs UI.
- `tests/test_consolidate_snapshot.py`, `tests/fixtures/*_status_v1.json` : tests locaux de fraîcheur, tagging, `UNAVAILABLE` et atomicité.
- `docs/REAL_DATA_INGESTION.md` : procédure locale et interdiction de publication publique des données réelles.
- `docs/ARCHITECTURE.md` : flux Mini → Intel → cloud → PWA et garde-fous.

### Décisions d'architecture

- Dépôt Agent Monitor indépendant ; aucun changement aux dépôts ou runtimes Agent Stock/Crypto.
- Mini : production locale légère, remplacement atomique, intervalle initial maximal de 30 minutes, pas de serveur permanent.
- Intel : récupération, validation, consolidation et publication unique.
- Cloud cible : Workers + KV ou D1, à confirmer après vérification des quotas/conditions actuels ; aucune ressource créée.
- Auth cible : passkey/WebAuthn avec Face ID, validation serveur et récupération sécurisée ; pas de cryptographie maison.
- PWA : lecture seule, aucune action de trading, runtime, quota ou service partagé.

### Validé / rejeté / non prouvé

- Validé : principe d'un snapshot petit et remplaçable plutôt que du stockage Git fréquent ; fréquence de départ 30 minutes.
- Validé : les données du Mini doivent être réutilisées depuis les métriques déjà disponibles quand c'est possible.
- Rejeté : exposer directement le Mini ou l'iPhone aux runtimes ; Git public ou secret dans la PWA.
- Non prouvé : coût réel de l'extraction sur Mini, droits de lecture, continuité SSH, quotas Cloudflare Free à la date de mise en service, WebAuthn côté Worker, charge de l'agrégateur.

### Tests / recherche

- `python3 -B tests/test_snapshot.py` : PASS au moment de ce checkpoint.
- Recherche conversationnelle : architecture Cloudflare serverless + passkey Face ID approuvée, mais les quotas doivent être revérifiés officiellement avant création de ressource.
- Aucun test live, appel payant, ordre, déploiement, publication cloud, redémarrage ou changement de quota effectué.

### Incidents / limitations

- Le Work annoncé dans la conversation précédente n'a pas laissé de checkout local identifiable ; la V1 a donc été reprise dans `/Users/ssg/agent-monitor`.
- L'authentification et la synchronisation réelle ne sont pas encore implémentées.
- La PWA locale charge le fixture via un chemin relatif et nécessite un petit serveur HTTP local pour éviter les restrictions `file://`.

### Définitivement clos pour cette reprise

- Ne pas recommencer le choix Mini → Intel → cloud → PWA.
- Ne pas réévaluer Git comme stockage principal des snapshots fréquents.
- Ne pas mélanger le checkpoint Agent Monitor avec Agent Stock, Agent Crypto ou Agent Lab.
- Ne pas brancher d'exporteur réel avant preuve de charge faible et autorisation explicite.

### Backlog / roadmap

1. Mesurer en lecture seule le coût réel de génération du snapshot minimal sur Mini.
2. Vérifier les droits de lecture et les chemins sources Stock/Crypto sans modifier leurs runtimes.
3. Revérifier les quotas/conditions Cloudflare Free et choisir KV ou D1.
4. Implémenter WebAuthn/passkey côté Worker, récupération et sessions protégées.
5. Ajouter exporteurs périodiques séparés, avec timeout, atomicité, logs de fraîcheur et kill fail-closed.
6. Ajouter validation serveur et publication cloud uniquement après GO explicite.

### Jobs / runtimes

Aucun job Agent Monitor installé ou en cours. Aucun runtime Stock/Crypto touché. Les états des machines restent ceux des checkpoints propriétaires et ne sont pas recopiés comme faits live dans ce projet.

### Dépendances / données

V1 : navigateur moderne, Python standard library uniquement pour le test et un serveur HTTP local facultatif. V2 : WebAuthn, Worker/KV ou D1, accès en lecture aux snapshots Mini/Intel, sans secret dans le dépôt.

### Règles opérationnelles

- Read-only partout ; aucune commande d'ordre, de redémarrage, de cutover ou de changement de quota.
- Vérifier l'état live des machines avant toute action machine.
- Ne jamais publier un état sensible sans GO explicite.
- Afficher `STALE`, `OFFLINE`, `UNKNOWN` ou `UNAVAILABLE` plutôt qu'une valeur inventée.
- Aucun push sans demande explicite.

### Exact immediate next action

Après ce commit local, valider les premiers vrais fichiers Stock/Crypto hors dépôt public, puis préparer le publisher Intel privé vers Cloudflare. Ne pas créer de ressource cloud, ne pas installer de scheduler et ne pas publier de données réelles avant validation de WebAuthn, redaction, quotas, rétention et accès privé.

### Reprise utile

```sh
cd /Users/ssg/agent-monitor
python3 -B tests/test_snapshot.py
python3 -m http.server 4173 --directory dist
git status --short
```

Checkpoints propriétaires à consulter uniquement pour contrats/limites :

- `/Users/ssg/agent-stock/docs/AGENT_STOCK_PROJECT_STATE.md`
- `/Users/ssg/agent-lab/AGENT_LAB_STATE.md`

`AGENT_LAB_STATE.md` n'a pas été modifié : aucune information transversale d'infrastructure n'a changé.
