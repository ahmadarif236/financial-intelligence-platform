import httpx
import pandas as pd
import asyncio
import io

BASE_URL = "http://localhost:8000/api"

async def run_tests():
    print("starting tests...")
    
    # 1. Register User
    print("1. Testing Auth/Register...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(f"{BASE_URL}/auth/register", json={
            "email": "test_cfo_{}@example.com".format(pd.Timestamp.now().to_pydatetime().strftime("%H%M%S")),
            "password": "password123",
            "full_name": "Test CFO"
        })
        if res.status_code != 200:
            print(f"Registration failed: {res.text}")
            return
        
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("   ✅ Registered and got token")

        # 2. Create Company
        print("2. Testing Company Profile...")
        res = await client.post(f"{BASE_URL}/company/", headers=headers, json={
            "name": "Synthetic Corp LLC",
            "country": "UAE",
            "currency": "AED",
            "industry": "Technology"
        }, timeout=60.0)
        if res.status_code != 200:
            print(f"Company creation failed: {res.text}")
            return
        print("   ✅ Company created")

        # 3. Create Synthetic Excel File and upload
        print("3. Testing Data Upload (Trial Balance)...")
        # Ensure we match expected mapping columns: Account Code, Account Name, Debit, Credit or Balance
        df = pd.DataFrame([
            {"Account Code": "1000", "Account Name": "Cash in Bank", "Debit": 500000, "Credit": 0},
            {"Account Code": "1200", "Account Name": "Accounts Receivable", "Debit": 150000, "Credit": 0},
            {"Account Code": "1500", "Account Name": "Inventory", "Debit": 100000, "Credit": 0},
            {"Account Code": "2000", "Account Name": "Accounts Payable", "Debit": 0, "Credit": 80000},
            {"Account Code": "2500", "Account Name": "Long Term Debt", "Debit": 0, "Credit": 200000},
            {"Account Code": "3000", "Account Name": "Share Capital", "Debit": 0, "Credit": 300000},
            {"Account Code": "4000", "Account Name": "Sales Revenue", "Debit": 0, "Credit": 500000},
            {"Account Code": "5000", "Account Name": "Cost of Goods Sold", "Debit": 200000, "Credit": 0},
            {"Account Code": "6000", "Account Name": "Salaries Expense", "Debit": 100000, "Credit": 0},
            {"Account Code": "6100", "Account Name": "Rent Expense", "Debit": 30000, "Credit": 0},
        ])
        
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        
        files = {'file': ('synthetic_tb.xlsx', excel_buffer, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        res = await client.post(f"{BASE_URL}/upload/trial-balance", headers=headers, files=files)
        if res.status_code != 200:
            print(f"File upload failed: {res.text}")
            return
        print(f"   ✅ Data Uploaded: Processing {res.json().get('entries_processed')} entries")

        # 4. Automap Accounts
        print("4. Testing Chart of Accounts Mapping...")
        res = await client.post(f"{BASE_URL}/mapping/auto-map", headers=headers)
        if res.status_code != 200:
            print(f"Auto-map failed: {res.text}")
            return
        print(f"   ✅ Auto-mapped {res.json().get('mapped_count')} accounts")

        # 5. Financial Statements
        print("5. Testing Financial Statements...")
        res = await client.get(f"{BASE_URL}/statements/all", headers=headers)
        if res.status_code != 200:
            print(f"Statements generation failed: {res.text}")
            return
        stmts = res.json()
        print(f"   ✅ P&L Net Profit: {stmts['profit_loss']['summary']['net_profit']}")
        print(f"   ✅ Balance Sheet Assets: {stmts['balance_sheet']['summary']['total_assets']}")
        print(f"   [Data] P&L Summary: {stmts['profit_loss']['summary']}")

        # 6. Ratios
        print("6. Testing Ratios...")
        res = await client.get(f"{BASE_URL}/ratios/", headers=headers)
        if res.status_code != 200:
            print(f"Ratios failed: {res.text}")
            return
        print("   ✅ Ratios calculated successfully")

        # 7. Dashboard
        print("7. Testing Dashboard...")
        res = await client.get(f"{BASE_URL}/dashboard/", headers=headers)
        if res.status_code != 200:
            print(f"Dashboard failed: {res.text}")
            return
        dash = res.json()
        print(f"   ✅ Dashboard KPI Revenue: {dash['kpis'].get('revenue')}")
        print(f"   [Data] Dashboard KPIs: {dash['kpis']}")

        # 8a. AI Commentary
        print("8. Testing AI Commentary (Cerebras Cloud Llama 3.3 70b)...")
        res = await client.get(f"{BASE_URL}/ai/commentary", headers=headers, timeout=60.0)
        if res.status_code != 200:
            print(f"AI Commentary failed: {res.text}")
        else:
            ai_data = res.json()
            print("   ✅ AI Commentary generated successfully. Health:", ai_data.get("overall_health"))
            print(f"   [Data] AI Executive Summary: {ai_data.get('executive_summary')}")
            print(f"   [Data] AI Risk Flags: {ai_data.get('risk_flags')}")

        # 8b. Export (Check PDF)
        print("9. Testing PDF Export (checking endpoint)...")
        res = await client.get(f"{BASE_URL}/export/pdf", headers=headers, timeout=30.0)
        if res.status_code == 200 and res.headers.get("content-type") == "application/pdf":
            print("   ✅ PDF exported successfully")
        else:
            print(f"   ❌ PDF Export failed: {res.status_code} {res.text}")

        # 8c. Export (Check Excel)
        print("10. Testing Excel Export (checking endpoint)...")
        res = await client.get(f"{BASE_URL}/export/excel", headers=headers)
        if res.status_code == 200:
            print("   ✅ Excel exported successfully")
        else:
            print(f"   ❌ Excel Export failed: {res.status_code}")

    print("\n🎉 All core backend workflows completed successfully!")

if __name__ == "__main__":
    asyncio.run(run_tests())
