# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 18:51:55 2023

@author: zhouh
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

############################################################################################################################################################## 
# 读取Excel文件
file_path = r"C:\Users\zhouh\OneDrive\Documenti\工作\杭州黑客与画家智能科技有限公司\加密币反洗钱\2.xlsx"
sheet_name = "Order History 现货订单记录"
df = pd.read_excel(file_path, sheet_name)

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
    "Status 交易状态": "Trade_Status",
    "Type 挂单类型": "Order_Type",
    "Stop Price 止损价": "Stop_Price",
    "Price Unit 计价单位": "Price_Unit",
    "Amount Unit 数量单位": "Amount_Unit"
}

df.rename(columns=optimized_columns, inplace=True)

df.set_index("Time", inplace=True) # 将 "Time" 列设置为索引
df.sort_index(inplace=True) # 升序排序
df.index = pd.to_datetime(df.index)  # 将索引转换为 datetime 类型
df.index = df.index.strftime('%Y-%m-%d %H:%M:%S') # 格式化索引为 "YYYY-MM-DD HH:MM:SS"

total_trade_count = len(df) #取一下原始总的交易数量

df = df[df["Trade_Status"] == "FILLED"] #筛选出 "TradeStatus" 为 "FILLED" 的数据
total_trade_filled_count = len(df) #取一下实际完成的交易数量

# 保留所需的列
selected_columns = ["Market_ID", "Price", "Quantity", "Average_Price", "Trade_Quantity", "Buy_Sell", "Price_Unit", "Amount_Unit"]
df = df[selected_columns]


############################################################################################################################################################## 
stable_coin = ['BUSD','USDT','USDC'] #这三个元素是当前biance上的稳定币代码
df.loc[:, 'stable_trade'] = df.apply(lambda row: row['Price_Unit'] in stable_coin and row['Amount_Unit'] in stable_coin, axis=1) #标识出买卖均为稳定币的交易（空转交易）
stable_trade_count = df['stable_trade'].sum() #取一下纯稳定币空转交易的数量

############################################################################################################################################################## 

# Time_diff列为两次filled交易之间的时间间隔
df['Time_diff'] = pd.to_datetime(df.index).to_series().diff()
df['Time_diff'] = df['Time_diff'].apply(lambda x: x.total_seconds()).fillna(0)

df_true = df[df['stable_trade']] #只取纯稳定币交易

df_true_pre = df[df['stable_trade']].shift(1) 
merged_df = pd.merge(df_true, df_true_pre, left_index=True, right_index=True, suffixes=('_now', '_pre')) #取纯稳定币交易之前的一次纯稳定币交易，并列进行分析

merged_df['Trade_Quantity_diff'] = merged_df['Trade_Quantity_now'] / merged_df['Trade_Quantity_pre'] - 1 # 匹配后一次交易相对上一次的数量差异，用于后续筛选

coin_hold = np.where(merged_df['Buy_Sell_pre'] == 'BUY', merged_df['Amount_Unit_pre'], merged_df['Price_Unit_pre']) # 前一次交易后手上持有的币种，用于和now这个后续交易使用币种关联
coin_used = np.where(merged_df['Buy_Sell_now'] == 'BUY', merged_df['Price_Unit_now'], merged_df['Amount_Unit_now']) # 当前交易使用的币种

merged_df['same_coin'] = coin_used == coin_hold

# 此版本的风险交易标识flag为TRUE的设置标准为：
# 1、当前交易花出去的币种等于前一次交易获得的币种，即coin_hold==coin_used；
# 2、Trade_Quantity_diff的绝对值小于0.01；
merged_df['same_coin'] = (coin_used == coin_hold)
merged_df['same_quant'] = merged_df['Trade_Quantity_diff'].abs() < 0.01
merged_df['risk_flag'] = (merged_df['same_coin'] & merged_df['same_quant'])

merged_df['trade_group'] = (~merged_df['risk_flag']).cumsum() #将连续风险交易视为一组交易从而对交易进行分组
merged_df['group_count'] = merged_df.groupby('trade_group')['trade_group'].transform('count')

risk_trade_count = (merged_df['group_count'] > 1).sum() #取一下被标为risk flag的交易数量
output_sentence = """该用户在此区间共申报了{total_trade_count}笔交易，其中完成FILLED的交易共有{total_trade_filled_count}笔；属于稳定币之间的转换交易(无投资意义的转换操作)有{stable_trade_count}笔，而通过进一步分析认定为极大可能为风险交易的有{risk_trade_count}笔。""".format(
                    total_trade_count=total_trade_count,total_trade_filled_count=total_trade_filled_count,stable_trade_count=stable_trade_count,risk_trade_count=risk_trade_count)
print(output_sentence)


# 对风险标识交易的交易间隔作图
# 筛选 risk_flag 为 True 的数据
true_data = merged_df[merged_df['risk_flag']]

# 将 Time_diff 列的数据除以 3600
plot_data = true_data['Time_diff_now'] / 3600

# 画样本分布图
plt.hist(plot_data, bins=50, color='blue', edgecolor='black')
plt.title('Sample Distribution of Time_diff for risk_flag=True')
plt.xlabel('Time_diff (hours)')
plt.ylabel('Frequency')
plt.show()







