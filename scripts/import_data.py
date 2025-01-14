import pandas as pd
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from datetime import datetime
import numpy as np
from setup_database import Property, FeatureCategory, Feature, PropertyFeature
from mls_field_mapper import MLSFieldMapper
import os

def create_backup(engine, timestamp):
    """Create backup using pandas"""
    try:
        print("Creating backup...")
        query = "SELECT * FROM properties"
        df = pd.read_sql_query(query, engine)
        backup_path = f'data/backup_{timestamp}.csv'
        df.to_csv(backup_path, index=False, encoding='utf-8')
        print(f"Successfully created backup: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Warning: Could not create backup: {str(e)}")
        return None

def try_read_csv(file_path):
    """Try different encodings to read CSV"""
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    
    for encoding in encodings:
        try:
            print(f"Trying to read CSV with {encoding} encoding...")
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"Successfully read CSV with {encoding} encoding")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"Error with {encoding} encoding: {str(e)}")
    
    raise ValueError("Could not read CSV file with any supported encoding")

def import_data(csv_path, session):
    print(f"Reading {csv_path}...")
    try:
        df = try_read_csv(csv_path)
        print(f"Found {len(df)} rows")
        
        mapper = MLSFieldMapper()
        processed_file = csv_path.replace('.csv', '_processed.csv')
        df = mapper.process_dataframe(df)
        
        df.to_csv(processed_file, index=False, encoding='utf-8')
        print(f"Saved processed file to {processed_file}")
        
        print("Importing/Updating properties...")
        records_updated = 0
        records_created = 0
        
        for idx, row in df.iterrows():
            try:
                existing_prop = session.query(Property).filter_by(
                    list_number=str(row['List Number']) if pd.notna(row['List Number']) else None
                ).first()
                
                prop_data = {
                    'list_number': str(row['List Number']) if pd.notna(row['List Number']) else None,
                    'agency_name': row.get('Agency Name'),
                    'agency_phone': row.get('Agency Phone'),
                    'listing_agent': row.get('Listing Agent'),
                    'property_type': row.get('property_type'),
                    'status': row.get('Status'),
                    'days_on_market': row.get('Days on Market'),
                    'area': row.get('Area'),
                    'community': row.get('Community'),
                    'initial_price': row.get('initial_price'),
                    'current_price': row.get('current_price'),
                    'sold_price': row.get('sold_price'),
                    'development_name': row.get('property_name'),
                    'state': row.get('state'),
                    'construction_ft2': row.get('construction_ft2'),
                    'lot_measurements': row.get('lot_measurements'),
                    'half_bath': row.get('half_bath'),
                    'floor_number': row.get('floor_number'),
                    'furnished': row.get('furnished'),
                    'construction_m2': row.get('construction_m2')
                }

                if existing_prop:
                    for key, value in prop_data.items():
                        setattr(existing_prop, key, value)
                    prop = existing_prop
                    records_updated += 1
                else:
                    prop = Property(**prop_data)
                    session.add(prop)
                    records_created += 1

                session.flush()
                
                if pd.notna(row.get('Features')):
                    if existing_prop:
                        session.query(PropertyFeature).filter_by(property_id=prop.id).delete()
                    
                    features_list = str(row['Features']).split(';')
                    for feature in features_list:
                        if '|' in feature:
                            category_name, feature_name, value = feature.split('|')
                            category = get_or_create_category(session, category_name.strip())
                            feature = get_or_create_feature(session, category.id, feature_name.strip())
                            prop_feature = PropertyFeature(
                                property_id=prop.id,
                                feature_id=feature.id,
                                value=value.strip()
                            )
                            session.add(prop_feature)
                
                if idx % 10 == 0:  # Commit every 10 records
                    session.commit()
                    print(f"Processed {idx+1}/{len(df)} records... (Updated: {records_updated}, Created: {records_created})"))