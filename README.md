End-to-End Mutual Fund Analysis & Recommendation Engine
The Goal: From Raw Data to Actionable Investment Insights
The Indian mutual fund market offers thousands of schemes, making it overwhelming for an investor to choose the right one. This project tackles that challenge by building a complete, automated data pipeline and analysis engine.

The core idea is to create a system that can:

Automatically gather historical and daily performance data for every mutual fund in India.

Build a robust, local database to store this massive dataset efficiently.

Run a comprehensive analysis to calculate key performance and risk metrics (CAGR, Sharpe Ratio, Volatility).

Provide personalized recommendations based on an investor's specific goals (time horizon and risk tolerance).

Offer advanced tools for portfolio diversification and technical analysis.

This project moves beyond a simple analysis script; it is a proof-of-concept for a full-scale financial data intelligence platform.

🚀 Key Features
Automated Data Pipeline: Scripts to fetch full historical data from the mfapi.in API and daily updates from the official AMFI source.

Robust Database Backend: Uses MySQL to store over a million NAV records, with intelligent data validation and duplicate handling.

Comprehensive Analysis Engine: Calculates 1, 3, 5, and 10-year CAGR, fund age, since-inception returns, annualized volatility, and Sharpe Ratio for thousands of funds.

Intelligent Fund Filtering: Automatically identifies and excludes unsuitable funds (like Fixed Maturity Plans, ETFs, closed-ended schemes) to ensure analysis is relevant for regular investors.

Personalized Recommendation Engine:

Scores funds based on a user's risk tolerance ('Low', 'Medium', 'High') and investment horizon.

Separates recommendations into Core (Diversified) and Specialized (Thematic) funds.

Advanced Diversification Tools:

Generates a Correlation Heatmap and Hierarchical Clustering Dendrogram to help users build a truly diversified portfolio by selecting funds that don't move in lockstep.

Predictive Forecasting: Uses an ensemble of Prophet and Holt-Winters models to forecast a fund's future NAV and visualize its year-over-year growth.

Technical Deep-Dive: For any top-recommended fund, it generates a technical chart with Moving Averages (SMAs), Bollinger Bands, and the Relative Strength Index (RSI) to identify trends and potential entry/exit points.

🛠️ Technology Stack
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

⚙️ How It Works: The Core Logic
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

🔧 How to Use This Project
Prerequisites:

Python 3.8+

A running MySQL server instance.

Setup:

Clone the repository: git clone https://github.com/your-username/SIP-Analyser.git

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

⚠️ Imperfections & Future Work
This project is a robust proof-of-concept, but there are clear areas for improvement:

Imperfections:

API Dependency: The historical data pipeline is entirely dependent on the free mfapi.in API. If this API goes down or becomes unreliable, the initial build will fail.

Static Risk-Free Rate: The Sharpe Ratio calculation uses a static risk-free rate of 4%. In a real-world application, this should be dynamic and fetched from a reliable source like RBI bond yields.

Simplistic Recommendation Score: The suitability score is based on a simple weighted average. A more advanced model could use machine learning (e.g., clustering users and funds) for more nuanced recommendations.

Future Enhancements:

Web Interface: Build a web application using Streamlit or Flask/Django to provide a user-friendly interface for setting goals and viewing recommendations, hiding the complexity of the notebooks.

Portfolio Backtesting: Add a feature to simulate how a recommended portfolio would have performed over the last 5-10 years.

Direct-from-PDF Analysis: Allow users to upload their CAS (Consolidated Account Statement) PDF, extract their current holdings, and analyze their existing portfolio's health and diversification.

Containerization: Dockerize the entire application (pipeline scripts, database, and web app) for easy deployment and scalability.

📊 Key Visuals from the Analysis
(This is where you should insert screenshots of your best charts)

1. Top Recommended Core Funds
(Insert screenshot of the 'Top 15 Core Diversified Funds' table)

2. Diversification Analysis - Dendrogram
(Insert screenshot of the Dendrogram chart)

3. Correlation Heatmap
(Insert screenshot of the Correlation Heatmap)

4. Individual Fund Technical Analysis
(Insert screenshot of the NAV chart with Bollinger Bands and RSI)

5. NAV Forecast
(Insert screenshot of the Prophet/Ensemble forecast chart)
