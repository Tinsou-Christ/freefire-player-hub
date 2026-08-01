# Free Fire Info API

API HTTP (Flask) qui renvoie toutes les informations d'un compte Free Fire à partir de son
UID et de son serveur — exactement les données de la commande `ffinfo`.

Le code de l'API vit dans `ffapi/`, le `Dockerfile` est à la racine (comme seamless-bot).

## Endpoints

| Méthode | Route | Description |
| --- | --- | --- |
| GET | `/` | Site web de recherche par UID |
| GET | `/health` | Statut du service |
| GET | `/api/servers` | Liste des serveurs supportés |
| GET | `/api/ffinfo?uid=<uid>&server=<SERVER>` | JSON complet (`player`, `summary`, `raw`) |
| GET | `/api/ffinfo?q=<uid> \| <SERVER>` | Même chose, au format de la commande |
| GET | `/api/ffinfo/text?uid=<uid>&server=<SERVER>` | Texte brut façon `ffinfo` |
| GET | `/api/profile-image?uid=<uid>` | Image de profil du joueur |

Serveurs : `SG BD RU ID TW US VN TH ME PK CIS BR IND`.

Exemple :

```bash
curl "https://<votre-app>.onrender.com/api/ffinfo?uid=1234567890&server=IND"
```

## Utilisation depuis la commande `ffinfo`

Remplacez l'URL upstream par la vôtre :

```ts
const { data } = await axios.get(
  `https://<votre-app>.onrender.com/api/ffinfo?uid=${uid}&server=${serverKey}`,
);
await output.reply(data.summary);
```

## Lancer en local

```bash
pip install -r requirements.txt
python ffapi/app.py     # http://localhost:8000
```

## Docker

```bash
docker build -t ffinfo-api .
docker run -p 8000:8000 ffinfo-api
```

## Déploiement Render.com

1. Poussez le dépôt sur GitHub.
2. Render → **New +** → **Web Service** → sélectionnez le dépôt.
3. Runtime **Docker** (le `Dockerfile` est détecté à la racine), health check `/health`.
4. Deploy — aucune variable d'environnement requise (`PORT` est fourni par Render).

`render.yaml` est inclus pour un déploiement en Blueprint.
