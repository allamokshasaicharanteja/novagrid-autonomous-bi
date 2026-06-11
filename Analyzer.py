import os
import sys  
import shutil
import pandas as pd
import numpy as np
import json
import base64
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Template
from dotenv import load_dotenv

# Initialize the secure environment configuration loader
load_dotenv()

# =======================================================
# 1 & 2. DYNAMIC INPUT RESOLUTION & SELF-HEALING INGESTION
# =======================================================
if len(sys.argv) > 1:
    target_csv_file = sys.argv[1]
    print(f"Processing targeted external source stream: {target_csv_file}")
else:
    target_csv_file = 'sales_data.csv'
    print(f"No argument detected. Falling back to local default asset: {target_csv_file}")

if not os.path.exists(target_csv_file):
    print(f"CRITICAL ERROR: Selected target file data path does not exist: {target_csv_file}")
    sys.exit(1)

print("Scanning file structure for dynamic layout discovery...")

column_dictionary = {
    'Transaction_ID': ['transaction id', 'tx_id', 'id', 'transactionid', 'tx id'],
    'Customer_Name': ['customer', 'client name', 'client', 'customername', 'buyer'],
    'Product_Category': ['category', 'item category', 'product group', 'product_category'],
    'Quantity': ['qty', 'volume', 'units', 'number of items'],
    'Unit_Price': ['price', 'cost per unit', 'rate', 'unit price', 'unit_price']
}

# Step A: Scan the first 15 lines as raw text to locate the headers dynamically
header_row_index = None
business_name = "Standard Enterprise Client" # Fail-safe default
tax_rate = 0.18                              # Fail-safe default (18%)
industry_tag = "Technology"                  # Fail-safe default

print("Running deep text-stream analysis for header localization...")
with open(target_csv_file, 'r', encoding='utf-8', errors='ignore') as f:
    for idx in range(15):
        line = f.readline()
        if not line:
            break
            
        line_lower = line.lower()
        
        matched_keywords = 0
        for standard_name, variations in column_dictionary.items():
            if standard_name.lower() in line_lower or any(v in line_lower for v in variations):
                matched_keywords += 1
                
        if matched_keywords >= 3:
            header_row_index = idx
            break

# Step B: Safe metadata extraction if headers are shifted down
if header_row_index is None:
    print("CRITICAL ERROR: Could not locate a valid data schema header matrix inside the file.")
    sys.exit(1)

print(f"[LAYOUT DISCOVERY]: Data headers successfully localized at Row Index [{header_row_index}]")

if header_row_index > 0:
    try:
        # 🚀 FIX: Load rows as raw strings explicitly to completely safeguard complex metadata configurations
        meta_df = pd.read_csv(target_csv_file, nrows=header_row_index, header=None, on_bad_lines='skip', dtype=str)
        if not meta_df.empty:
            # Row 1 (Index 0) is always the Business Name
            business_name = str(meta_df.iloc[0, 0]).strip()
            if pd.isna(business_name) or business_name == "" or business_name.lower() == "nan":
                business_name = "Standard Enterprise Client"
            
            # 🚀 FIX BUG 1: Case-insensitive, robust partial-string scanner node
            for r_idx in range(len(meta_df)):
                for c_idx in range(len(meta_df.columns) - 1):
                    key_cell = str(meta_df.iloc[r_idx, c_idx]).strip().lower()
                    val_cell = str(meta_df.iloc[r_idx, c_idx + 1]).strip()
                    
                    # Target partial words "industry" or "domain" completely case-insensitively
                    if "industry" in key_cell or "domain" in key_cell:
                        if val_cell and val_cell.lower() != "nan":
                            industry_tag = val_cell
                    
                    # Intercept operational tax keys smoothly
                    if "tax" in key_cell or "%" in val_cell:
                        val_str = val_cell.replace('%', '').strip()
                        if val_str.replace('.', '', 1).isdigit():
                            possible_tax = float(val_str)
                            tax_rate = possible_tax / 100 if possible_tax > 1 else possible_tax
    except Exception as e:
        print(f"[WARNING]: Metadata extraction channel bypassed: {str(e)}. Deploying fail-safe profiles.")

print(f"[PROFILE MATCHED]: Client Identity: {business_name} | Domain: {industry_tag} | Applied Tax: {int(tax_rate*100)}%")

# 🌌 COSMOS REVERT CORE: Universal theme mapping to the ultra-premium dark cosmic blue layout palette
theme_color = "#3b82f6"  
chart_palette = json.dumps(['#3b82f6', '#60a5fa', '#2563eb', '#1d4ed8', '#1e40af', '#475569'])

folder_name = str(business_name).replace(" ", "_")
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Step C: Parse the entire file safely using the dynamically discovered header index
df = pd.read_csv(target_csv_file, skiprows=header_row_index)
df = df.dropna(how='all')

