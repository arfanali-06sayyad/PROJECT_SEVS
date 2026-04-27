import pandas as pd
import logging
from pathlib import Path
from typing import Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# -------- DATA INGESTION --------

class DataLoader:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def load_data(self) -> Optional[pd.DataFrame]:
        self.logger.info(f"Attempting to load historian data from {self.filepath}")
        
        if not self.filepath.exists():
            self.logger.error("Data file not found. Ensure the CSV is in the data/ folder.")
            return None
        elif not self.filepath.is_file():
            self.logger.error("Path exists but is not a valid file.")
            return None
        else:
            df = pd.read_csv(self.filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').reset_index(drop=True)
            
            self.logger.info(f"Successfully loaded {len(df)} records.")
            return df