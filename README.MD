# PROJECT SEVS - Industrial Intellignece Dashboard
A Streamlit-based operations center for flour mill telemetry. Ingests historian data, applies Z-score anomaly detection, and calculates operational KPIs with cumulative delta math.

                    #-------------Features:----------------
        -Data Pipeline: Pandas-based ingestion with strict error handling.
        -Cumulative Logic: last - first delta math for totalizers (Feed Weight, Bag Count).
        -Intelligence: Z-score statistical engine for temperature deviations.
        -Aggregator: On-the-fly Daily/Weekly/Monthly resampling with min/max/mean metrics.
        -UI: Streamlit with custom CSS and HTML KPI cards.

**CREATE VIRTUAL ENVIRONMENT**
python -m venv .PROJ_SEVS

**to activate the enivronment**
.\.PROJ_SEVS\Scripts\activate
**to deactivated the environment**
.\.PROJ_SEVS\Scripts\deactivate

**Install all the requirements**
pip install -r requiremnts.txt

**To run the app**
streamlit run ui/app.py

**to clear the terminal cmds**
clear

**to traverse from file to file**
cd "file name"      #to enter the file
cd ..               # to exit the file

## Design Note

The architecture leverages a decoupled data pipeline using Streamlit for rapid presentation and Pandas/NumPy for vectorized backend operations.
This separation guarantees mathematical integrity during dynamic time-series resampling.
Streamlit was chosen for fast data application deployment, inspiration taken form industrial HERCULES interface, reducing load. 
Plotly was integrated for its high-performance rendering of dense telemetry trends. 

The foundational Z-score anomaly logic would be used to train LSTM or ARIMA models for proactive predictive maintenance forecasting.

### Notes on Data Handling
To ensure industrial accuracy, cumulative totalizers (`feed_weight_kg`, `bag_count`) are explicitly routed through a custom `last - first` delta function during aggregation to prevent totalizer bloat.
The system derives plant state dynamically (`is_running = throughput > 0`), ensuring that the anomaly detection engine mathematically ignores idle Sunday maintenance windows and planned stoppages to eliminate false positive alerts.


**To update the gih hub repoaitories follow certain steps**
check "git status"
 git add . 
 git commit -m "Update : "changes""
 git push 
It will then only reflect the changes in the repository.

