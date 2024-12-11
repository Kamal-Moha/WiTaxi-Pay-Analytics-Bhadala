import requests
import pandas as pd
import streamlit as st
from time import sleep
import streamlit_shadcn_ui as ui
from datetime import date

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

st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 5rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)


base_url = st.secrets['base_url']
payload = {}
headers = {
  'Accept': '*/*',
  'Authorization': f'Bearer {st.secrets["auth_key"]}'
}
# Getting account Info
acct_request = f"{base_url}/network/express/account"
acct_rsp = requests.request("GET", acct_request, headers=headers, data=payload)

st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
def account_reporting(comb_df, start, end):
  import pandas as pd

  print(f"** {type(start)} {type(end)}")
  if start == end:
    filtered_df = df[df['date'] == start]
  else:
    filtered_df = df[(df['date'] >= start) & (df['date'] <= end)]

  unique_nums = filtered_df['Phone Number'].unique()

  final_df = pd.DataFrame(columns=['Name', 'Phone Number', 'Email', 'Role', 'Status', 'Created On', 'Available', 'Balance',
                              'Num of Transactions', 'Topups', 'p2p transfers', 'Ride payments', 'Cashouts',
                                  'Last Trans Date', 'Last Trans Type', 'Last Trans Amt'])

  for num in df['Phone Number'].unique():
    di = {"Top Up": 0, "p2p": 0, "ride": 0, "Charge": 0, "Cash Out": 0}
    if num in unique_nums:
      spec_df = filtered_df[filtered_df['Phone Number'] == num]

      last_trans = spec_df[spec_df['Trans Type'] != "Charge"].iloc[0]
      last_trans_type = last_trans['Trans Type']  # last trans type
      last_trans_date = last_trans['date']  #last trans date
      time = last_trans['time']  # last trans time
      last_trans_amt = last_trans['Amount']  # last trans amount
      name = last_trans['Name'] # name
      email = last_trans['Email'] # email
      status = last_trans['Status'] # status
      created_on = last_trans['Created On'] # created on
      role = last_trans['Role'] # role
      available, balance = last_trans['Available'], last_trans['Balance']

      # print(f"{t_type} - {date} - {time} - {amount}")

      for i in spec_df['Trans Type']:
        if i in di:
          di[i]+=1
      # final_df.from_dict(di)
      # print(di)
      charge, topup, p2p, ride, cashout  = di['Charge'], di['Top Up'], di['p2p'], di['ride'], di['Cash Out']
      num_of_transactions = sum([topup, p2p, ride, cashout])
      new_rec = pd.DataFrame([[name, f"{num}", email, role, status, created_on, available, balance,
                                num_of_transactions, topup, p2p, ride, cashout, last_trans_date,
                              last_trans_amt, last_trans_type]],
                              columns=['Name', 'Phone Number', 'Email', 'Role', 'Status', 'Created On', 'Available', 'Balance',
                                        'Num of Transactions', 'Topups', 'p2p transfers', 'Ride payments',
                                        'Cashouts', 'Last Trans Date', 'Last Trans Amt', 'Last Trans Type'])
    
      final_df = pd.concat([final_df, new_rec], ignore_index=True)

    else:
      num_of_transactions = 0
      spec_df = df[df['Phone Number'] == num]
      trans = spec_df.iloc[0]
      name = trans['Name']
      email = trans['Email']
      status = trans['Status']
      created_on = trans['Created On']
      role = trans['Role']
      available, balance = trans['Available'], trans['Balance']
      charge, topup, p2p, ride, cashout  = di['Charge'], di['Top Up'], di['p2p'], di['ride'], di['Cash Out']
      last_trans_amt, last_trans_date, last_trans_type = 0, None, None
      
      new_rec = pd.DataFrame([[name, f"{num}", email, role, status, created_on, available, balance,
                                num_of_transactions, topup, p2p, ride, cashout, last_trans_date,
                              last_trans_amt, last_trans_type]],
                              columns=['Name', 'Phone Number', 'Email', 'Role', 'Status', 'Created On', 'Available', 'Balance',
                                        'Num of Transactions', 'Topups', 'p2p transfers', 'Ride payments',
                                        'Cashouts', 'Last Trans Date', 'Last Trans Amt', 'Last Trans Type'])
    
      final_df = pd.concat([final_df, new_rec], ignore_index=True)
  # global total_transactions
  total_transactions = sum(final_df['Num of Transactions'])
  print(f"TRANS: {total_transactions}")
  return total_transactions, final_df
  # st.dataframe(final_df)

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
        amount_per_type[tran['reference']]+=float(tran['amount'])

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

tab1, tab2 = st.tabs(["Account Reporting", "Transaction Analytics"])


with tab1:

  st.header('WiTaxi Pay - Account Dashboard', divider='rainbow')

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
                                        refresh_buttons=[{'is_show': True, 'button_name': 'Refresh Last 1 Days',
                                                        'refresh_value': refresh_value}])
  if date_range_string:
    start, end = date_range_string
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    print(start, end)
    print(type(start), type(end))

  acct_df = pd.read_csv("Data/accts_data.csv")
  
  acct_df['date']= pd.to_datetime(acct_df['date'])

  if start == end:
    flt_acct = acct_df[acct_df['date'] == start]
  else:
    flt_acct = acct_df[(acct_df['date'] >= start) & (acct_df['date'] <= end)]

  df = pd.read_csv('Data/data.csv')
  df['date'] = pd.to_datetime(df['date'])
  comb_df = df
  print(date_range_string)
  import streamlit_shadcn_ui as ui

  
  fun_call = account_reporting(df, start, end)

  sel_acct = flt_acct[flt_acct['Acct Name'] == "SEL"]
  sel_rev = f"{sum(sel_acct['Amount']):.2f}"
  # Bhadala
  bhadala_acct = flt_acct[flt_acct['Acct Name'] == "Bhadala"]
  bhadala_rev = f"{sum(bhadala_acct['Amount']):.2f}"
  # Bank
  nedbank_acct = flt_acct[flt_acct['Acct Name'] == "Nedbank"]
  nedbank_rev = f"{sum(nedbank_acct['Amount']):.2f}"
  # WiTaxiPay
  witaxipay_acct = flt_acct[flt_acct['Acct Name'] == "WiTaxi Pay"]
  witaxipay_rev = f"{sum(witaxipay_acct['Amount']):.2f}"
  # Associations
  assoc_acct = flt_acct[flt_acct['Acct Name'] == "Association"]
  assoc_rev = f"{sum(assoc_acct['Amount']):.2f}" 

  cols = st.columns(4)
  with cols[0]:
    ui.metric_card(title="WiTaxi Pay Revenue", content=f"R {witaxipay_rev}", key="card1")
  with cols[1]:
    ui.metric_card(title="SEL Revenue", content=f"R {sel_rev}", key="card2")
  with cols[2]:
    ui.metric_card(title="Bhadala Revenue", content=f"R {bhadala_rev}", key="card3")
  with cols[3]:
    ui.metric_card(title="Associations Revenue", content=f"R {assoc_rev}",)

  trans_count = fun_call[0]
  # Down Column
  cols = st.columns(4)
  with cols[0]:
    ui.metric_card(title="Registered Wallets", content=registered_wallets)
  with cols[1]:
    ui.metric_card(title="Nedbank Revenue", content=nedbank_rev)
  with cols[2]:
    ui.metric_card(title="Value of Wallets", content=wallet_value)
  with cols[3]:
    ui.metric_card(title="Number of Transactions", content=trans_count)
  
  st.dataframe(fun_call[1])
  
  

with tab2:
  transaction_analytics()

