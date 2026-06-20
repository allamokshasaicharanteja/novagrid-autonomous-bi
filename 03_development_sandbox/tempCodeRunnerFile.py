import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from jinja2 import Template
from xhtml2pdf import pisa

# =======================================================
# 1. DYNAMIC CONFIGURATION READING
# =======================================================
print("Reading business profile metrics from CSV source...")

config_df = pd.read_csv('sales_data.csv', nrows=1)
business_name = config_df['Company_Name'].iloc[0]
report_title = config_df['Report_Type'].iloc[0]
tax_rate = float(config_df['Tax_Rate_Percent'].iloc[0]) / 100

folder_name = business_name.replace(" ", "_")
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# =======================================================
# 2. LOAD & PROCESS DATA ROWS (WITH SELF-HEALING SCHEMAS)
# =======================================================
df = pd.read_csv('sales_data.csv', skiprows=3)

print(f"\n[Data Layer] Raw Columns Found in CSV: {list(df.columns)}")

# Define our synonym dictionary
column_dictionary = {
    'Transaction_ID': ['transaction id', 'tx_id', 'id', 'transactionid', 'tx id'],
    'Customer_Name': ['customer', 'client name', 'client', 'customername', 'buyer'],
    'Product_Category': ['category', 'item category', 'product group', 'product_category'],
    'Quantity': ['qty', 'volume', 'units', 'number of items'],
    'Unit_Price': ['price', 'cost per unit', 'rate', 'unit price', 'unit_price']
}

rename_rules = {}

# Match variations to standard target names
for standard_name, variations in column_dictionary.items():
    for col in df.columns:
        if col.lower().strip() in variations or col.lower().strip() == standard_name.lower():
            rename_rules[col] = standard_name

# Apply the self-healing layout map
df = df.rename(columns=rename_rules)
print(f"[Data Layer] Post-Cleaning Standardized Columns: {list(df.columns)}")

# Validation Check
required_columns = ['Transaction_ID', 'Customer_Name', 'Product_Category', 'Quantity', 'Unit_Price']
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    print(f"\n❌ CRITICAL ERROR: The uploaded CSV file is missing necessary data fields: {missing_columns}")
    print("Execution halted safely.")
    exit()
else:
    print("✅ Schema verification complete. No missing dimensions.")

# Run math safely
df['Total_Cost'] = df['Quantity'] * df['Unit_Price']

# 3. COMPUTE FINANCIAL METRICS
total_revenue = int(df['Total_Cost'].sum())
total_tax = int(np.round(total_revenue * tax_rate))

customer_spending = df.groupby('Customer_Name')['Total_Cost'].sum()
top_customer = customer_spending.idxmax()
top_customer_amount = int(customer_spending.max())

summary_data = {
    'Metric': ['Company Profile Name', 'Report Type Horizon', 'Total Revenue', f'Total Tax Collected ({int(tax_rate*100)}%)', 'Top Customer Name'],
    'Value': [business_name, report_title, f"Rs. {total_revenue:,}", f"Rs. {total_tax:,}", f"{top_customer} (Rs. {top_customer_amount:,})"]
}
summary_df = pd.DataFrame(summary_data)

# 4. EXPORT DATA ARTIFACTS TO EXCEL
excel_file_path = os.path.join(folder_name, 'Business_Summary.xlsx')
with pd.ExcelWriter(excel_file_path) as writer:
    summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
    df.to_excel(writer, sheet_name='Detailed Item Breakdown', index=False)


# 5. STAGE 2 - VISUALIZATION ENGINE
print(f"Generating visual analytics charts for {business_name}...")
category_sales = df.groupby('Product_Category')['Total_Cost'].sum().sort_values(ascending=False)

plt.figure(figsize=(8, 5))
colors = ['#2b5c8f', '#4682b4', '#6baed6', '#9ecae1', '#c6dbef']
category_sales.plot(kind='bar', color=colors, edgecolor='black', zorder=2)

plt.title(f'Revenue Analysis - {business_name}', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Product Category', fontsize=11, labelpad=10)
plt.ylabel('Total Revenue (in Rs.)', fontsize=11, labelpad=10)
plt.grid(axis='y', linestyle='--', alpha=0.7, zorder=1)
plt.xticks(rotation=15)
plt.tight_layout()

chart_image_name = 'category_sales.png'
chart_image_path = os.path.join(folder_name, chart_image_name)
plt.savefig(chart_image_path, dpi=300)
plt.close()

# =======================================================
# 6. STAGE 3 & 4 - JINJA2 TEMPLATE BINDING & RE-RENDERING
# =======================================================
print("Compiling dynamic layout matrices...")

with open('report_template.html', 'r') as file:
    template_content = file.read()

template = Template(template_content)
absolute_chart_path = os.path.abspath(chart_image_path)

context = {
    "business_name": business_name,
    "total_revenue": f"{total_revenue:,}",
    "total_tax": f"{total_tax:,}",
    "top_customer": f"{top_customer} (Spent Rs. {top_customer_amount:,})",
    "chart_path": absolute_chart_path
}

final_html_output = template.render(context)

output_html_path = os.path.join(folder_name, 'Executive_Report.html')
with open(output_html_path, 'w') as file:
    file.write(final_html_output)

# =======================================================
# 7. FINAL STAGE: PDF GENERATION ENGINE
# =======================================================
output_pdf_path = os.path.join(folder_name, 'Executive_Report.pdf')

with open(output_html_path, 'r') as html_file:
    html_content = html_file.read()

with open(output_pdf_path, 'w+b') as pdf_file:
    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

if not pisa_status.err:
    print(f"\n🏆 PIPELINE RUN COMPLETE FOR: {business_name}")
    print(f"📁 Check your new generated project folder: /{folder_name}")
else:
    print("X Process Error.")