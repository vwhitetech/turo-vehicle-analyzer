turo_agent.py import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dataclasses import dataclass
from typing import List, Dict
import time

# Configure page
st.set_page_config(
    page_title="Turo Purchase Agent",
    page_icon="🚗",
    layout="wide"
)

@dataclass
class Vehicle:
    make: str
    model: str
    year: int
    price: int
    mileage: int
    location: str
    url: str
    estimated_daily_rate: float
    roi_score: float

class TuroAgent:
    def __init__(self):
        self.db_name = "turo_data.db"
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id INTEGER PRIMARY KEY,
                make TEXT,
                model TEXT,
                year INTEGER,
                price INTEGER,
                mileage INTEGER,
                location TEXT,
                url TEXT,
                estimated_daily_rate REAL,
                roi_score REAL,
                date_added TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_analysis (
                id INTEGER PRIMARY KEY,
                vehicle_type TEXT,
                avg_daily_rate REAL,
                demand_score INTEGER,
                competition_level TEXT,
                date_analyzed TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_turo_market(self, location: str = "Los Angeles") -> Dict:
        """Simulate market analysis (in real version, would scrape Turo)"""
        # Simulated data - replace with actual Turo scraping
        market_data = {
            "economy": {"avg_rate": 45, "demand": 8, "competition": "High"},
            "compact": {"avg_rate": 55, "demand": 9, "competition": "High"},
            "midsize": {"avg_rate": 65, "demand": 7, "competition": "Medium"},
            "luxury": {"avg_rate": 150, "demand": 6, "competition": "Low"},
            "suv": {"avg_rate": 85, "demand": 8, "competition": "Medium"},
            "truck": {"avg_rate": 95, "demand": 5, "competition": "Low"}
        }
        return market_data
    
    def calculate_roi(self, purchase_price: int, estimated_daily_rate: float, 
                     vehicle_type: str = "midsize") -> float:
        """Calculate estimated ROI for a vehicle"""
        # Assumptions
        monthly_rental_days = 20  # Conservative estimate
        monthly_revenue = estimated_daily_rate * monthly_rental_days
        
        # Costs (monthly)
        insurance = 200
        maintenance = 150
        turo_fee_percent = 0.15
        depreciation_monthly = purchase_price * 0.01  # 1% per month
        
        monthly_costs = insurance + maintenance + (monthly_revenue * turo_fee_percent) + depreciation_monthly
        monthly_profit = monthly_revenue - monthly_costs
        
        if monthly_profit <= 0:
            return 0
        
        # Payback period in months
        payback_months = purchase_price / monthly_profit
        
        # ROI score (higher is better, max 10)
        roi_score = max(0, min(10, (monthly_profit / purchase_price) * 100))
        
        return roi_score
    
    def scrape_vehicles(self, max_price: int = 25000, location: str = "Los Angeles") -> List[Vehicle]:
        """Simulate vehicle scraping (replace with actual scraping)"""
        # Simulated vehicle data
        sample_vehicles = [
            Vehicle("Toyota", "Camry", 2019, 18000, 45000, location, "#", 55, 0),
            Vehicle("Honda", "Civic", 2020, 20000, 35000, location, "#", 50, 0),
            Vehicle("Nissan", "Altima", 2018, 16000, 55000, location, "#", 52, 0),
            Vehicle("BMW", "3 Series", 2019, 24000, 40000, location, "#", 85, 0),
            Vehicle("Tesla", "Model 3", 2020, 35000, 30000, location, "#", 95, 0),
            Vehicle("Jeep", "Wrangler", 2019, 28000, 35000, location, "#", 75, 0),
            Vehicle("Mercedes", "C-Class", 2018, 26000, 42000, location, "#", 90, 0),
            Vehicle("Audi", "A4", 2019, 29000, 38000, location, "#", 88, 0),
            Vehicle("Ford", "Mustang", 2020, 32000, 25000, location, "#", 82, 0),
            Vehicle("Chevrolet", "Tahoe", 2018, 35000, 60000, location, "#", 110, 0),
        ]
        
        # Filter by price and calculate ROI
        filtered_vehicles = []
        for vehicle in sample_vehicles:
            if vehicle.price <= max_price:
                vehicle.roi_score = self.calculate_roi(vehicle.price, vehicle.estimated_daily_rate)
                filtered_vehicles.append(vehicle)
        
        return filtered_vehicles
    
    def save_vehicles(self, vehicles: List[Vehicle]):
        """Save vehicles to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        for vehicle in vehicles:
            cursor.execute('''
                INSERT OR REPLACE INTO vehicles 
                (make, model, year, price, mileage, location, url, estimated_daily_rate, roi_score, date_added)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                vehicle.make, vehicle.model, vehicle.year, vehicle.price,
                vehicle.mileage, vehicle.location, vehicle.url,
                vehicle.estimated_daily_rate, vehicle.roi_score, datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_stored_vehicles(self) -> pd.DataFrame:
        """Retrieve vehicles from database"""
        conn = sqlite3.connect(self.db_name)
        df = pd.read_sql_query("SELECT * FROM vehicles ORDER BY roi_score DESC", conn)
        conn.close()
        return df

def main():
    st.title("🚗 Turo Vehicle Purchase Agent")
    st.markdown("*AI-powered vehicle selection for Turo hosts*")
    
    # Initialize agent
    agent = TuroAgent()
    
    # Sidebar controls
    st.sidebar.header("Search Parameters")
    max_price = st.sidebar.slider("Maximum Price ($)", 10000, 50000, 25000, step=1000)
    location = st.sidebar.selectbox("Location", ["Los Angeles", "New York", "Miami", "Chicago", "Austin"])
    
    if st.sidebar.button("🔍 Search Vehicles", type="primary"):
        with st.spinner("Analyzing market and finding vehicles..."):
            # Get market data
            market_data = agent.analyze_turo_market(location)
            
            # Search vehicles
            vehicles = agent.scrape_vehicles(max_price, location)
            agent.save_vehicles(vehicles)
            
            st.success(f"Found {len(vehicles)} vehicles matching your criteria!")
    
    # Main dashboard
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🎯 Recommended Vehicles")
        
        # Get stored vehicles
        df = agent.get_stored_vehicles()
        
        if not df.empty:
            # Display top vehicles
            for idx, row in df.head(10).iterrows():
                with st.container():
                    st.markdown("---")
                    cols = st.columns([3, 1, 1])
                    
                    with cols[0]:
                        st.subheader(f"{row['year']} {row['make']} {row['model']}")
                        st.write(f"📍 {row['location']} • {row['mileage']:,} miles")
                        
                        # ROI indicator
                        roi_color = "green" if row['roi_score'] > 6 else "orange" if row['roi_score'] > 3 else "red"
                        st.markdown(f"**ROI Score:** :{roi_color}[{row['roi_score']:.1f}/10]")
                    
                    with cols[1]:
                        st.metric("Price", f"${row['price']:,}")
                        st.metric("Est. Daily Rate", f"${row['estimated_daily_rate']:.0f}")
                    
                    with cols[2]:
                        if st.button(f"💰 Analyze", key=f"analyze_{idx}"):
                            # Show detailed analysis
                            with st.expander("Detailed Financial Analysis"):
                                monthly_days = 20
                                monthly_revenue = row['estimated_daily_rate'] * monthly_days
                                monthly_costs = 200 + 150 + (monthly_revenue * 0.15) + (row['price'] * 0.01)
                                monthly_profit = monthly_revenue - monthly_costs
                                payback_months = row['price'] / monthly_profit if monthly_profit > 0 else 999
                                
                                st.write(f"**Monthly Revenue:** ${monthly_revenue:,.0f}")
                                st.write(f"**Monthly Costs:** ${monthly_costs:,.0f}")
                                st.write(f"**Monthly Profit:** ${monthly_profit:,.0f}")
                                st.write(f"**Payback Period:** {payback_months:.1f} months")
        else:
            st.info("No vehicles found. Click 'Search Vehicles' to get started!")
    
    with col2:
        st.header("📊 Market Insights")
        
        # Market analysis
        market_data = agent.analyze_turo_market(location)
        
        st.subheader("Vehicle Categories")
        for category, data in market_data.items():
            with st.expander(f"{category.title()} - ${data['avg_rate']}/day"):
                st.write(f"**Demand Score:** {data['demand']}/10")
                st.write(f"**Competition:** {data['competition']}")
                
                # Simple recommendation
                if data['demand'] > 7 and data['competition'] != "High":
                    st.success("🎯 Good opportunity!")
                elif data['demand'] > 8:
                    st.warning("⚡ High demand, high competition")
                else:
                    st.info("📈 Monitor this category")
    
    # Portfolio section
    st.header("📈 Portfolio Analysis")
    
    df = agent.get_stored_vehicles()
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_roi = df['roi_score'].mean()
            st.metric("Average ROI Score", f"{avg_roi:.1f}/10")
        
        with col2:
            total_investment = df['price'].sum()
            st.metric("Total Investment", f"${total_investment:,}")
        
        with col3:
            high_roi_count = len(df[df['roi_score'] > 6])
            st.metric("High ROI Vehicles", high_roi_count)
        
        # ROI distribution chart
        if len(df) > 0:
            fig = px.histogram(df, x='roi_score', nbins=10, 
                              title='ROI Score Distribution',
                              labels={'roi_score': 'ROI Score', 'count': 'Number of Vehicles'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Vehicle type analysis
            fig2 = px.scatter(df, x='price', y='estimated_daily_rate', 
                             size='roi_score', color='roi_score',
                             hover_data=['make', 'model', 'year'],
                             title='Price vs Daily Rate Analysis',
                             color_continuous_scale='RdYlGn')
            st.plotly_chart(fig2, use_container_width=True)
    
    # Instructions
    with st.expander("ℹ️ How to use this agent"):
        st.markdown("""
        **Getting Started:**
        1. Set your maximum price and location in the sidebar
        2. Click "Search Vehicles" to find opportunities
        3. Review the ROI scores and market insights
        4. Analyze specific vehicles for detailed financials
        
        **ROI Score Guide:**
        - 🟢 **7-10**: Excellent opportunity
        - 🟡 **4-6**: Moderate opportunity  
        - 🔴 **0-3**: Poor opportunity
        
        **Next Steps to Enhance:**
        - Connect to real vehicle listing APIs
        - Add actual Turo market scraping
        - Implement ML models for better predictions
        - Add alert system for new opportunities
        """)

if __name__ == "__main__":
    main()
