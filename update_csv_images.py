import os
import glob
import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_image_url(link):
    if not link or pd.isna(link):
        return link, None
    try:
        res = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            meta_img = soup.find('meta', property='og:image')
            if meta_img and meta_img.get('content'):
                return link, meta_img['content']
    except Exception:
        pass
    return link, None

def update_csv_files():
    base_dir = 'scrapers'
    csv_files = glob.glob(os.path.join(base_dir, "cars24_*.csv")) + glob.glob(os.path.join(base_dir, "spinny_*.csv"))
    
    for file in csv_files:
        print(f"Processing {file}...")
        df = pd.read_csv(file)
        
        if 'link' not in df.columns:
            continue
            
        if 'imageurl' not in df.columns:
            df['imageurl'] = None
            
        # Filter rows that need fetching
        needs_fetch = df[df['imageurl'].isna() | (df['imageurl'] == '')]
        if needs_fetch.empty:
            continue
            
        links_to_fetch = needs_fetch['link'].unique()
        
        print(f"  Fetching {len(links_to_fetch)} image links for {os.path.basename(file)}...")
        
        results = {}
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(fetch_image_url, link): link for link in links_to_fetch}
            for future in as_completed(futures):
                link, img_url = future.result()
                if img_url:
                    results[link] = img_url
                    
        # Update dataframe
        for link, img_url in results.items():
            df.loc[df['link'] == link, 'imageurl'] = img_url
            
        # Save back to CSV
        df.to_csv(file, index=False)
        print(f"  Saved {len(results)} image URLs to {file}.")

if __name__ == '__main__':
    update_csv_files()
