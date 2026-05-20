import sqlite3
import requests
from bs4 import BeautifulSoup
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_and_save(rowid, url, headers):
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            meta_img = soup.find('meta', property='og:image')
            if meta_img and meta_img.get('content'):
                img_url = meta_img['content']
                img_res = requests.get(img_url, headers=headers, stream=True, timeout=5)
                if img_res.status_code == 200:
                    filename = f"{uuid.uuid4().hex}.jpg"
                    filepath = os.path.join('website', 'static', 'car_images', filename)
                    with open(filepath, 'wb') as f:
                        for chunk in img_res.iter_content(4096):
                            f.write(chunk)
                    return rowid, f"/static/car_images/{filename}"
    except Exception:
        pass
    return rowid, None

def download_images():
    db_path = os.path.join('scrapers', 'merged_car_listings.db')
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT rowid, listingurl FROM listings WHERE imageurl = '' OR imageurl IS NULL")
    cars = cur.fetchall()
    
    print(f"Found {len(cars)} cars without images. Starting fast download...")
    os.makedirs(os.path.join('website', 'static', 'car_images'), exist_ok=True)
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # Process in batches to avoid locking the db
    batch_size = 50
    updated_count = 0
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(fetch_and_save, row[0], row[1], headers): row for row in cars}
        
        batch_updates = []
        for future in as_completed(futures):
            rowid, db_img_url = future.result()
            if db_img_url:
                batch_updates.append((db_img_url, rowid))
                updated_count += 1
                
            if len(batch_updates) >= batch_size:
                cur.executemany("UPDATE listings SET imageurl = ? WHERE rowid = ?", batch_updates)
                conn.commit()
                print(f"Committed {len(batch_updates)} updates. Total: {updated_count}")
                batch_updates = []

        if batch_updates:
            cur.executemany("UPDATE listings SET imageurl = ? WHERE rowid = ?", batch_updates)
            conn.commit()
            print(f"Committed final {len(batch_updates)} updates.")

    conn.close()
    print(f"Finished updating {updated_count} total images.")

if __name__ == '__main__':
    download_images()
