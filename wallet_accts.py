import requests
import pandas as pd
# import streamlit as st
from datetime import datetime
from time import sleep
import os
# import streamlit_shadcn_ui as ui


base_url = os.environ['BASE_URL']
auth_key = os.environ['AUTH_KEY']

payload = {}
headers = {
  'Accept': '*/*',
  'Authorization': f'Bearer {auth_key}'
}
# Getting account Info
acct_request = f"{base_url}/network/express/account"
acct_rsp = requests.request("GET", acct_request, headers=headers, data=payload)


# st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# st.title("WiTaxi Pay - Account Dashboard")

accrual_accts = [i for i in acct_rsp.json()['data'] if i['type'] == 'accrual']
sel_rev = float([i['available'] for i in accrual_accts if i['alias'] == "platform_accrual"][0])
# print(f'SEL Revenue: {sel_rev:.2f}')

# witaxipay revenue
witaxipay_rev = float([i['available'] for i in accrual_accts if i['alias'] == "network_accrual"][0])
# print(f'WiTaxi Pay Revenue: {witaxipay_rev:.2f}')

merchant_accts = [i for i in acct_rsp.json()['data'] if i['type'] == 'merchant']

# Bhadala Revenue
bhadala_rev = float([i['available'] for i in merchant_accts if i['alias'] == "Bhadala Holding Account"][0])
# print(f'Bhadala Revenue: {bhadala_rev:.2f}')

# # Associations Revenue
assoc_rev = float([i['available'] for i in merchant_accts if i['alias'] == "Associations Holding Account"][0])
# print(f'Association Revenue: {assoc_rev:.2f}')

wallet_accts = [i for i in acct_rsp.json()['data'] if i['type'] == 'wallet']
registered_wallets = len(wallet_accts)
available = [float(i['available']) for i in wallet_accts]
wallet_value = f'{sum(available):.2f}'


# # @st.fragment
# def account_reporting(start, end):
import pandas as pd
df = pd.DataFrame(columns=['Name', 'Phone Number', 'Email', 'Status', 'Created On', 'Available', 'Balance',
                                  'SNSI', "Trans Type", "Amount", "Timestamp", 'Role'])
for dic in wallet_accts:
  num = dic['alias']
  if num == "27817412150":
    print(f"Skipping: {num}...")
    continue
  consumer_request = f"{base_url}/network/express/consumer/{num}"
  response = requests.request("GET", consumer_request, headers=headers, data=payload)
  data = response.json()['data']
  name = data['name']
  email = data['email']
  state = data['state']
  role = data['abstract']['role']
  wallet_trans = f"{base_url}/network/express/wallet/{num}/transaction?currency=ZAR"
  wallet_rsp = requests.request("GET", wallet_trans, headers=headers, data=payload)
  # wallet_data = wallet_rsp.json()['data']
  wallet_data = [i for i in wallet_rsp.json()['data'] if i['timestamp'].split('T')[0] > "2024-09-30"]
  # print(f"Data - {wallet_data}")

  # if start == end:
  #   wallet_data = [i for i in wallet_rsp.json()['data'] if datetime.strptime(i['timestamp'].split('T')[0], '%Y-%m-%d').date() == start]
  # else:
  #   wallet_data = [i for i in wallet_rsp.json()['data'] if datetime.strptime(i['timestamp'].split('T')[0], '%Y-%m-%d').date() >= start and datetime.strptime(i['timestamp'].split('T')[0], '%Y-%m-%d').date() <= end]





  # print(f"Len - {len(wallet_data)}")
  if wallet_data:
    # print(f"{num} - {name}")
    # print(f"-----------{wallet_data}------------")
    # new_wallet_data = [i for i in wallet_rsp.json()['data'] if i['timestamp'].split('T')[0] > '2024-09-30']

    # num_transactions = len(wallet_data)   # getting the number of wallet transaction
    # Doing Transaction Breakdown
    for i in wallet_data:
      type_name = i['abstract']['type'] if i['type_name'] == 'Transfer' else i['type_name']
      snsi = i['snsi']
      amount = i['amount']
      # date, time = i['timestamp'].split('T')
      timestamp = i['timestamp']
      new_rec = pd.DataFrame([[name, f"{num}", email, state, dic['opened'], dic['available'], dic['balance'],
                            snsi, type_name, amount, timestamp, role]],
                          columns=['Name', 'Phone Number', 'Email', 'Status', 'Created On', 'Available', 'Balance',
                                    'SNSI', "Trans Type", "Amount", "Timestamp", 'Role'])
      df = pd.concat([df, new_rec], ignore_index=True)

  else:
    new_rec = pd.DataFrame([[name, num, email, state, dic['opened'], dic['available'], dic['balance'],
                          None, "No Transaction", 0, None, role]],
                        columns=['Name', 'Phone Number', 'Email', 'Status', 'Created On', 'Available', 'Balance',
                                  'SNSI', "Trans Type", "Amount", "Timestamp", 'Role'])


    df = pd.concat([df, new_rec], ignore_index=True)

df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')

df = df.assign(
        date=df["Timestamp"].dt.date,
        time=df["Timestamp"].dt.time
    )

df.to_csv('Data/data.csv', index=False)
