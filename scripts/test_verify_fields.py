import unittest
import pandas as pd
from verify_fields import verify_fields

class TestVerifyFields(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame for testing
        self.valid_data = pd.DataFrame({
            'List Number': ['A1', 'A2', 'A3'],
            'Agency Name': ['Agency 1', 'Agency 2', 'Agency 3'],
            'Status': ['Active', 'Sold', 'Active'],
            'Area': ['North', 'South', 'East'],
            'current_price': [100000, 200000, 300000],
            'property_type': ['House', 'Condo', 'House'],
            'construction_ft2': [1500, 1200, 1800],
            'Days on Market': [10, 20, 15]
        })
        
    def test_valid_data(self):
        """Test with valid data"""
        result = verify_fields(self.valid_data)
        self.assertTrue(result)
        
    def test_missing_required_field(self):
        """Test with missing required field"""
        invalid_data = self.valid_data.drop('Status', axis=1)
        result = verify_fields(invalid_data)
        self.assertFalse(result)
        
    def test_invalid_price(self):
        """Test with invalid price"""
        invalid_data = self.valid_data.copy()
        invalid_data.loc[0, 'current_price'] = -1000
        result = verify_fields(invalid_data)
        self.assertFalse(result)
        
    def test_duplicate_listings(self):
        """Test with duplicate listing numbers"""
        invalid_data = self.valid_data.copy()
        invalid_data.loc[2, 'List Number'] = 'A1'  # Create duplicate
        result = verify_fields(invalid_data)
        # Should still return True but log a warning
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