rename_rules = {}
for standard_name, variations in column_dictionary.items():
    for col in df.columns:
        if col.lower().strip() in variations or col.lower().strip() == standard_name.lower():
            rename_rules[col] = standard_name

df = df.rename(columns=rename_rules)

required_columns = ['Transaction_ID', 'Customer_Name', 'Product_Category', 'Quantity', 'Unit_Price']
if not all(col in df.columns for col in required_columns):
    print("CRITICAL ERROR: Parsed dataset does not align with core execution criteria.")
    sys.exit(1)

df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce')
df['Unit_Price'] = pd.to_numeric(df['Unit_Price'], errors='coerce')
df = df.dropna(subset=['Quantity', 'Unit_Price', 'Customer_Name'])
df = df.reset_index(drop=True)

df['Total_Cost'] = df['Quantity'] * df['Unit_Price']


# =======================================================
# 3. COMPUTE FINANCIAL METRICS & CLIENT CONCENTRATION
# =======================================================
total_revenue = int(df['Total_Cost'].sum())
total_tax = int(np.round(total_revenue * tax_rate))

customer_spending = df.groupby('Customer_Name')['Total_Cost'].sum().sort_values(ascending=False)
top_customer = customer_spending.idxmax()
top_customer_amount = int(customer_spending.max())

client_shares = (customer_spending / total_revenue) * 100
cumulative_shares = client_shares.cumsum()

top_tier_clients = customer_spending[cumulative_shares <= 73]
if top_tier_clients.empty: 
    top_tier_clients = customer_spending.head(3)

top_clients_html = "".join([f"<li><strong>{name}</strong>: Rs. {amt:,} ({client_shares[name]:.1f}%)</li>" for name, amt in top_tier_clients.items()])

summary_data = {
    'Metric': ['Company Name', 'Total Revenue', f'Total Tax ({int(tax_rate*100)}%)', 'Primary Key Client', 'Top Core Clients Count'],
    'Value': [business_name, f"Rs. {total_revenue:,}", f"Rs. {total_tax:,}", top_customer, f"{len(top_tier_clients)} Clients drive ~70% of rev"]
}
summary_df = pd.DataFrame(summary_data)

# =======================================================
# 4. EXPORT DATA ARTIFACTS TO EXCEL (WITH AUTO-FIT)
# =======================================================
print("Exporting auto-fitted data artifacts to Excel...")
excel_file_path = os.path.join(folder_name, 'Business_Summary.xlsx')

with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
    df.to_excel(writer, sheet_name='Detailed Item Breakdown', index=False)
    
    for sheet_name in writer.sheets:
        worksheet = writer.sheets[sheet_name]
        for col in worksheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

# =======================================================
# 5. JAVASCRIPT OBJECT RE-COMPILATION ENGINE
# =======================================================
print("Compiling data vectors into native JSON arrays...")

full_category_sales = df.groupby('Product_Category')['Total_Cost'].sum().sort_values(ascending=False)
category_sales = full_category_sales.head(6) 

js_category_labels = json.dumps(list(category_sales.index))
js_category_data = json.dumps([int(x) for x in category_sales.values])

top_5_clients = customer_spending.head(5)
pie_labels = list(top_5_clients.index)
pie_data = [int(x) for x in top_5_clients.values]

remaining_clients_total = customer_spending.sum() - top_5_clients.sum()
if remaining_clients_total > 0:
    pie_labels.append('Other Accounts')
    pie_data.append(int(remaining_clients_total))

js_client_labels = json.dumps(pie_labels)
js_client_data = json.dumps(pie_data)

# =======================================================
# 6. JINJA2 TEMPLATE BINDING & HYBRID LAYOUT GENERATION
# =======================================================
print("Binding analytic vectors to HTML dashboard runtime...")

with open('report_template.html', 'r', encoding='utf-8') as file:
    template_content = file.read()

template = Template(template_content)

context = {
    "business_name": business_name,      
    "industry": industry_tag,            
    "theme_color": theme_color,          
    "chart_palette": chart_palette,      
    "total_revenue": f"{total_revenue:,}",
    "total_tax": f"{total_tax:,}",
    "top_customer": f"{top_customer} (Spent Rs. {top_customer_amount:,})",
    "top_clients_html": top_clients_html,
    "js_category_labels": js_category_labels,
    "js_category_data": js_category_data,
    "js_client_labels": js_client_labels,
    "js_client_data": js_client_data
}

final_html_output = template.render(context)
output_html_path = os.path.join(folder_name, 'Executive_Report.html')
with open(output_html_path, 'w', encoding='utf-8') as file:
    file.write(final_html_output)

