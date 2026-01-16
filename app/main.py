from fastapi import FastAPI, HTTPException
from .database import RedisManager
from .gacha_logic import perform_pull
from .models import GachaResponse, PullResult
import json
import random

app = FastAPI(title="WuWa Convene Simulator 2026")
db = RedisManager()

# Standard 4-Star character pool
STANDARD_4STAR_CHARS = ["Aalto", "Baizhi", "Chixia", "Danjin", "Mortefi", "Sanhua", "Taoqi", "Yangyang", "Yuanwu"]
# Simplified 4-Star Weapon Pool (grouped by type)
STANDARD_4STAR_WEAPONS = ["Dauntless Evernight", "Helios Cleaver", "Lunar Cutter", "Novaburst", "Overture", "Undying Flame"]

# Load banner data
with open("data/banners.json", "r") as f:
    BANNERS = json.load(f)

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.post("/pull/{banner_id}", response_model=GachaResponse)
async def pull(banner_id: str, user_id: str = "default_rover"):
    if banner_id not in BANNERS:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    # Retrieve current state from Redis
    pity_5 = db.get_pity(user_id, banner_id)
    pity_4 = db.get_pity_4(user_id, banner_id)  # self-note: add this method to database.py
    is_guaranteed = db.get_guarantee(user_id, banner_id)
    
    # Execute logic
    result = perform_pull(pity_5, pity_4, is_guaranteed)
    banner = BANNERS[banner_id]
    item_name = ""
    is_featured = False

    # Determine item name based on rarity
    if result["rarity"] == 5:
        is_featured = result.get("won_5050", False)
        item_name = banner["featured_5star"] if is_featured else random.choice(banner["standard_5stars"])
    
    elif result["rarity"] == 4:
        # 50% chance for a Rate-Up character, 50% for the Standard Pool
        if random.random() <= 0.5:
            item_name = random.choice(banner["rate_up_4stars"])
            is_featured = True
        else:
            # Randomly pick between a standard character or weapon
            pool = STANDARD_4STAR_CHARS + STANDARD_4STAR_WEAPONS
            item_name = random.choice(pool)
            is_featured = False
    
    else:
        item_name = "3-Star Weapon"

    # Update Database State
    # Handle 5-star resets
    if result["reset_5"]:
        db.set_pity(user_id, banner_id, 0)
        db.set_guarantee(user_id, banner_id, not is_featured if result["rarity"] == 5 else is_guaranteed)
    else:
        db.set_pity(user_id, banner_id, pity_5 + 1)

    # Handle 4-star resets
    if result["reset_4"] or result["reset_5"]:
        db.set_pity_4(user_id, banner_id, 0)
    else:
        db.set_pity_4(user_id, banner_id, pity_4 + 1)
        
    return {
        "pulls": [{
            "item": item_name,
            "rarity": result["rarity"],
            "is_featured": is_featured,
            "pity_at_pull": pity_5 + 1
        }],
        "current_pity": 0 if result["reset_5"] else pity_5 + 1,
        "has_guarantee": db.get_guarantee(user_id, banner_id)
    }