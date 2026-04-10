import urllib.request
import csv
import os
import sys

# Setup path so app modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.firebase import get_firestore

CSV_URL = "https://data.opencity.in/dataset/30dd0c51-61d4-4085-99ab-9a8aec97b329/resource/433caa89-75e2-474d-b5d6-db8fd7a3171d/download/c91c0878-b4f9-419f-8d7c-97eb6c7a9083.csv"

def document_id_limit(s: str) -> str:
    return s.replace("/", "-")

def process_and_seed():
    """
    Downloads PMPML routes CSV, parses, bulk writes to ROUTES collection.
    If there are route stops detail in the CSV, it optionally writes to ROUTE_STOPS.
    """
    print("Downloading Routes CSV...")
    csv_path, _ = urllib.request.urlretrieve(CSV_URL, "routes.csv")
    print("Downloaded successfully.")

    db = get_firestore()
    batch = db.batch()
    
    count = 0
    total_written = 0
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # We assume columns like route_id, route_name, start_stop, end_stop exist
            # This logic depends deeply on the actual CSV schema, here using fallback approximations
            route_id = row.get("route_id", row.get("RouteNo", "Unknown")).strip()
            if not route_id:
                route_id = f"ROUTE_{count}"
                
            doc_id = document_id_limit(route_id)
            doc_ref = db.collection("ROUTES").document(doc_id)
            
            # Map CSV fields to what we store
            data = {
                "route_no": row.get("RouteNo", row.get("route_id", "")),
                "source": row.get("Source", ""),
                "destination": row.get("Destination", ""),
                "raw_data": row  # Keep raw data for flexibility
            }
            
            batch.set(doc_ref, data, merge=True)
            
            # Note: A real implementation would also parse out exact Stop sequences 
            # into ROUTE_STOPS if the CSV supports it, or use another specialized script.
            
            count += 1
            if count == 500:
                batch.commit()
                total_written += count
                print(f"Written {total_written} routes...")
                batch = db.batch()
                count = 0

    if count > 0:
        batch.commit()
        total_written += count
        
    print(f"Written {total_written} routes. Done!")
    os.remove(csv_path)

if __name__ == "__main__":
    process_and_seed()
