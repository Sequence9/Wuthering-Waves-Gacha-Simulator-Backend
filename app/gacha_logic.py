import random

def calculate_rate(current_pity: int) -> float:
    base_rate = 0.008  # 0.8%
    if current_pity < 65:
        return base_rate
    
    # Soft pity: increasing 6% every pull after 64
    extra_chance = (current_pity - 64) * 0.062
    return min(1.0, base_rate + extra_chance)

def perform_pull(pity_count: int, four_star_pity: int, is_guaranteed: bool, is_weapon_banner: bool = False):
    rate = calculate_rate(pity_count + 1)
    roll = random.random()
    
    if roll <= rate:
        # 5-star hit
        if is_weapon_banner:
            won_5050 = True # Weapon banners in WuWa have no 50/50
        else:
            won_5050 = random.random() <= 0.5 or is_guaranteed
        return {"rarity": 5, "won_5050": won_5050, "reset_pity": True}
    
    # Check 4-star pity (Guaranteed every 10)
    if (four_star_pity + 1) >= 10:
        return {"rarity": 4, "won_5050": False, "reset_pity": False}
        
    # Standard 3-star roll
    # Real base rate for 4-star is 6.0%
    if random.random() <= 0.06:
        return {"rarity": 4, "won_5050": False, "reset_pity": False}

    return {"rarity": 3, "won_5050": False, "reset_pity": False}