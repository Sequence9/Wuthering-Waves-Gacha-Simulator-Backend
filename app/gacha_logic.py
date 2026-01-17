import random

def calculate_rate(current_pity: int) -> float:
    # WuWa Accuracy: base rate is 0.8%
    # Soft pity starts around 66-70
    base_rate = 0.008 
    if current_pity < 70:
        return base_rate
    
    # Increases so it hits 100% by pull 80
    extra_chance = (current_pity - 69) * 0.1
    return min(1.0, base_rate + extra_chance)

def perform_pull(pity_5: int, pity_4: int, is_guaranteed: bool):
    rate_5 = calculate_rate(pity_5 + 1)
    roll = random.random()
    
    # 5-Star check
    if roll <= rate_5:
        won_5050 = random.random() <= 0.5 or is_guaranteed
        return {
            "rarity": 5, 
            "won_5050": won_5050, 
            "reset_5": True, 
            "reset_4": True  # Getting a 5-star resets 4-star pity too
        }
    
    # 2. 4-Star guaranteed at pull 10 or ~6% random chance
    rate_4 = 0.06
    if (pity_4 + 1) >= 10 or roll <= (rate_5 + rate_4):
        return {
            "rarity": 4, 
            "won_5050": False, 
            "reset_5": False, 
            "reset_4": True
        }
    
    # 3. 3-Star (Trash)
    return {
        "rarity": 3, 
        "won_5050": False, 
        "reset_5": False, 
        "reset_4": False
    }
