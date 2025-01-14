import pandas as pd
import logging
from datetime import datetime

def verify_fields(df: pd.DataFrame) -> bool:
    """Verify all required fields are present and valid"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging.basicConfig(
        filename=f'field_verification_log_{timestamp}.txt',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Required fields
        required_fields = [
            'List Number',
            'Agency Name',
            'Status',
            'Area',
            'current_price',
            'property_type'
        ]
        
        # Check for missing required fields
        missing_fields = [field for field in required_fields if field not in df.columns]
        if missing_fields:
            logging.error(f"Missing required fields: {missing_fields}")
            return False
            
        # Verify data types
        type_checks = {
            'List Number': str,
            'current_price': [float, int],
            'construction_ft2': [float, int],
            'Days on Market': [float, int]
        }
        
        for field, expected_types in type_checks.items():
            if field in df.columns:
                if not isinstance(expected_types, list):
                    expected_types = [expected_types]
                    
                valid_type = any(df[field].dtype == type for type in expected_types)
                if not valid_type:
                    logging.error(f"Invalid data type for {field}. Expected {expected_types}, got {df[field].dtype}")
                    return False
                    
        # Check for empty values in required fields
        for field in required_fields:
            empty_count = df[field].isna().sum()
            if empty_count > 0:
                logging.warning(f"Found {empty_count} empty values in {field}")
                
        # Verify value ranges
        if 'current_price' in df.columns:
            invalid_prices = (df['current_price'] <= 0).sum()
            if invalid_prices > 0:
                logging.error(f"Found {invalid_prices} invalid prices (<=0)")
                return False
                
        if 'construction_ft2' in df.columns:
            invalid_sizes = (df['construction_ft2'] <= 0).sum()
            if invalid_sizes > 0:
                logging.warning(f"Found {invalid_sizes} invalid construction sizes (<=0)")
                
        # Check for duplicate listings
        duplicates = df['List Number'].duplicated().sum()
        if duplicates > 0:
            logging.warning(f"Found {duplicates} duplicate listing numbers")
            
        logging.info("Field verification completed successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error during field verification: {str(e)}")
        return False

def main():
    try:
        # Load CSV file
        df = pd.read_csv('data/mls.csv')
        print(f"Loaded {len(df)} records")
        
        # Verify fields
        if verify_fields(df):
            print("Field verification passed")
        else:
            print("Field verification failed - check log file for details")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
