import pandas as pd
import numpy as np
import logging
from typing import List
from dataclasses import dataclass
from src.config import AdvancedConfig


# -------- INTELLIGENCE ENGINE --------

@dataclass
class Alert:
    timestamp: pd.Timestamp
    category: str
    message: str
    severity: str

class ProcessIntelligence:
    def __init__(self, config: AdvancedConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info("Running statistical anomaly detection on moisture...")
        
        df_intel = df.copy()
        target_col = 'moisture_pct' 
        
        rolling_mean = df_intel[target_col].rolling(window=24, min_periods=5).mean().shift(1)
        rolling_std = df_intel[target_col].rolling(window=24, min_periods=5).std().shift(1)
        
        df_intel['moisture_zscore'] = 0.0
        valid_std_mask = rolling_std > 0
        
        df_intel.loc[valid_std_mask, 'moisture_zscore'] = (
            (df_intel.loc[valid_std_mask, target_col] - rolling_mean[valid_std_mask]) 
            / rolling_std[valid_std_mask]
        )
            
        df_intel['is_anomaly'] = False
        
        is_startup = (df_intel['timestamp'].dt.hour == 6)
        
        anomaly_mask = (
            (df_intel['is_running'] == True) & 
            (~is_startup) & 
            (df_intel['moisture_zscore'].abs() > self.config.anomaly_zscore_threshold)
        )
        
        df_intel.loc[anomaly_mask, 'is_anomaly'] = True
        
        return df_intel

    def generate_alerts(self, df: pd.DataFrame) -> List[Alert]:
        alerts = []
        anomalies = df[df['is_anomaly'] == True]
        
        for _, row in anomalies.iterrows():
            alerts.append(Alert(
                timestamp=row['timestamp'],
                category='PROCESS DEVIATION',
                message=f"Moisture Excursion: {row['moisture_pct']:.2f}% (Z: {row['moisture_zscore']:.2f})",
                severity='HIGH'
            ))
            
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)