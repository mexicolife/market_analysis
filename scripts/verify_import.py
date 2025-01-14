import pandas as pd
import logging
from datetime import datetime
from sqlalchemy import create_engine
from typing import Tuple, Optional

def verify_import(csv_path: str, db_url: str) -> Tuple[bool, Optional[str]]:
    """Verify that data was imported correctly"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        filename=f'import_verification_log_{timestamp}.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Read CSV file
        logging.info(f"Reading CSV file: {csv_path}")
        csv_df = pd.read_csv(csv_path)
        csv_count = len(csv_df)
        logging.info(f"CSV contains {csv_count} records")
        
        # Connect to database
        logging.info("Connecting to database")
        engine = create_engine(db_url)
        
        # Count records in database
        with engine.connect() as conn:
            result = conn.execute("SELECT COUNT(*) FROM properties")
            db_count = result.scalar()
            logging.info(f"Database contains {db_count} records")
            
        # Compare record counts
        if db_count < csv_count:
            msg = f"Missing records: CSV has {csv_count} but DB has {db_count}"
            logging.error(msg)
            return False, msg
            
        # Verify key fields
        with engine.connect() as conn:
            # Sample some records for detailed comparison
            db_df = pd.read_sql(
                "SELECT * FROM properties LIMIT 100",
                conn
            )
            
        # Check data types
        type_mismatches = []
        for col in db_df.columns:
            if col in csv_df.columns:
                if db_df[col].dtype != csv_df[col].dtype:
                    type_mismatches.append(f"{col}: CSV={csv_df[col].dtype}, DB={db_df[col].dtype}")
                    
        if type_mismatches:
            msg = f"Data type mismatches found: {', '.join(type_mismatches)}"
            logging.warning(msg)
            
        # Check for null values in required fields
        required_fields = ['list_number', 'property_type', 'status', 'area']
        null_counts = db_df[required_fields].isnull().sum()
        
        if null_counts.sum() > 0:
            fields_with_nulls = null_counts[null_counts > 0].index.tolist()
            msg = f"Found null values in required fields: {fields_with_nulls}"
            logging.error(msg)
            return False, msg
            
        logging.info("Import verification completed successfully")
        return True, None
        
    except Exception as e:
        error_msg = f"Error during import verification: {str(e)}"
        logging.error(error_msg)
        return False, error_msg

def main():
    try:
        db_url = "postgresql://postgres:admin@localhost/market_analysis_db"
        csv_path = "data/mls.csv"
        
        success, error_msg = verify_import(csv_path, db_url)
        
        if success:
            print("Import verification passed successfully!")
        else:
            print(f"Import verification failed: {error_msg}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
