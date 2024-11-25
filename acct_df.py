import requests
import os
import pandas as pd
base_url = os.environ['BASE_URL']
auth_key = os.environ['AUTH_KEY']

accounts = {
      "WiTaxi Pay":"1000000004",
      "Bhadala":"3000000002",
      "Nedbank": "1000000003",
      "Associations": "3000000001",
      "SEL": "1000000002"
  }
acct_df = pd.DataFrame(columns=['Acct Name', 'Trans Type', 'Amount', 'Timestamp'])
for acct in accounts:
  url = f"{base_url}/network/express/account/{accounts[acct]}/transaction?currency=ZAR"
  trans = {"Wallet to Wallet Transfer": "p2p", "Wallet to Wallet Transfer - Ride": "Ride", "Notification via SMS": "SMS",
           "Topup via Online Card": "Card Topup", "Topup via Instant EFT": "EFT Topup",
           "Cashout via ATM": "Cashout ATM", "Cashout via Retail": "Cashout Retail", 
          'Payment via EFT Standard': 'Payment via EFT Standard', 'Payment via EFT Realtime': 'Payment via EFT Realtime'}
  payload = {}
  headers = {
    'Accept': '*/*',
    'Authorization': f'Bearer {auth_key}'
  }

  response = requests.request("GET", url, headers=headers, data=payload)
  data = response.json()['data']

  successful_trans = [i for i in data if i['state'] == "authorization_success"]

  new_rec = pd.DataFrame([[acct, trans[i['reference']], i['amount'], i['timestamp']] for i in successful_trans],
                        columns=['Acct Name', 'Trans Type', 'Amount', 'Timestamp'])
  acct_df = pd.concat([acct_df, new_rec], ignore_index=True)


acct_df['Timestamp'] = pd.to_datetime(acct_df['Timestamp'], errors='coerce')

acct_df = acct_df.assign(
        date=acct_df["Timestamp"].dt.date,
        time=acct_df["Timestamp"].dt.time
    )

acct_df.to_csv('Data/accts_data.csv', index=False)
