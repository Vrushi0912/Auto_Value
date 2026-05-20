import sqlite3
import requests
from bs4 import BeautifulSoup
import os
import uuid

def download_images():
    db_path = os.path.join('scrapers', 'merged_car_listings.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Select cars that don't have an image
    cur.execute("SELECT rowid, listingurl, source FROM listings WHERE imageurl = '' OR imageurl IS NULL LIMIT 200")
    cars = cur.fetchall()
    
    print(f"Found {len(cars)} cars without images.")
    
    os.makedirs(os.path.join('website', 'static', 'car_images'), exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    updated_count = 0
    for rowid, url, source in cars:
        if not url: continue
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                meta_img = soup.find('meta', property='og:image')
                if meta_img and meta_img.get('content'):
                    img_url = meta_img['content']
                    
                    # Download image
                    img_res = requests.get(img_url, headers=headers, stream=True, timeout=5)
                    if img_res.status_code == 200:
                        filename = f"{uuid.uuid4().hex}.jpg"
                        filepath = os.path.join('website', 'static', 'car_images', filename)
                        with open(filepath, 'wb') as f:
                            for chunk in img_res.iter_content(1024):
                                f.write(chunk)
                                
                        db_img_url = f"/static/car_images/{filename}"
                        cur.execute("UPDATE listings SET imageurl = ? WHERE rowid = ?", (db_img_url, rowid))
                        conn.commit()
                        updated_count += 1
                        print(f"Updated {rowid}: {db_img_url}")
        except Exception as e:
            print(f"Error for {url}: {e}")
            
    conn.close()
    print(f"Finished updating {updated_count} images.")

if __name__ == '__main__':
    download_images()
