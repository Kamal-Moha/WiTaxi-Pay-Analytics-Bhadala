import requests
import pandas as pd
import streamlit as st
from time import sleep
import streamlit_shadcn_ui as ui

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
# st.set_page_config(page_title="WiTaxi Pay Dashboard", page_icon="📊", layout="wide")

st.set_page_config(
    page_title="WiTaxi Pay Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

base_url = "https://api.production.af-south-1.siliconenterprise.com"
payload = {}
headers = {
  'Accept': '*/*',
  'Authorization': 'Bearer 5ebb05ae-5422-417f-b639-286dd3d5be8b'
}
# Getting account Info
acct_request = f"{base_url}/network/express/account"
acct_rsp = requests.request("GET", acct_request, headers=headers, data=payload)

rep_selectbox = st.sidebar.selectbox(
    "What do you want to monitor?",
    ("Account Reporting", "Transaction Analytics")
)

print(rep_selectbox)


st.markdown(hide_streamlit_style, unsafe_allow_html=True)
# st.title("WiTaxi Pay - Account Dashboard")

accrual_accts = [i for i in acct_rsp.json()['data'] if i['type'] == 'accrual']
sel_rev = float([i['available'] for i in accrual_accts if i['alias'] == "platform_accrual"][0])
# print(f'SEL Revenue: {sel_rev:.2f}')

# Bank Revenue
bank_rev = float([i['available'] for i in accrual_accts if i['alias'] == "bank_accrual"][0])

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


@st.fragment
def account_reporting(start, end):
  import pandas as pd
  df = pd.DataFrame(columns=['Name', 'Phone Number', 'Email', 'Status', 'Created On', 'Available', 'Balance',
                            'Num of Transactions', 'Charges', 'Topups', 'p2p transfers', 'Ride payments', 'Cashouts', 'Last Trans Date', 'Last Trans Type', 'Last Trans Amt', 'Role'])

  import streamlit as st
  with st.spinner("Loading..."):
    for dic in wallet_accts:
      num = dic['alias']
      if num == "27817412150":
        print(f"Skipping: {num}...")
        continue
      consumer_request = f"{base_url}/network/express/consumer/{num}"
      response = requests.request("GET", consumer_request, headers=headers, data=payload)
      data = response.json()['data']
      email = data['email']
      name = data['name']
      state = data['state']
      role = data['abstract']['role']
      wallet_trans = f"{base_url}/network/express/wallet/{num}/transaction?currency=ZAR"
      wallet_rsp = requests.request("GET", wallet_trans, headers=headers, data=payload)
      # wallet_data = wallet_rsp.json()['data']

      if start == end:
        wallet_data = [i for i in wallet_rsp.json()['data'] if datetime.strptime(i['timestamp'].split('T')[0], '%Y-%m-%d').date() == start]
      else:
        wallet_data = [i for i in wallet_rsp.json()['data'] if datetime.strptime(i['timestamp'].split('T')[0], '%Y-%m-%d').date() >= start and datetime.strptime(i['timestamp'].split('T')[0], '%Y-%m-%d').date() <= end]

      if wallet_data:
        # new_wallet_data = [i for i in wallet_rsp.json()['data'] if i['timestamp'].split('T')[0] > '2024-09-30']
        
        num_transactions = len(wallet_data)   # getting the number of wallet transaction
        # Doing Transaction Breakdown
        di = {}
        for i in wallet_data:
          type_name = i['type_name']
          type_name = i['abstract']['type'] if i['type_name'] == 'Transfer' else i['type_name']
          di[type_name] = di.get(type_name, 0) + 1

        def_di = {"Top Up": 0, 'p2p': 0, 'ride': 0,'Cash Out': 0, 'Charge': 0}   # Default dictionary to model
        if di:
          for k in di.keys():
            def_di[k] = di[k]
            charge, topup, p2p, ride, cashout  = def_di['Charge'], def_di['Top Up'], def_di['p2p'], def_di['ride'], def_di['Cash Out']
        # else:
        #   charge, topup, transfer, cashout = 0, 0, 0, 0



        for k in range(len(wallet_data)):
          if wallet_data[k]['type_name'] in ['Transfer', 'Cash Out', 'Top Up']:
            actual_trans = wallet_data[k]
            last_trans_date = actual_trans['timestamp']
            last_trans_amt = actual_trans['amount']
            last_trans_type = actual_trans['abstract']['type'] if actual_trans['type_name'] == 'Transfer' else actual_trans['type_name']   # actual_trans['type_name']
            break

      else:
        num_transactions, charge, topup, p2p, ride, cashout, last_trans_date, last_trans_amt, last_trans_type = 0, 0, 0, 0, 0, 0, None, None, None


      for i in range(registered_wallets):
        new_rec = pd.DataFrame([[name, num, email, state, dic['opened'], dic['available'], dic['balance'],
                                num_transactions, charge, topup, p2p, ride, cashout, last_trans_date, last_trans_amt, last_trans_type, role]],
                              columns=['Name', 'Phone Number', 'Email', 'Status', 'Created On', 'Available', 'Balance',
                                        'Num of Transactions', 'Charges', 'Topups', 'p2p transfers', 'Ride payments', 'Cashouts', 'Last Trans Date', 'Last Trans Amt', 'Last Trans Type', 'Role'])
      df = pd.concat([df, new_rec], ignore_index=True)

    # REGISTERED WALLETS
    st.markdown('**Wallet Account Analytics**')
    if start == end:
      st.write(f'Below Data is for the date: {start}')
    else:
      st.write(f'Below Data is from {start} until {end}')
                
    st.dataframe(df)

@st.cache_data
def transaction_analytics():
  st.markdown(hide_streamlit_style, unsafe_allow_html=True)
  st.header('WiTaxi Pay Transaction Report', divider='rainbow')

  # getting registered wallets - To calculate ARPU
  account_request = f"{base_url}/network/express/account"
  account_rsp = requests.request("GET", account_request, headers=headers, data=payload)
  wallet_accts = [i for i in account_rsp.json()['data'] if i['type'] == 'wallet']
  registered_wallets = len(wallet_accts)

  accrual_accts = [i for i in account_rsp.json()['data'] if i['type'] == 'accrual']
  # witaxipay revenue
  witaxipay_rev = float([i['available'] for i in accrual_accts if i['alias'] == "network_accrual"][0])

  # merchant account
  merchant_accts = [i for i in account_rsp.json()['data'] if i['type'] == 'merchant']

  # Bhadala Revenue
  bhadala_rev = float([i['available'] for i in merchant_accts if i['alias'] == "Bhadala Holding Account"][0])


  # Creating Transaction Report
  accounts = {
      "WiTaxi Pay":"1000000004",
      "Bhadala":"3000000002",
      "Nedbank": "1000000003"
  }

  for acct in accounts:
    st.header(f"{acct} Info")
    if acct == "Bhadala":
      st.metric("Revenue", f"{bhadala_rev:.2f}")
    elif acct == "Nedbank":
      st.metric("Revenue", f"{bank_rev:.2f}")
    else:
      col1, col2 = st.columns(2)
      col1.metric("Revenue", f"{witaxipay_rev:.2f}")
      col2.metric("ARPU", round(witaxipay_rev/registered_wallets, 3))

    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)


    # transaction report
    url = f"{base_url}/network/express/account/{accounts[acct]}/transaction"

    acct_rsp = requests.request("GET", url, headers=headers, data=payload)

    transactions = acct_rsp.json()['data']
    tup = ()
    for tran in transactions:
      tup+=(tran['reference'],)

    trans_count = {}
    amount_per_type = {}
    for i in set(tup):
      trans_count[i] = 0
      amount_per_type[i] = 0

    for tran in transactions:
      if tran['state'] == "authorization_success":
        trans_count[tran['reference']]+=1
        # if tran['reference'] ==
        amount_per_type[tran['reference']]+=float(tran['amount'])

      # tup+=(tran['reference'],)

    references = {
        "Notification via SMS": "SMS",
        "Cashout via ATM": "Cashout ATM",
        "Cashout via Retail": "Cashout Retail",
        "Wallet to Wallet Transfer - Ride": "Ride payment",
        "Wallet to Wallet Transfer": "P2P Transfers"
        }

    trans_count = {(references[k] if k in references else k):v  for (k,v) in trans_count.items()}
    amount_per_type = {(references[k] if k in references else k):v  for (k,v) in amount_per_type.items()}

    lst_pick = [trans_count, amount_per_type]
    for pick in lst_pick:
      # Transaction Count Pie Chart

      # declaring data
      data = [v for v in pick.values()]
      keys = [k for k in pick.keys()]

      import plotly.graph_objects as go
      colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen']

      fig = go.Figure(data=[go.Pie(labels=keys,
                                  values=data)])

      fig.update_traces(hoverinfo='value', textinfo='label+percent', textfont_size=12,
                        marker=dict(line=dict(color='#000000', width=1)))

      # fig.show()

      # displaying chart
      if pick == trans_count:
        fig.update_layout(barmode='group',
                          title=dict(
                                    text = "Count of Each Transaction Type",
                                    x = 0.5, y = 0.90,
                                    xanchor =  'center', yanchor = 'top',
                                    #pad = dict(
                                    #            t = 0
                                    #           ),
                                    font = dict(
                                                #family='Courier New, monospace',
                                                size = 20,
                                                #color='#000000'
                                                )
                                    )
                        )
        col4.plotly_chart(fig, theme=None)
        tran_ct_df = pd.DataFrame.from_dict(data = {'Type': [k for k in trans_count.keys()],'Count': [v for v in trans_count.values()]})
        # st.dataframe(df)
      else:
        fig.update_layout(barmode='group',
                        title=dict(
                                  text = "Revenue Per Each Transaction Type",
                                  x = 0.5, y = 0.90,
                                  xanchor =  'center', yanchor = 'top',
                                  #pad = dict(
                                  #            t = 0
                                  #           ),
                                  font = dict(
                                              #family='Courier New, monospace',
                                              size = 20,
                                              #color='#000000'
                                              )
                                  ))
        col3.plotly_chart(fig, theme=None)
        rev_df = pd.DataFrame.from_dict(data = {'Type': [k for k in amount_per_type.keys()],'Revenue': [v for v in amount_per_type.values()]})
        # st.dataframe(df)
    col5.dataframe(rev_df)
    col6.dataframe(tran_ct_df)



