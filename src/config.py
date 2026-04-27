from dataclasses import dataclass, field
from typing import List


# -------- CONFIG: PLANT OPERATIONS --------

@dataclass
class PlantConfig:
    operating_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5])
    start_hour: int = 6
    end_hour: int = 22
    
    tag_feed_weight: str = "feed_weight_kg"
    tag_motor_current: str = "motor_current_a"
    tag_throughput: str = "throughput_kgph"
    tag_grinder_temp: str = "grinder_temp_c"
    tag_moisture: str = "moisture_pct"
    tag_bag_count: str = "bag_count"
    
    bag_weight_kg: float = 50.0


# -------- CONFIG: INTELLIGENCE --------

@dataclass
class AdvancedConfig:
    temp_high_warning: float = 40.0
    moisture_high_warning: float = 14.0
    moisture_low_warning: float = 11.5
    anomaly_zscore_threshold: float = 3.0