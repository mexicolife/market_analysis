import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
from typing import Dict, List, Any, Tuple, Optional
from sqlalchemy import create_engine
import json
from datetime import datetime, timedelta

class MarketAnalytics:
    def __init__(self, db_engine):
        self.engine = db_engine
        self.models = {}
        self.transformers = {}
        
    def analyze_price_trends(self, area: Optional[str] = None, 
                           property_type: Optional[str] = None) -> Dict[str, Any]:
        """Analyze and predict price trends"""
        # Build query based on filters
        query = """
            SELECT 
                p.*,
                EXTRACT(MONTH FROM begin_date) as month,
                EXTRACT(YEAR FROM begin_date) as year
            FROM properties p
            WHERE begin_date IS NOT NULL
                AND current_price > 0
        """
        
        if area:
            query += f" AND area = '{area}'"
        if property_type:
            query += f" AND property_type = '{property_type}'"
            
        df = pd.read_sql(query, self.engine)
        
        # Prepare features for modeling
        features = [
            'construction_ft2', 'year', 'month', 
            'total_bedrooms', 'total_baths', 'garage_stalls'
        ]
        
        categorical_features = ['property_type', 'area']
        target = 'current_price'
        
        # Create and train price prediction model
        model, transformer = self._train_price_model(
            df, features, categorical_features, target
        )
        
        # Generate predictions and insights
        trends = self._analyze_temporal_trends(df, model, transformer)
        seasonality = self._analyze_seasonality(df)
        forecasts = self._generate_price_forecasts(df, model, transformer)
        
        return {
            "trends": trends,
            "seasonality": seasonality,
            "forecasts": forecasts,
            "model_metrics": self._get_model_metrics(model)
        }
