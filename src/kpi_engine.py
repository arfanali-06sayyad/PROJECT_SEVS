import pandas as pd
import numpy as np
import logging
from src.config import PlantConfig

# -------- KPI ENGINE --------

class KPIEngine:
    def __init__(self, config: PlantConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Processing derived KPIs...")
        
        if df is None:
            self.logger.error("Input DataFrame is None.")
            return pd.DataFrame()
        elif df.empty:
            self.logger.error("Input DataFrame is empty.")
            return pd.DataFrame()
        else:
            enriched_df = df.copy()
            
            enriched_df['is_running'] = enriched_df[self.config.tag_throughput] > 0
            enriched_df['production_total_kg'] = enriched_df[self.config.tag_bag_count] * self.config.bag_weight_kg
            
            enriched_df['extraction_yield_pct'] = np.where(
                enriched_df[self.config.tag_feed_weight] > 0,
                (enriched_df['production_total_kg'] / enriched_df[self.config.tag_feed_weight]) * 100,
                0.0
            )
            
            enriched_df['energy_intensity_proxy'] = np.where(
                enriched_df['is_running'],
                enriched_df[self.config.tag_motor_current] / enriched_df[self.config.tag_throughput],
                0.0
            )
            
            self.logger.info("KPI enrichment complete.")
            return enriched_df