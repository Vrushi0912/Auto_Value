import os
import glob
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import pickle
import sqlite3

base_dir = os.path.join(os.path.dirname(__file__), 'scrapers')

cars24_files = glob.glob(os.path.join(base_dir, "cars24_*.csv"))
spinny_files = glob.glob(os.path.join(base_dir, "spinny_*.csv"))

data = []

for f in cars24_files:
    df = pd.read_csv(f)
    if 'name' not in df.columns:
        continue
    loc = os.path.basename(f).split('_')[1].split('.')[0].lower()
    for _, row in df.iterrows():
        try:
            name_parts = str(row['name']).split(' ', 1)
            year = int(name_parts[0])
            make_model = name_parts[1]
            make = make_model.split(' ')[0]
            model = ' '.join(make_model.split(' ')[1:])
            
            price_str = str(row['price']).lower()
            if 'lakh' in price_str:
                price = float(price_str.replace('lakh', '').replace(',', '').strip())
            else:
                price = float(price_str.replace(',', '').strip()) / 100000.0
                
            km_str = str(row['kilometer']).replace('km', '').replace(',', '').strip()
            km = float(km_str)
            
            fuel = str(row['fuel']).lower()
            transmission = str(row['transmission']).lower()
            link = str(row.get('link', ''))
            
            data.append({
                'carname': str(row['name']),
                'make': make.lower(),
                'model': model.lower(),
                'year': year,
                'kilometersdriven': km,
                'fueltype': fuel.capitalize(),
                'transmission': transmission,
                'location': loc,
                'city': loc,
                'price': f"{price:.2f} Lakh",
                'price_lakhs': price,
                'listingurl': link,
                'imageurl': '',
                'source': 'Cars24'
            })
        except Exception as e:
            continue

for f in spinny_files:
    df = pd.read_csv(f)
    if 'name' not in df.columns:
        continue
    loc = os.path.basename(f).split('_')[1].split('.')[0].lower()
    for _, row in df.iterrows():
        try:
            name_val = str(row['name'])
            first_line = name_val.split('\n')[0]
            name_parts = first_line.replace('"', '').split(' ', 1)
            year = int(name_parts[0])
            make_model = name_parts[1]
            make = make_model.split(' ')[0]
            model = ' '.join(make_model.split(' ')[1:])
            
            price_str = str(row['price']).lower()
            if 'lakh' in price_str:
                price = float(price_str.replace('lakh', '').replace(',', '').strip())
            else:
                price = float(price_str.replace(',', '').strip()) / 100000.0
                
            km_str = str(row['kilometer']).lower().replace('km', '').strip()
            if 'k' in km_str:
                km = float(km_str.replace('k', '').strip()) * 1000
            else:
                km = float(km_str.replace(',', '').strip())
                
            fuel = str(row['fuel']).lower()
            transmission = str(row['transmission']).lower()
            link = str(row.get('link', ''))
            
            address = str(row.get('location', loc))
            if address.lower() == 'nan':
                address = loc
            
            data.append({
                'carname': first_line.replace('"', ''),
                'make': make.lower(),
                'model': model.lower(),
                'year': year,
                'kilometersdriven': km,
                'fueltype': fuel.capitalize(),
                'transmission': transmission,
                'location': address,
                'city': loc,
                'price': f"{price:.2f} Lakh",
                'price_lakhs': price,
                'listingurl': link,
                'imageurl': '',
                'source': 'Spinny'
            })
        except Exception as e:
            continue

df_final = pd.DataFrame(data)
df_final.dropna(inplace=True)
df_final.to_csv(os.path.join(base_dir, 'all_car_listings_data_for_model.csv'), index=False)

# Save to SQLite DB for fast querying by the website
conn = sqlite3.connect(os.path.join(base_dir, 'merged_car_listings.db'))
df_final.to_sql('listings', conn, if_exists='replace', index=False)
conn.close()

X = df_final[['make', 'model', 'year', 'kilometersdriven', 'fueltype', 'transmission', 'city']].copy()
X = X.rename(columns={'kilometersdriven': 'kms_driven', 'fueltype': 'fuel_type', 'city': 'location'})

y = df_final['price_lakhs']

numeric_features = ['year', 'kms_driven']
categorical_features = ['make', 'model', 'fuel_type', 'transmission', 'location']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

pipeline = Pipeline(steps=[('preprocessor', preprocessor),
                           ('regressor', RandomForestRegressor(n_estimators=50, random_state=42))])

pipeline.fit(X, y)

with open(os.path.join(base_dir, 'car_price_model.pkl'), 'wb') as f:
    pickle.dump(pipeline, f)

print("Model trained successfully and DB created!")