if rep_selectbox == "Account Reporting":

  st.header('WiTaxi Pay - Account Dashboard', divider='rainbow')

  cols = st.columns(4)
  with cols[0]:
      ui.metric_card(title="WiTaxi Pay Revenue", content=f"R {witaxipay_rev}", key="card1")
  with cols[1]:
      ui.metric_card(title="SEL Revenue", content=f"R {sel_rev}", key="card2")
  with cols[2]:
      ui.metric_card(title="Bhadala Revenue", content=f"R {bhadala_rev}", key="card3")
  with cols[3]:
      ui.metric_card(title="Associations Revenue", content=f"R {assoc_rev}",)

  # Down Column
  cols = st.columns(3)
  with cols[0]:
      ui.metric_card(title="Registered Wallets", content=registered_wallets)
  with cols[1]:
      ui.metric_card(title="Nedbank Revenue", content=bank_rev)
  with cols[2]:
      ui.metric_card(title="Value of Wallets", content=wallet_value)


  from datetime import datetime, timedelta
  import streamlit as st
  from streamlit_date_picker import date_range_picker, date_picker, PickerType
  st.markdown("**Date Range Picker**")
  st.write('(Select Dates after 2024-09-30)')
  default_start, default_end = datetime.now() - timedelta(days=1), datetime.now()
  refresh_value = timedelta(days=1)
  date_range_string = date_range_picker(picker_type=PickerType.date,
                                        start=default_start, end=default_end,
                                        key=f'date_range_picker',
                                        refresh_button={'is_show': True, 'button_name': 'Refresh Last 1 Days',
                                                        'refresh_value': refresh_value})
  if date_range_string:
    start, end = date_range_string
    start = datetime.strptime(start, "%Y-%m-%d").date()
    end = datetime.strptime(end, "%Y-%m-%d").date()
    print(start, end)
    print(type(start), type(end))
    # start, end = date_range_string

    # st.write(f"Below Data is from {start} to {end}")

  print(date_range_string)
  import streamlit_shadcn_ui as ui
  
  account_reporting(start, end)

else:
  transaction_analytics()
