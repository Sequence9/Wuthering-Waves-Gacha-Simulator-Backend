from pydantic import BaseModel
from typing import List, Optional

class PullResult(BaseModel):
    item: str
    rarity: int
    is_featured: bool
    pity_at_pull: int

class GachaResponse(BaseModel):
    pulls: List[PullResult]
    current_pity: int
    has_guarantee: bool

class BannerInfo(BaseModel):
    banner_id: str
    name: str
    featured_unit: str
    rate_up_4stars: List[str]