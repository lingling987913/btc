# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 21:01:40 2023

@author: zhouh
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

####################################################### 数据加载预处理 ######################################################################### 


def btc_model(file_path):
    # DataSheet 1:
    # Order History 现货订单记录数据加载预处理
    sheet_name = "Order History 现货订单记录"
    df_order = pd.read_excel(file_path, sheet_name)

    # 优化列名
    optimized_columns = {
        "User ID 用户ID": "User_ID",
        "Market ID 交易对": "Market_ID",
        "Price 价格": "Price",
        "Qty 数量": "Quantity",
        "Average Price 平均价": "Average_Price",
        "Remain Qty 剩余数量": "Remain_Quantity",
        "Trade Qty 交易数量": "Trade_Quantity",
        "Time 时间": "Time",
        "Update Time 更新时间": "Update_Time",
        "Side 买卖交易方向": "Buy_Sell",
        "Status 交易状态": "Status",
        "Type 挂单类型": "Order_Type",
        "Stop Price 止损价": "Stop_Price",
        "Price Unit 计价单位": "Price_Unit",
        "Amount Unit 数量单位": "Amount_Unit"
    }

    selected_columns = ["Time", "Quantity", "Average_Price", "Trade_Quantity", "Buy_Sell", "Price_Unit", "Amount_Unit","Status"]
    df_order.rename(columns=optimized_columns, inplace=True)
    df_order = df_order[selected_columns] # 保留所需的列
    del sheet_name, optimized_columns, selected_columns

    # 新增 Currency_Out/Currency_Out_Amount 列
    df_order["Currency_Out"] = df_order.apply(
        lambda row: row["Price_Unit"] if row["Buy_Sell"] == "BUY" else row["Amount_Unit"],
        axis=1
    )

    df_order["Currency_Out_Amount"] = df_order.apply(
        lambda row: row["Average_Price"]*row["Trade_Quantity"] if row["Buy_Sell"] == "BUY" else row["Trade_Quantity"],
        axis=1
    )

    # 新增 Currency_In/Currency_In_Amount 列
    df_order["Currency_In"] = df_order.apply(
        lambda row: row["Amount_Unit"] if row["Buy_Sell"] == "BUY" else row["Price_Unit"],
        axis=1
    )

    df_order["Currency_In_Amount"] = df_order.apply(
        lambda row: row["Trade_Quantity"] if row["Buy_Sell"] == "BUY" else row["Average_Price"]*row["Trade_Quantity"],
        axis=1
    )

    df_order["Trade_Type"] = "order" 

    # DataSheet 2:
    # Deposit History 充值记录数据加载预处理
    sheet_name = "Deposit History 充值记录"
    df_deposit = pd.read_excel(file_path, sheet_name)

    # 优化列名
    optimized_columns = {
        "User ID 用户ID": "User_ID",
        "Currency 币种": "Currency_In",
        "Amount 数额": "Currency_In_Amount",
        "Account Type 帐户类型": "Account_Type",
        "BUSD 对应数额": "BUSD_Amount",
        "Deposit Address 接收地址": "Deposit_Address",
        "Source Address 发送地址": "Source_Address",
        "TXID 交易哈希": "TXID",
        "Create Time 时间": "Time",
        "Status 状态": "Status",
        "Network 网络": "Network",
        "CounterParty ID 内部划转方ID": "CounterParty_ID"
    }

    selected_columns = ["Time", "Currency_In", "Currency_In_Amount", "BUSD_Amount", "Status"]

    df_deposit.rename(columns=optimized_columns, inplace=True)
    df_deposit = df_deposit[selected_columns] # 保留所需的列
    del sheet_name, optimized_columns, selected_columns

    # 新增 Currency_Out/Currency_Out_Amount 列
    df_deposit["Currency_Out"] = ""
    df_deposit["Currency_Out_Amount"] = 0.0

    df_deposit["Trade_Type"] = "deposit" 

    # DataSheet 3:
    # Withdrawal History 提现记录数据加载预处理
    sheet_name = "Withdrawal History 提现记录"
    df_withdrawal = pd.read_excel(file_path, sheet_name)

    # 优化列名
    optimized_columns = {
        "User ID 用户ID": "User_ID",
        "Currency 币种": "Currency_Out",
        "Amount 数额": "Currency_Out_Amount",
        "Account Type 帐户类型": "Account_Type",
        "BUSD 对应数额": "BUSD_Amount",
        "Destination Address 目标地址": "Destination_Address",
        "Label/Tag/Memo 标签/备忘录": "Label_Tag_Memo",
        "txId 交易哈希": "TXID",
        "Apply Time 申请时间": "Time",
        "Status 状态": "Status",
        "Network 网络": "Network",
        "CounterParty ID 内部划转方ID": "CounterParty_ID"
    }


    selected_columns = ["Time", "Currency_Out", "Currency_Out_Amount", "BUSD_Amount", "Status"]

    df_withdrawal.rename(columns=optimized_columns, inplace=True)
    df_withdrawal = df_withdrawal[selected_columns] # 保留所需的列
    del sheet_name, optimized_columns, selected_columns

    # 新增 Currency_In/Currency_In_Amount 列
    df_withdrawal["Currency_In"] = ""
    df_withdrawal["Currency_In_Amount"] = 0.0

    df_withdrawal["Trade_Type"] = "withdrawal" 

    # DataSheet 4:
    # P2P 法币交易数据加载预处理
    sheet_name = "P2P 法币交易"
    df_RMB = pd.read_excel(file_path, sheet_name)

    # 优化列名
    optimized_columns = {
        "Order ID 订单ID": "Order_ID",
        "Ad number ad号": "Ad_Number",
        "Buy or Sell 买卖": "Buy_Sell",
        "Crypto 币种": "Crypto",
        "Amount 数额": "Amount",
        "Fiat Currency 法币": "Fiat_Currency",
        "Total Amount 总数额": "Total_Amount",
        "Unit Price 单价": "Unit_Price",
        "Take ID 对手方用户ID": "Take_ID",
        "Ad publisher ID 广告发行人": "Ad_Publisher_ID",
        "Create Time 创建时间": "Time",
        "Status 状态": "Status",
        "Payment method 支付方式": "Payment_Method",
        "Client 客户端": "Client",
        "Payment Time 支付时间": "Payment_Time",
        "Release time 放币时间": "Release_Time",
        "Update time 更新时间": "Update_Time"
    }


    selected_columns = ["Time", "Buy_Sell", "Crypto", "Amount", "Total_Amount", "Unit_Price", "Status"]

    df_RMB.rename(columns=optimized_columns, inplace=True)
    df_RMB = df_RMB[selected_columns] # 保留所需的列
    del sheet_name, optimized_columns, selected_columns

    # 新增 Currency_Out/Currency_Out_Amount 列
    df_RMB["Currency_Out"] = df_RMB.apply(
        lambda row: "" if row["Buy_Sell"] == "buy" else row["Crypto"],
        axis=1
    )

    df_RMB["Currency_Out_Amount"] = df_RMB.apply(
        lambda row: 0.0 if row["Buy_Sell"] == "buy" else row["Amount"],
        axis=1
    )

    # 新增 Currency_In/Currency_In_Amount 列
    df_RMB["Currency_In"] = df_RMB.apply(
        lambda row: row["Crypto"] if row["Buy_Sell"] == "buy" else "",
        axis=1
    )

    df_RMB["Currency_In_Amount"] = df_RMB.apply(
        lambda row: row["Amount"] if row["Buy_Sell"] == "buy" else 0.0,
        axis=1
    )

    df_RMB["Trade_Type"] = "RMB" 

    # DataSheet 5:
    # Binance Pay 币安支付数据加载预处理
    sheet_name = "Binance Pay 币安支付"
    df_binance = pd.read_excel(file_path, sheet_name)

    # 优化列名
    optimized_columns = {
        "Currency 币种": "Currency",
        "Amount 数额": "Amount",
        "Transaction Time 交易时间": "Time"
    }


    selected_columns = ["Time", "Currency", "Amount"]

    df_binance.rename(columns=optimized_columns, inplace=True)
    df_binance = df_binance[selected_columns] # 保留所需的列
    del sheet_name, optimized_columns, selected_columns

    # 新增 Currency_Out/Currency_Out_Amount 列
    df_binance["Currency_Out"] = df_binance.apply(
        lambda row: "" if row["Amount"] > 0 else row["Currency"],
        axis=1
    )

    df_binance["Currency_Out_Amount"] = df_binance.apply(
        lambda row: 0.0 if row["Amount"] > 0 else -row["Amount"],
        axis=1
    )

    # 新增 Currency_In/Currency_In_Amount 列
    df_binance["Currency_In"] = df_binance.apply(
        lambda row: row["Currency"] if row["Amount"] > 0 else "",
        axis=1
    )

    df_binance["Currency_In_Amount"] = df_binance.apply(
        lambda row: row["Amount"] if row["Amount"] > 0 else 0.0,
        axis=1
    )

    df_binance["Trade_Type"] = "binance" 


    ##################### 将5张数据表合并成一个统一格式的流入/流出 In/Out表格
    same_colums = ["Time", "Currency_In", "Currency_In_Amount", "Currency_Out", "Currency_Out_Amount", "Trade_Type"]



    merged_df = pd.concat([df_order[df_order["Status"] == "FILLED"][same_colums], 
                        df_deposit[df_deposit["Status"] == "成功"][same_colums],
                        df_withdrawal[df_withdrawal["Status"] == "Success"][same_colums],
                        df_RMB[df_RMB["Status"] == "Completed"][same_colums],
                        df_binance[same_colums]], ignore_index=True)



    merged_df = pd.concat([df_order[df_order["Status"] == "FILLED"][same_colums], 
                        df_deposit[df_deposit["Status"] == "成功"][same_colums],
                        df_withdrawal[df_withdrawal["Status"] == "Success"][same_colums],
                        df_RMB[df_RMB["Status"] == "Completed"][same_colums]], ignore_index=True)
    return merged_df






if __name__ == "__main__":
    # 读取Excel文件
    file_path = r'/Users/simo/Data/btc/data1.xlsx'
    merged_df = btc_model(file_path=file_path)
    print(merged_df)




