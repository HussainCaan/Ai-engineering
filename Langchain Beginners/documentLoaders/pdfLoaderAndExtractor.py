# from langchain_community.document_loaders import PDFPlumberLoader
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import UnstructuredPDFLoader
from sqlalchemy import text
import sys
from pathlib import Path
from datetime import datetime
from prompts import FINANCIAL_EXTRACTION_PROMPT, TRADING_ADVISORY_PROMPT

# Add parent directory to path to import db modules
sys.path.append(str(Path(__file__).parent.parent))
from db.session import engine

load_dotenv()

# ============================================
# STEP 1: GET LATEST REPORT METADATA
# ============================================
def get_latest_report_metadata(symbol, report_type='Quarterly'):
    """
    Get the complete metadata row for the latest report.
    Returns: dict with id, symbol, year, period, file_path, extracted_data, etc.
    Returns None if no report found.
    """
    query = text("""
        SELECT id, symbol, report_type, year, period, file_path, 
               extracted_data, extracted_at
        FROM financial_reports_metadata 
        WHERE symbol = :symbol 
        AND report_type = :report_type
        ORDER BY year DESC, period DESC 
        LIMIT 1
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {'symbol': symbol, 'report_type': report_type})
        row = result.fetchone()
        
        if not row:
            return None
        
        # Return as dictionary for easy access
        return {
            'id': row[0],
            'symbol': row[1],
            'report_type': row[2],
            'year': row[3],
            'period': row[4],
            'file_path': row[5],
            'extracted_data': row[6],  # This will be None if not extracted yet
            'extracted_at': row[7]
        }


# ============================================
# STEP 2: CHECK IF DATA ALREADY EXTRACTED
# ============================================
def is_data_extracted(metadata):
    """
    Check if extracted_data exists in the metadata.
    Used as condition for RunnableBranch.
    
    Returns: True if data exists, False if needs extraction
    """
    if not metadata:
        return False
    return metadata.get('extracted_data') is not None


# ============================================
# STEP 3A: LOAD EXTRACTED DATA FROM DATABASE
# ============================================
def load_extracted_data_from_db(metadata):
    """
    Branch A: Load already extracted data from database.
    Used when extracted_data is not None.
    
    Returns: The extracted financial data (as JSON string or dict)
    """
    print(f"✅ Found cached extraction from {metadata['extracted_at']}")
    return metadata['extracted_data']


# ============================================
# STEP 3B: EXTRACT FROM PDF AND SAVE TO DATABASE
# ============================================
def extract_and_save_to_db(metadata):
    """
    Branch B: Extract financial data from PDF using LLM #1 and save to database.
    Used when extracted_data is None.
    
    Returns: The extracted financial data (as string)
    """
    print(f"📄 Loading PDF: {metadata['file_path']}")
    
    # Load PDF
    loader = UnstructuredPDFLoader(metadata['file_path'], strategy="ocr_only")
    docs = loader.load()
    
    print("🤖 Extracting financial data with LLM #1...")
    
    # Setup LLM #1
    model = ChatOpenAI(
        model="xiaomi/mimo-v2-flash:free",
        temperature=0.4,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "LangChain Learning Project"
        }
    )
    
    prompt = PromptTemplate(
        template=FINANCIAL_EXTRACTION_PROMPT,
        input_variables=["report_text"]
    )
    
    parser = StrOutputParser()
    chain = prompt | model | parser
    
    # Extract data
    extracted_data = chain.invoke({"report_text": docs[0].page_content})
    
    # Save to database
    print("💾 Saving extracted data to database...")
    update_query = text("""
        UPDATE financial_reports_metadata
        SET extracted_data = CAST(:data AS jsonb),
            extracted_at = :timestamp
        WHERE id = :id
    """)
    
    with engine.connect() as conn:
        conn.execute(update_query, {
            'data': extracted_data,
            'timestamp': datetime.now(),
            'id': metadata['id']
        })
        conn.commit()
    
    print("✅ Data extracted and saved!")
    return extracted_data


# ============================================
# STEP 4: GET STOCK PRICES (LAST 30 DAYS)
# ============================================
def get_stock_prices(symbol, days=30):
    """
    Get stock prices for the last N days from database.
    Returns: dict with current_price, open_price, high, low, volume, price_change_pct
    """
    query = text("""
        SELECT time, open, high, low, close, volume
        FROM stock_prices
        WHERE symbol = :symbol
        ORDER BY time DESC
        LIMIT :days
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {'symbol': symbol, 'days': days})
        rows = result.fetchall()
        
        if not rows:
            return None
        
        # Latest price is first row, oldest is last
        latest = rows[0]
        oldest = rows[-1]
        
        return {
            'current_price': float(latest[4]),  # close
            'open_price': float(oldest[1]),     # open from N days ago
            'high_price': max(float(r[2]) for r in rows),
            'low_price': min(float(r[3]) for r in rows),
            'volume': sum(r[5] for r in rows if r[5]),
            'price_change_pct': round(((float(latest[4]) - float(oldest[4])) / float(oldest[4])) * 100, 2)
        }


