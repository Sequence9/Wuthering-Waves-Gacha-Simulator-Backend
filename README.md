# Wuthering Waves Gacha Simulator Backend

A small FastAPI backend that simulates Wuthering Waves style convene pulls.
It keeps pity and the 50/50 guarantee in Redis.

This is a project for learning and tinkering.

## What it does

- One endpoint to do a pull on a banner
- Banner data is loaded from `data/banners.json`
- Tracks per user and per banner:
  - 5 star pity
  - 4 star pity (10 pull guarantee)
  - 5 star featured guarantee (after losing a 50/50)
- Stores state in Redis

## Tech

- Python
- FastAPI
- Redis
- Docker + Docker Compose

## Folder / file map

- `app/main.py` - FastAPI app and endpoints
- `app/gacha_logic.py` - rarity roll logic (rates, soft pity)
- `app/database.py` - Redis helper (pity + guarantee keys)
- `app/models.py` - Pydantic response models
- `data/banners.json` - banner definitions
- `docker-compose.yml` - runs the API and Redis
- `docker/Dockerfile` - API container image

## Run it (Docker Compose)

From the repo root:

```bash
docker compose up --build
```

API:
- http://localhost:8000
- Docs: http://localhost:8000/docs

Health check:

```bash
curl http://localhost:8000/health
```

## API

### POST /pull/{banner_id}

Does one pull on the banner.

- `banner_id` is a key in `data/banners.json` (example: `lynae_banner`)
- `user_id` is optional (query param). Default is `default_rover`

Example:

```bash
curl -X POST "http://localhost:8000/pull/lynae_banner?user_id=default_rover"
```

Response looks like:

```json
{
  "pulls": [
    {
      "item": "Chixia",
      "rarity": 4,
      "is_featured": true,
      "pity_at_pull": 12
    }
  ],
  "current_pity": 13,
  "has_guarantee": false
}
```

Important note:
- Pity and guarantee are stored per `(user_id, banner_id)`.
  That means pity does not automatically carry between different banner IDs.

## How the gacha works

### Rarity rates

5 star:
- Base rate is 0.8% (`0.008`).
- Soft pity starts at pull 70.
- After that, the 5 star chance goes up fast so it hits 100% by pull 80.

4 star:
- Base rate is 6% (`0.06`).
- Guaranteed on the 10th pull since your last 4 star or higher.

3 star:
- If you do not hit 5 star or 4 star, you get a simple `"3-Star Weapon"` result.

### Featured rules

5 star featured (50/50):
- If you are guaranteed, your next 5 star is the featured unit.
- Otherwise, on a 5 star:
  - 50% featured unit
  - 50% random from `standard_5stars`
- If you lose the 50/50, the next 5 star becomes guaranteed.

4 star featured:
- On a 4 star:
  - 50% from `rate_up_4stars` (featured)
  - 50% from a standard 4 star pool (hardcoded in `app/main.py`)

### Pity updates

- If you hit a 5 star:
  - 5 star pity resets to 0
  - 4 star pity resets to 0
- If you hit a 4 star:
  - 4 star pity resets to 0
  - 5 star pity goes up by 1
- If you hit a 3 star:
  - both pity counters go up by 1

## Banner config

Banners live in `data/banners.json`.

Example:

```json
{
  "lynae_banner": {
    "name": "Requiem Without End",
    "featured_5star": "Lynae",
    "standard_5stars": ["Verina", "Encore", "Calcharo", "Jianxin", "Lingyang"],
    "rate_up_4stars": ["Chixia", "Danjin", "Mortefi"],
    "rates": { "5star": 0.008, "4star": 0.06 }
  }
}
```

Note:
- The `rates` field exists in the JSON, but the current code uses hardcoded rates in `app/gacha_logic.py`.

## Reset Redis

If you want to wipe all saved pity/guarantee state:

```bash
docker compose exec redis redis-cli FLUSHALL
```

## Disclaimer

Fan made simulator for learning.
Not affiliated with Kuro Games or Wuthering Waves.
