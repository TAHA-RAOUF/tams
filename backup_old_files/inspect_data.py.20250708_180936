#!/usr/bin/env python3
"""
Data inspection script for TAQATHON Excel file
Checks the structure and content of the Excel file before seeding
"""

import pandas as pd
import sys
import os

def inspect_excel_data():
    """Inspect the Excel file structure and content"""
    
    excel_path = "ml_models/Taqathon_data_01072025.xlsx"
    
    try:
        print(f"📖 Reading data from {excel_path}...")
        df = pd.read_excel(excel_path)
        
        print(f"✅ Successfully loaded Excel file")
        print(f"📊 Total records: {len(df)}")
        print(f"📋 Total columns: {len(df.columns)}")
        
        print("\n🔍 Column names and sample data:")
        print("=" * 60)
        
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")
            # Show first non-null value as example
            sample_value = df[col].dropna().iloc[0] if not df[col].dropna().empty else "No data"
            print(f"     Example: {sample_value}")
            print(f"     Type: {df[col].dtype}")
            print(f"     Non-null values: {df[col].count()}/{len(df)}")
            print()
        
        print("\n📈 First 3 rows of data:")
        print("=" * 60)
        print(df.head(3).to_string())
        
        print(f"\n📉 Data info:")
        print("=" * 60)
        print(df.info())
        
        print(f"\n🎯 Checking for prediction columns:")
        prediction_cols = ["Fiabilité Intégrité", "Disponibilté", "Process Safety", "Criticité"]
        for col in prediction_cols:
            if col in df.columns:
                print(f"   ✅ Found: {col}")
                print(f"      Range: {df[col].min():.2f} to {df[col].max():.2f}")
                print(f"      Mean: {df[col].mean():.2f}")
            else:
                print(f"   ❌ Missing: {col}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 TAQATHON Excel Data Inspector")
    print("=" * 50)
    inspect_excel_data()
