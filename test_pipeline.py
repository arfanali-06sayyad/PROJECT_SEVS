from src.config import PlantConfig
from src.data_loader import DataLoader
from src.kpi_engine import KPIEngine
from src.aggregator import HistorianAggregator

print("1. Loading Config...")
config = PlantConfig()

print("2. Ingesting Historian Data...")
loader = DataLoader("data/mini_hercules_mock_data_hourly.csv")
df = loader.load_data()

if df is None or df.empty:
    print("\nFAILED TO LOAD DATA. Check file path.")
else:
    print("\n3. Running KPI Engine (Calculating Yield & Energy)...")
    engine = KPIEngine(config)
    enriched_df = engine.process(df)
    print("\n--- Enriched Data Sample ---")
    print(enriched_df[['timestamp', 'throughput_kgph', 'production_total_kg', 'extraction_yield_pct']].head())

    print("\n4. Running Aggregator (Daily Buckets)...")
    aggregator = HistorianAggregator(config)
    daily_df = aggregator.aggregate(enriched_df, 'D')
    print("\n--- Daily Aggregation Sample ---")
    print(daily_df[['timestamp', 'bag_count', 'is_running']].head())
    
    print("\nPIPELINE TEST SUCCESSFUL")