# ============================================
# STEP 5: GET TECHNICAL INDICATORS
# ============================================
def get_technical_indicators(symbol):
    """
    Get latest technical indicators from database.
    Returns: Formatted string ready for TRADING_ADVISORY_PROMPT
    """
    query = text("""
        SELECT sma_20, sma_50, ema_12, ema_26, rsi_14, 
               macd, macd_signal, macd_histogram,
               bb_upper, bb_middle, bb_lower,
               stoch_k, stoch_d
        FROM technical_indicators
        WHERE symbol = :symbol
        ORDER BY time DESC
        LIMIT 1
    """)
    
    with engine.connect() as conn:
        result = conn.execute(query, {'symbol': symbol})
        row = result.fetchone()
        
        if not row:
            return "Technical indicators not available"
        
        # Format indicators for the prompt
        return f"""- 20-Day SMA: PKR {float(row[0]):.2f}
- 50-Day SMA: PKR {float(row[1]):.2f}
- Trend: {'Bullish' if row[0] > row[1] else 'Bearish'} (SMA20 {'above' if row[0] > row[1] else 'below'} SMA50)
- RSI (14): {float(row[4]):.1f} ({'Overbought' if row[4] > 70 else 'Oversold' if row[4] < 30 else 'Neutral'})
- MACD: {float(row[5]):.2f} (Signal: {float(row[6]):.2f}) - {'Bullish' if row[5] > row[6] else 'Bearish'}
- Bollinger Bands: Upper {float(row[8]):.2f}, Lower {float(row[10]):.2f}
- Stochastic %K: {float(row[11]):.1f}, %D: {float(row[12]):.1f}"""


# ============================================
# STEP 6: BUILD CONDITIONAL BRANCH (RUNNABLE)
# ============================================
def build_extraction_branch():
    """
    Create a RunnableBranch that:
    - Checks if data is extracted
    - If YES: Load from database
    - If NO: Extract from PDF and save
    
    Returns: RunnableBranch
    """
    branch = RunnableBranch(
        (
            # Condition: Is data already extracted?
            lambda metadata: is_data_extracted(metadata),
            # If True: Load from database
            RunnableLambda(load_extracted_data_from_db)
        ),
        # Default (If False): Extract from PDF
        RunnableLambda(extract_and_save_to_db)
    )
    
    return branch


# ============================================
# STEP 7: MAIN ANALYSIS FUNCTION
# ============================================
def analyze_stock(symbol):
    """
    Complete analysis pipeline:
    1. Get metadata
    2. Branch: Load cached OR Extract from PDF
    3. Get stock prices
    4. Get technical indicators
    5. Send everything to LLM #2 for recommendation
    
    Returns: Trading recommendation from LLM #2
    """
    print("\n" + "="*70)
    print(f"🚀 STARTING ANALYSIS FOR: {symbol}")
    print("="*70 + "\n")
    
    # Step 1: Get metadata
    print("📊 Step 1: Getting report metadata...")
    metadata = get_latest_report_metadata(symbol)
    if not metadata:
        return f"❌ No financial report found for {symbol}"
    print(f"   Found: {metadata['year']} {metadata['period']}\n")
    
    # Step 2: Get or extract financial data (using branch)
    print("📄 Step 2: Getting financial data...")
    extraction_branch = build_extraction_branch()
    financial_data = extraction_branch.invoke(metadata)
    print()
    
    # Step 3: Get stock prices
    print("📈 Step 3: Getting stock prices (last 30 days)...")
    stock_data = get_stock_prices(symbol, days=30)
    if not stock_data:
        return f"❌ No price data found for {symbol}"
    print(f"   Current: PKR {stock_data['current_price']:.2f}")
    print(f"   30-Day Change: {stock_data['price_change_pct']}%\n")
    
    # Step 4: Get technical indicators
    print("🔢 Step 4: Getting technical indicators...")
    indicators = get_technical_indicators(symbol)
    print("   ✅ Indicators loaded\n")
    
    # Step 5: Get company info for context
    query = text("SELECT company_name, sector FROM symbols WHERE symbol = :symbol")
    with engine.connect() as conn:
        result = conn.execute(query, {'symbol': symbol})
        row = result.fetchone()
        company_name = row[0] if row else symbol
        sector = row[1] if row else "Unknown"
    
    # Step 6: Send to LLM #2 for trading recommendation
    print("💡 Step 5: Generating trading recommendation with LLM #2...")
    
    model = ChatOpenAI(
        model="qwen/qwen-2-7b-instruct:free",
        temperature=0.3,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "LangChain Learning Project"
        }
    )
    
    prompt = PromptTemplate(
        template=TRADING_ADVISORY_PROMPT,
        input_variables=["symbol", "company_name", "sector", "current_price", 
                        "analysis_date", "financial_metrics", "days", "open_price",
                        "high_price", "low_price", "price_change_pct", "volume",
                        "technical_indicators"]
    )
    
    parser = StrOutputParser()
    chain = prompt | model | parser
    
    recommendation = chain.invoke({
        "symbol": symbol,
        "company_name": company_name,
        "sector": sector,
        "current_price": stock_data['current_price'],
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "financial_metrics": financial_data,
        "days": 30,
        "open_price": stock_data['open_price'],
        "high_price": stock_data['high_price'],
        "low_price": stock_data['low_price'],
        "price_change_pct": stock_data['price_change_pct'],
        "volume": stock_data['volume'],
        "technical_indicators": indicators
    })
    
    # Print results
    print("\n" + "="*70)
    print(f"📊 FINANCIAL DATA (from {metadata['year']} {metadata['period']})")
    print("="*70)
    print(financial_data)
    print("="*70 + "\n")
    
    print("\n" + "="*70)
    print(f"💡 TRADING RECOMMENDATION FOR: {symbol}")
    print("="*70)
    print(recommendation)
    print("="*70 + "\n")
    
    return recommendation


# ============================================
# TESTING
# ============================================
if __name__ == "__main__":
    # Run complete analysis
    analyze_stock("ABL")