# Quantitative Mutual Fund Analytics & Forecasting Pipeline

## What is it 
An automated, end-to-end data pipeline and quantitative screening engine for the Indian Mutual Fund market. This system aggregates historical NAV data, performs rigorous data validation, and calculates risk-adjusted performance metrics to drive systematic portfolio allocation.

## Architecture & Infrastructure 
The project is structured for reliability and automated reporting, heavily emphasizing data integrity before any statistical modeling occurs.

**1. Data Ingestion & Pipeline:** Multi-threaded historical data extraction from the AMFI API, coupled with a resilient daily update mechanism (exponential backoff, retry logic).

**2.Data Validation:** Strict schema enforcement using Pandera. Erroneous data (e.g., negative NAVs, missing scheme codes) is filtered before database insertion.

**3.Storage Layer:** MySQL database managed via SQLAlchemy ORM, utilizing connection pooling for high-throughput I/O operations.

**4.Analytical Engine:** Calculates annualized volatility, CAGR across multiple horizons, and the Sharpe ratio  (Sharpe ratio $$  \left( Sharpe = \frac{R_p - R_f}{\sigma_p} \right)  $$) for 5,000+ open-ended funds.
<img width="787" height="742" alt="image" src="https://github.com/user-attachments/assets/c0a9cd36-4725-4cd5-bbfe-8d053e4f6fd1" />

**5.Automated Reporting:** A CLI-driven orchestrator (run_local_pipeline.py) that executes the analytical pipeline and generates a stylized, client-ready PDF report via xhtml2pdf.
<img width="774" height="303" alt="image" src="https://github.com/user-attachments/assets/71b0d3c6-bd51-409a-a10e-593224cf436b" />

## Quantitative Backtesting Performance
The ProfessionalMFEngine module implements a systematic backtester evaluating a combined Trend-Following (Fast/Slow EMA crossover) and Momentum (RSI + Prophet directional prediction) strategy.

Synthetic bull market simulation assuming 0.08% average daily return drift over 1200 trading days .

### Metrics details:

|Metric   | Strategy Performance|
|---|---|
|Directional Accuracy   |  52.3% |
|Total Strategy Return   | 185.4%  | 
|Benchmark Return        | 162.1%  |
|Max Drawdown            |  -12.4% |
Annualized Sharpe Ratio |    1.85  |


## Forecasting Methodology
Forward-looking projections are handled by a dual-model ensemble approach to balance trend responsiveness with seasonal stability:

1. Facebook Prophet: Handles daily/yearly seasonality and automatic changepoint detection for trend shifts.

2. Holt-Winters (Exponential Smoothing): Captures additive trend and seasonal components over a 365-day period.

The final projected NAV is a weighted ensemble of both models, heavily reducing the variance of single-model forecasts.

<img width="748" height="410" alt="image" src="https://github.com/user-attachments/assets/effdda41-72db-4d11-8153-5bce3e35a240" />

## Reproducibility & Setup
#### Prerequisites
* Python 3.8+

* Running MySQL Server instance

#### Installation

1. Clone the repo and install dependencies:

   ```Bash
   git clone https://github.com/your-username/mf-quant-pipeline.git
   cd mf-quant-pipeline
   pip install -r requirements.txt
   ```

2. Configure the environment. Create a .env file in the root directory:

   ```.env
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=mutual_funds
   ```

 #### Execution

 **Option 1: Full System Initialization (First Run)**
 Builds the historical database from scratch, runs the statistical models, and generates the PDF report. 
 
 ``` Python
 python run_local_pipeline.py --full
 ```

 **Option 2: Daily Updates & Report Generation**
 Fetches the latest T+1 NAV data, updates the MySQL database, and regenerates the analytical reports.

 ``` Python
 python run_local_pipeline.py
 ```

## Portfolio Construction Logic

The recommendation algorithm utilizes agglomerative hierarchical clustering (Ward's method) and a daily return correlation matrix. The pipeline automatically constructs a diversified portfolio by selecting an "Anchor" fund based on the highest risk-adjusted suitability score, and iteratively appending funds that maintain an internal correlation coefficient of < 0.85.


*Disclaimer: This is not financial advice. Past performance ≠ future results. For educational/research use only.*
