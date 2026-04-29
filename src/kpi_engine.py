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
            
            # Ensure timestamp is datetime for schedule logic
            if not pd.api.types.is_datetime64_any_dtype(enriched_df['timestamp']):
                enriched_df['timestamp'] = pd.to_datetime(enriched_df['timestamp'])
            
            hourly_feed = enriched_df[self.config.tag_feed_weight].diff().fillna(0)
            hourly_bags = enriched_df[self.config.tag_bag_count].diff().fillna(0)
            hourly_flour = hourly_bags * self.config.bag_weight_kg

            hours = enriched_df['timestamp'].dt.hour
            days = enriched_df['timestamp'].dt.dayofweek # 6 == Sunday
            
            enriched_df['machine_state'] = 'UNKNOWN'
            
            maintenance_mask = (days == 6)
            offshift_mask = (~maintenance_mask) & ((hours < self.config.start_hour) | (hours >= self.config.end_hour))
            running_mask = (~maintenance_mask) & (~offshift_mask) & (enriched_df[self.config.tag_throughput] > 0)
            stoppage_mask = (~maintenance_mask) & (~offshift_mask) & (enriched_df[self.config.tag_throughput] == 0)
 
            enriched_df.loc[maintenance_mask, 'machine_state'] = 'MAINTENANCE'
            enriched_df.loc[offshift_mask, 'machine_state'] = 'OFF-SHIFT'
            enriched_df.loc[running_mask, 'machine_state'] = 'RUNNING'
            enriched_df.loc[stoppage_mask, 'machine_state'] = 'PLANNED STOPPAGE'
            
            enriched_df['is_running'] = running_mask

            rolling_feed = hourly_feed.rolling(window=4, min_periods=1).sum()
            rolling_flour = hourly_flour.rolling(window=4, min_periods=1).sum()
            
            enriched_df['extraction_yield_pct'] = np.where(
                rolling_feed > 0,
                (rolling_flour / rolling_feed) * 100,
                0.0
            )
            enriched_df['extraction_yield_pct'] = np.clip(enriched_df['extraction_yield_pct'], 0.0, 99.9)
            
            enriched_df['production_total_kg'] = enriched_df[self.config.tag_bag_count] * self.config.bag_weight_kg
            
            enriched_df['energy_intensity_proxy'] = np.where(
                enriched_df['is_running'],
                enriched_df[self.config.tag_motor_current] / enriched_df[self.config.tag_throughput].replace(0, np.nan),
                0.0
            )
            enriched_df['energy_intensity_proxy'] = enriched_df['energy_intensity_proxy'].fillna(0.0)
            
            self.logger.info("KPI enrichment complete.")
            return enriched_df