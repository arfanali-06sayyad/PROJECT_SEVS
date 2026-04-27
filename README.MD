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

