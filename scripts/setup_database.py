from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True)
    list_number = Column(String, unique=True)
    agency_name = Column(String)
    agency_phone = Column(String)
    listing_agent = Column(String)
    property_type = Column(String)
    status = Column(String)
    days_on_market = Column(Integer)
    area = Column(String)
    community = Column(String)
    initial_price = Column(Float)
    current_price = Column(Float)
    sold_price = Column(Float)
    development_name = Column(String)
    state = Column(String)
    construction_ft2 = Column(Float)
    lot_measurements = Column(String)
    half_bath = Column(Integer)
    floor_number = Column(Integer)
    furnished = Column(Boolean)
    construction_m2 = Column(Float)
    begin_date = Column(DateTime)
    
    features = relationship('PropertyFeature', back_populates='property')

class FeatureCategory(Base):
    __tablename__ = 'feature_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    features = relationship('Feature', back_populates='category')

class Feature(Base):
    __tablename__ = 'features'
    
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey('feature_categories.id'))
    name = Column(String)
    
    category = relationship('FeatureCategory', back_populates='features')
    property_features = relationship('PropertyFeature', back_populates='feature')

class PropertyFeature(Base):
    __tablename__ = 'property_features'
    
    id = Column(Integer, primary_key=True)
    property_id = Column(Integer, ForeignKey('properties.id'))
    feature_id = Column(Integer, ForeignKey('features.id'))
    value = Column(String)
    
    property = relationship('Property', back_populates='features')
    feature = relationship('Feature', back_populates='property_features')

def setup_database():
    DATABASE_URL = "postgresql://postgres:admin@localhost/market_analysis_db"
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    setup_database()
