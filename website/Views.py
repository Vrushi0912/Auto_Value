from flask import Blueprint, render_template,request,flash,jsonify,redirect, session  
from .models import Users 
import requests 
import sqlite3 
import pandas as pd 
import json 
import pickle 
import numpy as np 
import os
from flask_login import login_required,current_user 

views = Blueprint("views",__name__) 

car_locations = ["Mumbai", "Pune", "Delhi","Hyderabad","Bangalore", 'Any'] 

@views.route("/",methods=["GET","POST"]) 
def index(): 
    return render_template("index.html") 

@views.route("/landing-page",methods=["GET","POST"]) 
@login_required 
def landing_page(): 
    companies = []
    fuel_types = ["Petrol","CNG","Diesel", "Any"] 
    popular_car_listings_dict = []
    spinny_featured_car_listings_dict = []
    cars24_featured_car_listings_dict = []
    
    user_id = session.get('user_id')  # Fetch user id from session 
    user = Users.query.get(user_id) if user_id else None  # Fetch user details using user id 

    return render_template('landing_page.html', 
                            companies=companies,
                            locations=car_locations,
                            fuel_types=fuel_types,
                            popular_cars=popular_car_listings_dict,
                            spinny_featured_cars=spinny_featured_car_listings_dict,
                            cars24_featured_cars=cars24_featured_car_listings_dict, 
                            user=user) 

def get_blogs_data(keyword=None):
    import csv
    import hashlib
    
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scrapers', 'car_blogs.csv')
    if not os.path.exists(csv_path):
        return [], []
        
    all_blogs = []
    blog_images = ['/static/blog_sierra_ev.png', '/static/blog_suv_dominance.png', '/static/blog_ev_infra.png', '/static/blog_hybrid_tech.png']
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row.get('title', '')
                source = row.get('source', 'AutoNews')
                url = row.get('link', '')
                
                # Filter out short titles (usually category links)
                if len(title.split()) >= 4:
                    # Deterministic image
                    h = hashlib.md5(title.encode('utf-8')).hexdigest()
                    img = blog_images[int(h, 16) % len(blog_images)]
                    
                    all_blogs.append({
                        'source': source,
                        'title': title,
                        'url': url,
                        'summary': 'Click to read more about this topic on ' + source + '.',
                        'image_url': img
                    })
    except Exception as e:
        print("Error reading blogs CSV:", e)
        return [], []
        
    # Apply keyword filter if provided
    if keyword:
        keyword = keyword.lower()
        all_blogs = [b for b in all_blogs if keyword in b['title'].lower() or keyword in b['source'].lower()]
        
    last_10_blogs = all_blogs[:10] if len(all_blogs) > 10 else all_blogs
    
    return all_blogs, last_10_blogs

@views.route("/api/blogs", methods=['GET'])
def api_blogs():
    all_blogs, last_10_blogs = get_blogs_data()
    return jsonify({"all_blogs": all_blogs, "last_10_blogs": last_10_blogs})

@views.route("/car-blogs", methods=["GET","POST"]) 
def car_blogs(): 
    user_id = session.get('user_id') 
    user = Users.query.get(user_id) if user_id else None 
    if request.method == "GET": 
        all_blogs, last_10_blogs = get_blogs_data()
        return render_template("car_blogs.html",all_blogs=all_blogs,last_10_blogs=last_10_blogs,user=user) 
    elif request.method == "POST": 
        keyword = request.form.get("search-input") 
        all_blogs, last_10_blogs = get_blogs_data(keyword)
        return render_template("car_blogs.html",all_blogs=all_blogs,last_10_blogs=last_10_blogs,user=user) 

@views.route("/home/get-car-models-prediction-page", methods=["POST"]) 
def get_car_models_for_prediction_page(): 
    return jsonify({"models":["Select Car Model"]}) 

@views.route("/home/get-price-prediction",methods=["POST"]) 
def get_car_price_prediction():
    try:
        make = request.form.get("select-company-price", "").strip().lower()
        model = request.form.get("select-model-price", "").strip().lower()
        year_str = request.form.get("year-price", "")
        kms_str = request.form.get("kms-driven-price", "")
        fuel = request.form.get("select-fuel-type-price", "").strip().capitalize()
        transmission = request.form.get("select-transmission-price", "").strip().lower()
        location = request.form.get("select-location-price", "").strip().lower()

        if not (make and model and year_str and kms_str and fuel and transmission and location):
            return "Please fill all fields"

        year = int(year_str)
        kms = float(kms_str)

        input_data = pd.DataFrame([{
            'make': make,
            'model': model,
            'year': year,
            'kms_driven': kms,
            'fuel_type': fuel,
            'transmission': transmission,
            'location': location
        }])

        model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scrapers', 'car_price_model.pkl')
        if not os.path.exists(model_path):
            return "Model not trained"

        with open(model_path, 'rb') as f:
            pipeline = pickle.load(f)

        pred_price = pipeline.predict(input_data)[0]
        return "{:.2f} Lakhs".format(pred_price)
    except Exception as e:
        print("Prediction Error:", e)
        return "Error predicting" 

@views.route("/home/get-car-models",methods=["POST"]) 
def get_car_models(): 
    return jsonify({"models": ["Select Car Model"]}) 

