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
        self.logger.info("Running statistical anomaly detection...")
        
        running_mask = df['is_running'] == True
        temp_mean = df.loc[running_mask, 'grinder_temp_c'].mean()
        temp_std = df.loc[running_mask, 'grinder_temp_c'].std()
        
        df['temp_zscore'] = 0.0
        
        if temp_std > 0:
            df.loc[running_mask, 'temp_zscore'] = (df.loc[running_mask, 'grinder_temp_c'] - temp_mean) / temp_std
            
        df['is_anomaly'] = False
        df.loc[running_mask & (df['temp_zscore'].abs() > self.config.anomaly_zscore_threshold), 'is_anomaly'] = True
        
        return df

    def generate_alerts(self, df: pd.DataFrame) -> List[Alert]:
        alerts = []
        anomalies = df[df['is_anomaly'] == True]
        
        for _, row in anomalies.iterrows():
            alerts.append(Alert(
                timestamp=row['timestamp'],
                category='ANOMALY',
                message=f"Temp Anomaly: Grinder {row['grinder_temp_c']:.1f}°C (Z: {row['temp_zscore']:.2f})",
                severity='HIGH'
            ))
            
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)