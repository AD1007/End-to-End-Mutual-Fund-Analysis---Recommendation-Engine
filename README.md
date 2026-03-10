# Quantitative Mutual Fund Analytics & Forecasting Pipeline

## What is it 
An automated, end-to-end data pipeline and quantitative screening engine for the Indian Mutual Fund market. This system aggregates historical NAV data, performs rigorous data validation, and calculates risk-adjusted performance metrics to drive systematic portfolio allocation.

## Architecture & Infrastructure 
The project is structured for reliability and automated reporting, heavily emphasizing data integrity before any statistical modeling occurs.

**1. Data Ingestion & Pipeline:** Multi-threaded historical data extraction from the AMFI API, coupled with a resilient daily update mechanism (exponential backoff, retry logic).

**2.Data Validation:** Strict schema enforcement using Pandera. Erroneous data (e.g., negative NAVs, missing scheme codes) is filtered before database insertion.

**3.Storage Layer:** MySQL database managed via SQLAlchemy ORM, utilizing connection pooling for high-throughput I/O operations.

**4.Analytical Engine:** Calculates annualized volatility, CAGR across multiple horizons, and the Sharpe ratio  ($Sharpe = \frac{R_p - R_f}{\sigma_p}$) for 5,000+ open-ended funds.

**5.Automated Reporting:** A CLI-driven orchestrator (run_local_pipeline.py) that executes the analytical pipeline and generates a stylized, client-ready PDF report via xhtml2pdf.

## Quantitative Backtesting Performance
The ProfessionalMFEngine module implements a systematic backtester evaluating a combined Trend-Following (Fast/Slow EMA crossover) and Momentum (RSI + Prophet directional prediction) strategy.

Simulation on Bull Market parameters (0.08% daily drift, 1200 periods):


|Metric   | Strategy Performance|
|---|---|
|Directional Accuracy   |  52.3% |
|Total Strategy Return   | 185.4%  | 
|Benchmark Return        | 162.1%  |
|Max Drawdown            |  -12.4% |
Annualized Sharpe Ratio |    1.85  |


## 🛠️ Technology Stack
Backend & Data Processing: Python

Data Manipulation & Analysis: Pandas, NumPy

Database: MySQL

Database Connector & ORM: SQLAlchemy, PyMySQL

Data Validation: Pandera

Web Scraping & API Interaction: Requests

Time-Series Forecasting: Prophet (by Facebook), Statsmodels

Data Visualization: Matplotlib, Seaborn

Configuration Management: Pydantic, python-dotenv

Development Environment: Jupyter Notebook

## ⚙️ How It Works: The Core Logic
The project is divided into two main parts: the Data Pipeline that builds the database and the Analysis Engine that uses the data.

Part 1: The Data Pipeline (Building the Foundation)
build_full_history_optimized.py:

This is the master script to build the database from scratch.

It first fetches a list of all 50,000+ scheme codes from the API.

Using multi-threading (ThreadPoolExecutor), it downloads the full historical NAV data for every single fund in parallel, making the process significantly faster.

It includes a checkpoint system: it saves progress periodically, so if the script fails, it can be resumed without losing downloaded data.

Once all data is downloaded, it is cleaned, validated, and loaded into the nav_data table in the MySQL database.

update_daily.py:

This script is meant to be run daily.

It scrapes the latest NAV data from the official AMFI website.

It intelligently appends this new data to the existing database, updating records for the latest day. This ensures the database is always current.

Part 2: The Analysis & Recommendation Engine (Analysis_Optimized.ipynb)
Memory-Safe Data Loading: It first connects to the database and runs a query to get a list of all fund names. It uses a keyword filter to identify unsuitable funds (FMPs, ETFs, etc.) and then loads the full data for only the suitable funds. This is a critical optimization that prevents memory errors.

Metric Calculation: It calculates daily returns and then computes the full suite of metrics: historical CAGR, fund age, volatility, and Sharpe Ratio.

Recommendation Scoring: You set your INVESTMENT_HORIZON_YEARS and RISK_TOLERANCE. The engine then calculates a "Suitability Score" for each fund based on a weighted average of its risk-adjusted return (Sharpe Ratio) and expected performance.

Diversification Analysis: For the top-recommended funds, it creates a pivot table of their daily returns and calculates the correlation matrix. This matrix is then used to generate the dendrogram and heatmap.

Final Portfolio Construction: It builds a sample portfolio by first picking the highest-scoring fund, then iteratively adding other high-scoring funds that have a low correlation (<0.85) to the ones already selected.

## 🔧 How to Use This Project
Prerequisites:

Python 3.8+

A running MySQL server instance.

Setup:

Clone the repository: git clone [https://github.com/your-username/SIP-Analyser.git](https://github.com/AD1007/End-to-End-Mutual-Fund-Analysis---Recommendation-Engine)

Install the required libraries: pip install -r requirements.txt

Create a .env file in the root directory and add your database credentials:

DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=mutual_funds

Create the mutual_funds database in your MySQL server.

Run the Pipeline:

Step 1 (One-time only): Build the historical database. This will take a long time.

python build_full_history_optimized.py

Step 2 (Run daily/weekly): Keep the database updated with the latest data.

python update_daily.py

Run the Analysis:

Open and run the Analysis_Optimized.ipynb and forecasting_final.ipynb notebooks in Jupyter to see the results and get recommendations.

## ⚠️ Imperfections & Future Work
This project is a robust proof-of-concept, but there are clear areas for improvement:

### Imperfections:

API Dependency: The historical data pipeline is entirely dependent on the free mfapi.in API. If this API goes down or becomes unreliable, the initial build will fail.

Static Risk-Free Rate: The Sharpe Ratio calculation uses a static risk-free rate of 4%. In a real-world application, this should be dynamic and fetched from a reliable source like RBI bond yields.

Simplistic Recommendation Score: The suitability score is based on a simple weighted average. A more advanced model could use machine learning (e.g., clustering users and funds) for more nuanced recommendations.

### Future Enhancements:

Web Interface: Build a web application using Streamlit or Flask/Django to provide a user-friendly interface for setting goals and viewing recommendations, hiding the complexity of the notebooks.

Portfolio Backtesting: Add a feature to simulate how a recommended portfolio would have performed over the last 5-10 years.

Direct-from-PDF Analysis: Allow users to upload their CAS (Consolidated Account Statement) PDF, extract their current holdings, and analyze their existing portfolio's health and diversification.

Containerization: Dockerize the entire application (pipeline scripts, database, and web app) for easy deployment and scalability.

## 📊 Key Visuals from the Analysis
(This is where you should insert screenshots of your best charts)

1. Top Recommended Core Funds
(Insert screenshot of the 'Top 15 Core Diversified Funds' table)

2. Diversification Analysis - Dendrogram
(Insert screenshot of the Dendrogram chart)

3. Correlation Heatmap
(Insert screenshot of the Correlation Heatmap)


# SIP-Analyzer is the main file that contain the main ipynb file, run that and you will get all the necessary files to run the pipeline.

5. Individual Fund Technical Analysis
(Insert screenshot of the NAV chart with Bollinger Bands and RSI)

6. NAV Forecast
(Insert screenshot of the Prophet/Ensemble forecast chart)