# =======================================================
# 7. BROWSER-GRADE HD PDF GENERATION ENGINE & AUTO-QR
# =======================================================
print("Launching headless layout browser engine...")
from selenium.webdriver import Edge
from selenium.webdriver.edge.options import Options
import qrcode 
import requests  

edge_options = Options()
edge_options.add_argument("--headless")
edge_options.add_argument("--disable-gpu")
edge_options.add_argument("--run-all-javascript")
edge_options.add_argument("--force-device-scale-factor=2") 

driver = Edge(options=edge_options)
output_pdf_path = os.path.join(folder_name, 'Executive_Report.pdf')

try:
    abs_html_path = os.path.abspath(output_html_path)
    driver.get(f"file:///{abs_html_path}")
    
    print("Waiting for dynamic chart graphics and page layout bindings to completely stabilize...")
    time.sleep(3.5) 
    
    print("Executing high-definition layout snapshot...")
    # 🚀 FIX BUG 2: Professional-grade publication template vectors for A4 PDF page scaling
    print_options = {
        'landscape': False,
        'displayHeaderFooter': True,      
        'printBackground': True,           
        'preferCSSPageSize': True,         
        'scale': 0.95,                     
        'paperWidth': 8.27,           
        'paperHeight': 11.69,         
        'marginTop': 0.7,                 
        'marginBottom': 0.7,              
        'marginLeft': 0.4,
        'marginRight': 0.4,
        
        'headerTemplate': f"""
            <div style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 7.5pt; width: 100%; margin-left: 0.4in; margin-right: 0.4in; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; display: flex; justify-content: space-between; color: #64748b;">
                <span style="letter-spacing: 0.5px; font-weight: 500;">ENTERPRISE REAL-TIME TRANSACTION DATA AUDIT</span>
                <span style="font-weight: 600; color: #0f172a;">{business_name}</span>
            </div>
        """,
        
        'footerTemplate': """
            <div style="font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 7.5pt; width: 100%; margin-left: 0.4in; margin-right: 0.4in; border-top: 1px solid #e2e8f0; padding-top: 6px; display: flex; justify-content: space-between; color: #64748b;">
                <span>CONFIDENTIAL &bull; SYSTEM PROVISIONED INGRESS FLOW</span>
                <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
            </div>
        """
    }
    
    result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
    pdf_bytes = base64.b64decode(result['data'])
    
    with open(output_pdf_path, 'wb') as f:
        f.write(pdf_bytes)
    print("[SUCCESS] HD PDF Report compiled successfully.")

    # ==============================================================================
    # 🦾 AUTONOMOUS INGRESS NETWORK DISCOVERY BLOCK (ZERO-TOUCH LINK EXTRACTION)
    # ==============================================================================
    print("\n⚡ [AUTONOMOUS INGRESS NODE]: Querying internal tunnel routing protocols...")
    live_public_url = None
    
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        if response.status_code == 200:
            tunnel_data = response.json()
            for tunnel in tunnel_data.get('tunnels', []):
                if tunnel.get('proto') == 'https':
                    live_public_url = tunnel.get('public_url', '').strip()
                    break
    except Exception as e:
        print(f"⚠️  Internal api channel standby: {str(e)}")

    if not live_public_url:
        print("🔗 [FALLBACK]: Internal tunnel endpoint offline. Switching to manual input tracking...")
        live_public_url = input("🌐 Paste Active Public Link manually: ").strip()
    else:
        print(f"🎯 [AUTO DISCOVERY SUCCESS]: Intercepted Active Endpoint -> {live_public_url}")
    
    if live_public_url and len(live_public_url.strip()) > 0:
        clean_base_url = live_public_url.strip().rstrip('/')
        company_routing_url = f"{clean_base_url}/{folder_name}/Executive_Report.html"
        
        print(f"🔗 [ROUTING NODE]: Building true multi-tenant pointer vector:")
        print(f"    ↳ {company_routing_url}")
        
        print("Compiling cryptographic link matrix into high-contrast image matrix...")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H, 
            box_size=10,
            border=4,
        )
        qr.add_data(company_routing_url) 
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="#0f172a", back_color="#ffffff") 
        qr_output_path = os.path.join(folder_name, 'Live_Dashboard_QR.png')
        qr_img.save(qr_output_path)
        
        print(f"🎯 [QR SUCCESS]: Live navigation asset compiled successfully at: /{qr_output_path}")
        
        live_public_url = company_routing_url
    else:
        print("⚠️  [QR SKIPPED]: Empty string entry mapped. Bypassing asset generation.")

except Exception as e:
    print(f"[ERROR] Browser layout or QR engine failed: {str(e)}")
finally:
    driver.quit()

