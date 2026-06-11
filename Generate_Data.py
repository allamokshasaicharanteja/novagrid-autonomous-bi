import os
import random
import csv
from datetime import datetime

DROP_ZONE = "."

# SCALED MATRIX: 100 Unique Enterprise Clients distributed across domains
COMPANIES = []
industries_pool = ["Biomedical", "Aerospace", "Technology"]
for i in range(1, 101):
    ind = random.choice(industries_pool)
    tax = f"{random.randint(10, 25)}%"
    if ind == "Biomedical":
        name = f"Stellar Bio-Pharma Labs Node_{i:03d}"
    elif ind == "Aerospace":
        name = f"Apex Orbital Defense Corp_{i:03d}"
    else:
        name = f"Vanguard Cloud Systems Inc_{i:03d}"
    COMPANIES.append({"name": name, "industry": ind, "tax": tax})

CLIENT_POOL = [
    "Moksha Alla", "Sunitha Alla", "Naveen Kumar", "Charan Reddy", "Teja Das", 
    "Ananya Rao Engine", "David Miller", "Sophia Chen", "Marcus Vance", "Elena Rostova"
]

CATEGORIES_BY_IND = {
    "Biomedical": [
        "Genomic Sequencing", "Clinical Reagents", "CRISPR Vectors", 
        "Neural Implants", "Bio-Informatics Compute", "Solar Inverter Arrays", 
        "Wind Turbine Blades", "Lithium Storage Storage Nodes", "Nano-Bot Ingress", "Molecular Mapping"
    ],
    "Aerospace": [
        "Avionics Telemetry", "Propulsion Shrouds", "Titanium Fasteners", 
        "Cryo-Valves", "Thermal Shielding", "Freight Route Node Optimize", 
        "Autonomous Drone Fleet", "Cold-Chain Fleet Sensors", "Telemetry Ingress Nodes", "Quantum Scanners"
    ],
    "Technology": [
        "SaaS Core Enterprise", "Quantum Node Compute", "API Ingress Traffic", 
        "Database Replication", "Edge CDN Bandwidth", "High-Frequency Arbitrage Engine", 
        "Risk Ledger Nodes", "Liquidity Pool Routing", "AI Compute Matrices", "Cyber Shield Layers"
    ]
}

COLUMN_VARIANTS = [
    ['Transaction_ID', 'Customer_Name', 'Product_Category', 'Quantity', 'Unit_Price'],
    ['tx_id', 'customer', 'category', 'qty', 'price'],
    ['Transaction ID', 'Client Name', 'Item Category', 'Volume', 'Cost Per Unit'],
    ['TX_ID', 'BUYER', 'PRODUCT_CATEGORY', 'UNITS', 'UNIT_PRICE']
]

def generate_massive_enterprise_ledger(total_rows=50000):
    company = random.choice(COMPANIES)
    industry = company["industry"]
    biz_name = company["name"]
    tax_rate = company["tax"]
    
    print(f"=======================================================")
    print(f"🚀 MASSIVE INGESTION PIPELINE: {biz_name.upper()}")
    print(f"=======================================================")
    print(f"[SCALE CONFIG]: Generating {total_rows} records...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sanitized_biz = biz_name.lower().replace(" ", "_").replace("_0", "")
    filename = f"ledger_stream_{sanitized_biz}_{timestamp}.csv"
    full_target_path = os.path.join(DROP_ZONE, filename)
    
    header_shift_offset = random.randint(4, 8)
    print(f"[LAYOUT]: Header Shift Delay Active -> Row [{header_shift_offset}]")
    
    with open(full_target_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        writer.writerow([biz_name])
        writer.writerow(["Industry Domain Profile", industry])
        writer.writerow(["Applied Operational Tax Statutory Provision", tax_rate])
        
        for _ in range(header_shift_offset - 3):
            writer.writerow([])
            
        selected_headers = random.choice(COLUMN_VARIANTS)
        writer.writerow(selected_headers)
        
        base_tx_id = random.randint(100000, 999999)
        
        print("⏳ Processing binary row blocks...")
        for idx in range(total_rows):
            tx_id = f"TXN-{base_tx_id + idx}"
            customer = random.choice(CLIENT_POOL)
            category = random.choice(CATEGORIES_BY_IND[industry])
            qty = random.randint(5, 120)
            unit_price = random.randint(15000, 450000)
            
            writer.writerow([tx_id, customer, category, qty, unit_price])
            
            if (idx + 1) % 15000 == 0:
                print(f"   ↳ Compiled {idx + 1} / {total_rows} records safely...")
                
    print(f"\n🟢 [SUCCESS]: Industrial-scale file dropped cleanly: {filename}")
    print(f"📊 Total Footprint Size: {os.path.getsize(full_target_path) / (1024 * 1024):.2f} MB\n")

if __name__ == "__main__":
    generate_massive_enterprise_ledger(50000)