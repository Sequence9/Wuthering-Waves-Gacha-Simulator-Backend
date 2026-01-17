from fastapi import FastAPI, HTTPException
from .database import RedisManager
from .gacha_logic import perform_pull
from .models import GachaResponse
import json
import random

app = FastAPI(title="WuWa Convene Simulator 2026")
db = RedisManager()

# Standard Pool (Characters + Weapons)
STANDARD_4STAR_POOL = [
    "Aalto", "Baizhi", "Chixia", "Danjin", "Mortefi", "Sanhua", "Taoqi", "Yangyang", "Yuanwu",
    "Dauntless Evernight", "Helios Cleaver", "Lunar Cutter", "Novaburst", "Overture", "Undying Flame"
]

with open("data/banners.json", "r") as f:
    BANNERS = json.load(f)

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

@app.post("/pull/{banner_id}", response_model=GachaResponse)
async def pull(banner_id: str, user_id: str = "default_rover"):
    if banner_id not in BANNERS:
        raise HTTPException(status_code=404, detail="Banner not found")
    
    # Get current state (pity and guarantee)
    pity_5 = db.get_pity(user_id, banner_id)
    pity_4 = db.get_pity_4(user_id, banner_id)
    is_guaranteed = db.get_guarantee(user_id, banner_id)
    
    result = perform_pull(pity_5, pity_4, is_guaranteed)
    banner = BANNERS[banner_id]
    item_name = ""
    item_is_featured = False

    # 50/50 mechanic
    if result["rarity"] == 5:
        if result["won_5050"]:
            item_name = banner["featured_5star"]
            item_is_featured = True
            db.set_guarantee(user_id, banner_id, False)
        else:
            item_name = random.choice(banner["standard_5stars"])
            item_is_featured = False
            db.set_guarantee(user_id, banner_id, True)
        
        db.set_pity(user_id, banner_id, 0) # Reset 5-star pity
        db.set_pity_4(user_id, banner_id, 0) # WuWa resets 4-star pity on 5-star hits

    # 4-Star logic
    elif result["rarity"] == 4:
        if random.random() <= 0.5:
            item_name = random.choice(banner["rate_up_4stars"])
            item_is_featured = True
        else:
            item_name = random.choice(STANDARD_4STAR_POOL)
            item_is_featured = False
        
        db.set_pity_4(user_id, banner_id, 0)
        db.set_pity(user_id, banner_id, pity_5 + 1)

    # 3-Star (trash)
    else:
        item_name = "3-Star Weapon"
        db.set_pity(user_id, banner_id, pity_5 + 1)
        db.set_pity_4(user_id, banner_id, pity_4 + 1)

    return {
        "pulls": [{
            "item": item_name,
            "rarity": result["rarity"],
            "is_featured": item_is_featured,
            "pity_at_pull": pity_5 + 1
        }],
        "current_pity": db.get_pity(user_id, banner_id),
        "has_guarantee": db.get_guarantee(user_id, banner_id)
    }
