import urllib.request
import xml.etree.ElementTree as ET
import os
import sys
from google.cloud import firestore

# Setup path so app modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.firebase import get_firestore

KML_URL = "https://data.opencity.in/dataset/30dd0c51-61d4-4085-99ab-9a8aec97b329/resource/2c43a9a6-9a58-48dd-8891-e5f3dbe9120c/download/46c96db4-af62-4b84-a479-5a0279a8f44a.kml"

def parse_kml_and_seed():
    """
    Downloads PMPML bus stops KML, parse placemarks, bulk write to Firestore using batched writes of 500.
    """
    print("Downloading KML file...")
    kml_path, _ = urllib.request.urlretrieve(KML_URL, "stops.kml")
    print("Downloaded successfully.")

    tree = ET.parse(kml_path)
    root = tree.getroot()

    # KML parsing usually involves namespaces
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    stops = []
    
    # SimpleData mapping for opencity PMPML KML structure
    for placemark in root.findall('.//kml:Placemark', namespace):
        name_elem = placemark.find('kml:name', namespace)
        point_elem = placemark.find('.//kml:coordinates', namespace)
        
        name = name_elem.text if name_elem is not None else "Unknown"
        coords = point_elem.text.strip().split(',') if point_elem is not None else None
        
        if coords and len(coords) >= 2:
            lng = float(coords[0])
            lat = float(coords[1])
            
            # Use 'name' as a stop ID fallback, typically KML has a specific ExtendedData field for ID
            stop_id = name.replace(" ", "_").upper() 
            
            stops.append({
                "id": stop_id[:document_id_limit(stop_id)], # Ensure it fits length bounds if needed
                "name": name,
                "lat": lat,
                "lng": lng
            })

    print(f"Parsed {len(stops)} stops. Seeding Firestore via batched writes...")
    
    db = get_firestore()
    batch = db.batch()
    count = 0
    total_written = 0
    
    for stop in stops:
        doc_ref = db.collection("BUS_STOPS").document(stop["id"])
        batch.set(doc_ref, {
            "name": stop["name"],
            "lat": stop["lat"],
            "lng": stop["lng"]
        })
        count += 1
        
        if count == 500:
            batch.commit()
            total_written += count
            print(f"Written {total_written} stops...")
            batch = db.batch()
            count = 0
            
    if count > 0:
        batch.commit()
        total_written += count
        print(f"Written {total_written} stops. Done!")
        
    os.remove(kml_path)

def document_id_limit(s: str) -> str:
    # Quick fix for valid FS doc IDs, removing slashes which are invalid in FireStore doc IDs
    return s.replace("/", "-")

if __name__ == "__main__":
    parse_kml_and_seed()