# =======================================================
# 8. AUTOMATED SECURE SMTP MAIL DISPATCHER
# =======================================================
print("Initiating automated SMTP mail dispatcher...")

sender_email = os.getenv("EMAIL_SENDER")
sender_password = os.getenv("EMAIL_PASSWORD")
receiver_email = os.getenv("EMAIL_RECEIVER")

if not all([sender_email, sender_password, receiver_email]):
    print("⚠️  [MAIL SKIPPED]: SMTP credentials missing from environment file.")
else:
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = f"📊 Executive Financial Performance Audit: {business_name}"

        body = f"""Hello Team,

Please find attached the automatically generated financial intelligence packages for {business_name}.

🚀 LIVE INTERACTIVE PORTAL: 
You can access your live, real-time executive dashboard anywhere in the world via this secure public endpoint:
{live_public_url}

Included Artifacts:
1. Executive_Report.pdf - Premium corporate dashboard mapping revenue vertices and concentration risks.
2. Business_Summary.xlsx - Micro-level accounting audit spreadsheet containing structural breakdowns.

Best Regards,
Enterprise Data Automation Pipeline Hub
"""
        msg.attach(MIMEText(body, 'plain'))

        attachments = [output_pdf_path, excel_file_path]

        for filepath in attachments:
            filename = os.path.basename(filepath)
            with open(filepath, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {filename}",
                )
                msg.attach(part)

        print("Establishing secure SSL link to mail servers...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())

        print("[MAIL SUCCESS]: Enterprise analytics package delivered to destination inbox.")

    except Exception as e:
        print(f"[MAIL FAULT]: Dispatch system failed to deliver package: {str(e)}")

# =======================================================
# 9. LIVE DATA HOUSEKEEPING & NOTIFICATION ALERTS
# =======================================================
import requests 

def send_live_pipeline_notification(company_name, total_revenue, client_count, file_name):
    webhook_url = os.getenv("DISCORD_WEBHOOK", "YOUR_DISCORD_WEBHOOK_URL")
    
    if "YOUR_DISCORD_WEBHOOK_URL" in webhook_url or not webhook_url.startswith("http"):
        print("⚠️  [NOTIFICATION SKIPPED]: Active Discord Webhook link not configured.")
        return

    payload = {
        "username": "Pipeline Radar Bot",
        "avatar_url": "https://i.imgur.com/4M34wCY.png",
        "embeds": [{
            "title": "⚡ ENTERPRISE DATA STREAM PROCESSED SUCCESSFULLY",
            "color": 2333934,  
            "fields": [
                {"name": "🏢 Client Identity", "value": f"**{company_name}**", "inline": True},
                {"name": "📊 Total Gross Revenue", "value": f"**{total_revenue}**", "inline": True},
                {"name": "📥 Source Ingress Asset", "value": f"`{file_name}`", "inline": False},
                {"name": "💡 Intelligence Insight", "value": f"Top {client_count} core accounts successfully mapped inside custom repository.", "inline": False}
            ],
            "footer": {"text": "Autonomous Ingestion Hub • Live Node Update"},
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }]
    }

    try:
        response = requests.post(webhook_url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code == 204:
            print("📱 [LIVE ALERT]: Pipeline completion broadcast sent straight to notification network!")
        else:
            print(f"[NOTIFY FAILED]: Server responded with code {response.status_code}")
    except Exception as e:
        print(f"[NOTIFY FAULT]: Communication line down: {str(e)}")


if len(sys.argv) > 1:
    print("\nExecuting autonomous house-keeping file operations...")
    try:
        raw_filename = os.path.basename(target_csv_file)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        archive_name = f"{timestamp}_{raw_filename}"
        
        archive_folder = "02_processed_archive"
        if not os.path.exists(archive_folder):
            os.makedirs(archive_folder)
            
        archive_dest_path = os.path.join(archive_folder, archive_name)
        
        shutil.move(target_csv_file, archive_dest_path)
        print(f"[ARCHIVE SUCCESS]: Raw source file cataloged to: /{archive_dest_path}")
        
        send_live_pipeline_notification(business_name, f"Rs. {total_revenue:,}", len(top_tier_clients), raw_filename)
        
        print(f"\n[SUCCESS] MULTI-PIPELINE CYCLE COMPLETE FOR: {business_name}")
    except Exception as e:
        print(f"[WARNING] Housekeeping failed to clean file stream: {str(e)}")
else:
    print(f"\n[SUCCESS] MANUAL RUN TERMINATED CLEANLY FOR: {business_name}")

try:
    shutil.copy(output_html_path, "index.html")
    print("\n🟢 [SERVER NODE]: Root index.html successfully synchronized with fresh enterprise data.")
except Exception as e:
    print(f"\n⚠️  [SERVER NODE WARNING]: Could not duplicate layout to root space: {str(e)}")