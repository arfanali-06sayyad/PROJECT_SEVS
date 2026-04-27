import pandas as pd
import logging
from src.config import PlantConfig


# -------- AGGREGATION ENGINE --------

class HistorianAggregator:
    def __init__(self, config: PlantConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.delta_cols = [
            self.config.tag_feed_weight, 
            self.config.tag_bag_count, 
            'production_total_kg'
        ]
        
        self.signal_cols = [
            self.config.tag_motor_current, 
            self.config.tag_throughput,
            self.config.tag_grinder_temp, 
            self.config.tag_moisture,
            'extraction_yield_pct', 
            'energy_intensity_proxy'
        ]

    @staticmethod
    def _calc_delta(series: pd.Series) -> float:
        if len(series) == 0:
            return 0.0
        elif len(series) == 1:
            return 0.0
        else:
            return float(series.iloc[-1] - series.iloc[0])

    def aggregate(self, df: pd.DataFrame, frequency: str) -> pd.DataFrame:
        self.logger.info(f"Aggregating data at frequency: {frequency}")
        
        if df is None:
            return pd.DataFrame()
        elif df.empty:
            return pd.DataFrame()
        else:
            temp_df = df.set_index('timestamp')
            agg_dict = {}
            
            for col in self.delta_cols:
                if col in temp_df.columns:
                    agg_dict[col] = self._calc_delta
                    
            for col in self.signal_cols:
                if col in temp_df.columns:
                    agg_dict[col] = ['min', 'max', 'mean']
                    
            if 'is_running' in temp_df.columns:
                agg_dict['is_running'] = 'sum'
                
            agg_df = temp_df.resample(frequency).agg(agg_dict)
            
            if isinstance(agg_df.columns, pd.MultiIndex):
                new_cols = []
                for col in agg_df.columns:
                    if col[1] == '':
                        new_cols.append(col[0])
                    elif col[1] == '_calc_delta':
                        new_cols.append(f"{col[0]}_total")
                    else:
                        new_cols.append(f"{col[0]}_{col[1]}")
                agg_df.columns = new_cols
                
            agg_df = agg_df.fillna(0.0)
            return agg_df.reset_index()