def assign_fallback_images(rows):
    import hashlib
    car_images_dir = os.path.join(os.path.dirname(__file__), 'static', 'car_images')
    available_images = []
    if os.path.exists(car_images_dir):
        available_images = [f for f in os.listdir(car_images_dir) if f.endswith('.jpg')]
        
    results = []
    for row in rows:
        res_dict = dict(row)
        img_key = 'imageurl' if 'imageurl' in res_dict else 'ImageURL'
        url_key = 'listingurl' if 'listingurl' in res_dict else 'ListingURL'
        
        if not res_dict.get(img_key) and available_images:
            h = hashlib.md5(res_dict.get(url_key, '').encode()).hexdigest()
            idx = int(h, 16) % len(available_images)
            res_dict[img_key] = f"/static/car_images/{available_images[idx]}"
        results.append(res_dict)
    return results

def query_merged_db(company, model, fuel_type, year, kms_driven, location, transmission='any'):
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scrapers', 'merged_car_listings.db')
    if not os.path.exists(db_path):
        return []
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        
        query = "SELECT * FROM listings WHERE 1=1"
        params = []
        
        if company and company.lower() != 'any':
            query += " AND LOWER(make) = ?"
            params.append(company.lower())
        if model:
            query += " AND LOWER(model) LIKE ?"
            params.append(f"%{model.lower()}%")
        if fuel_type and fuel_type.lower() != 'any':
            query += " AND LOWER(fueltype) = ?"
            params.append(fuel_type.lower())
        if year:
            query += " AND year >= ?"
            params.append(int(year))
        if kms_driven:
            query += " AND kilometersdriven <= ?"
            params.append(int(kms_driven))
        if location and location.lower() != 'any':
            query += " AND LOWER(city) = ?"
            params.append(location.lower())
        if transmission and transmission.lower() != 'any':
            if transmission.lower() == 'automatic':
                query += " AND LOWER(transmission) IN ('automatic', 'auto')"
            else:
                query += " AND LOWER(transmission) = ?"
                params.append(transmission.lower())
            
        query += " ORDER BY CASE WHEN imageurl != '' AND imageurl IS NOT NULL THEN 0 ELSE 1 END LIMIT 60"
        
        cur.execute(query, params)
        rv = cur.fetchall()
        cur.close()
        conn.close()
        
        return assign_fallback_images(rv)
    except sqlite3.Error as e:
        print(f"Database error in merged_car_listings.db: {e}")
        return []

@views.route("/api/cars", methods=['GET'])
def api_cars():
    company = request.args.get('company', 'any')
    model = request.args.get('model', '')
    fuel = request.args.get('fuel', 'any')
    year = request.args.get('year', '')
    kms = request.args.get('kms', '')
    location = request.args.get('location', 'any')
    transmission = request.args.get('transmission', 'any')
    
    # If any filter is provided, use query_merged_db
    if company != 'any' or model or fuel != 'any' or year or kms or location != 'any' or transmission != 'any':
        all_cars = query_merged_db(company, model, fuel, year, kms, location, transmission)
        return jsonify({"status": "success", "data": all_cars})
        
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scrapers', 'merged_car_listings.db')
    if not os.path.exists(db_path):
        return jsonify({"status": "success", "data": []})
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            WITH RankedCars AS (
                SELECT *, ROW_NUMBER() OVER(PARTITION BY city ORDER BY rowid) as rn
                FROM listings
            )
            SELECT carname as CarName, price as Price, year as Year, location as Location, imageurl as ImageURL, source as Source, kilometersdriven as KilometersDriven, fueltype as FuelType, listingurl as ListingURL 
            FROM RankedCars 
            WHERE rn <= 5
            ORDER BY rn, city
            LIMIT 30
        """)
        rv = cur.fetchall()
        cur.close()
        conn.close()
        all_cars = assign_fallback_images(rv)
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        all_cars = []
        
    return jsonify({"status": "success", "data": all_cars})

@views.route("/get-car-listings",methods=["POST"]) 
def get_car_listings(): 
    if request.method == "POST": 
        user_id = session.get('user_id') 
        user = Users.query.get(user_id) if user_id else None 
        
        car_company = request.form.get("select-company", "any") 
        car_model = request.form.get("select-model", "") 
        car_kms_driven = request.form.get("kms-driven", "") 
        car_location = request.form.get("select-location", "any").strip().lower() 
        car_fuel_type = request.form.get("select-fuel-type", "any").strip().lower() 
        car_year = request.form.get("year", "") 
        car_transmission = request.form.get("select-transmission", "any").strip().lower()
        
        all_cars = query_merged_db(car_company, car_model, car_fuel_type, car_year, car_kms_driven, car_location, car_transmission)
        
        spinny_data = [car for car in all_cars if car.get('source', '').lower() == 'spinny']
        cars24_data = [car for car in all_cars if car.get('source', '').lower() == 'cars24']
        olx_data = [car for car in all_cars if car.get('source', '').lower() == 'olx']
        
        return render_template("car_listings.html",spinny_data=spinny_data,olx_data=olx_data,cars24_data=cars24_data, user=user)

@views.route("/get-similar-car-listings",methods=["POST"]) 
def get_similar_car_listings(): 
    return get_car_listings()

