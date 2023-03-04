#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import plotly.io as io
io.renderers.default='browser' #이거 해야 ploty 실시간 확인 가능 fig.show()가 인터넷 창에
st.set_page_conf황ig(page_title='월간수출입통계',  layout='wide')
    
#%% 데이터 보기좋게 편집

df = pd.read_csv("data.csv")
df = df[df["year"] != "총계"].reset_index(drop = True)
df["month"] = pd.DatetimeIndex(df["year"]).month
df["date"] = pd.DatetimeIndex(df["year"]).strftime("%Y년 %m월")
df["year"] = pd.DatetimeIndex(df["year"]).year

df_korean_column = df[["date", "balPayments", "impDlr", "expDlr", "year", "month"]]
df_korean_column.columns = ["년월", "무역수지", "수입금액(달러)", "수출금액(달러)", "year", "month"]

df_for_nice_view_and_download = df_korean_column[["년월", "무역수지", "수입금액(달러)", "수출금액(달러)"]]
@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(df_for_nice_view_and_download)
#%% streamlit 출력


st.title("무역 수출입통계")
st.caption("""
           https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15102108 에서
           확보한 데이터를 사용.
           """)

#%% 해당기 근황 출력
st.header("무역 통계 현황")



year_month_selected = st.selectbox(
     '어느 기의 값을 보시겠습니까?',
     df_korean_column["년월"].iloc[12:].sort_index(ascending = False))
#year_month_selected = "2022년 01월"

selected = df_korean_column[df_korean_column["년월"] == year_month_selected]
year_calc = selected["year"].iloc[0]
month_calc = selected["month"].iloc[0]

is_before_12month = st.checkbox('전년동월비를 보시겠습니까?')

if is_before_12month:
    diff_help_message = "전년동월 대비 증감비"
    before_12month = (year_calc - 1), month_calc
    df_selection_for_diff = df_korean_column.query(
        "(year == @before_12month[0]) and (month == @before_12month[1])"
        )
else:
    diff_help_message = "전월 대비 증감비"
    before_1month = (year_calc-1, 12) if month_calc == 1 else (year_calc, month_calc-1)  
    df_selection_for_diff = df_korean_column.query(
        "(year == @before_1month[0]) and (month == @before_1month[1])"
        )


first_layer_col1, first_layer_col2, first_layer_col3 = st.columns(3)

first_layer_col1.metric("무역수지", 
            "{0:,.2f} 백만불".format(selected["무역수지"].iloc[0]/100000000),  
            "{0:,.2f} %".format(selected["무역수지"].iloc[0]/ df_selection_for_diff["무역수지"].iloc[0]),
            help=diff_help_message)
first_layer_col2.metric("수출금액",
            "{0:,.2f} 백만불".format(selected["수출금액(달러)"].iloc[0]/100000000),  
            "{0:,.2f} %".format(selected["수출금액(달러)"].iloc[0]/ df_selection_for_diff["수출금액(달러)"].iloc[0]),
            help=diff_help_message)
first_layer_col3.metric("수입금액",
            "{0:,.2f} 백만불".format(selected["수입금액(달러)"].iloc[0]/100000000),  
            "{0:,.2f} %".format(selected["수입금액(달러)"].iloc[0]/ df_selection_for_diff["수입금액(달러)"].iloc[0]),
            help=diff_help_message)

#%% plotly 그래프 1 전체 다함께
st.header("종합 그래프")

start_index_fig_bar, end_index_fig_bar = st.select_slider(
    '표를 확인할 범위를 설정하시오',
    options= df_korean_column["년월"],
    value=(df_korean_column.iloc[0]["년월"], df_korean_column.iloc[-1]["년월"] ))

df_column_slided = df_korean_column.query("(년월 >= @start_index_fig_bar) and (년월 <= @end_index_fig_bar)")

df_column_slided["수출금액(달러)"] = -1 * df_column_slided["수출금액(달러)"]
# 수출 금액은 음의 방향으로 되어 있음
fig_bar = px.bar(df_column_slided, x="년월", y=["수입금액(달러)", "수출금액(달러)"], 
                 barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Dark24)
fig_bar.add_traces(go.Scatter(x = df_column_slided["년월"], y = df_column_slided["무역수지"], mode = "lines", name="무역수지"))
fig_bar.update_layout(title='무역량 그래프', xaxis_title='기간', yaxis_title='액수 (달러)')
fig_bar.update_traces(hovertemplate='%{x}: %{y}')
#fig_bar.show()
st.plotly_chart(fig_bar, use_container_width=True)

#%% plotly 그래프 3개 각각



third_layer_col1, third_layer_col2, third_layer_col3 = st.columns(3)

third_layer_col1.header("수입금액")
fig_bar2 = px.bar(df_korean_column, x="년월", y=["수입금액(달러)"], 
                 barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Dark24)
fig_bar2.update_layout(title='수입금액 그래프(달러)', xaxis_title='기간', yaxis_title='액수 (달러)')
fig_bar2.update_traces(hovertemplate='%{x}: %{y}')
third_layer_col1.plotly_chart(fig_bar2, use_container_width=True)


third_layer_col2.header("무역수지")
fig_bar3 = px.bar(df_korean_column, x="년월", y=["무역수지"], 
                 barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Dark24)
fig_bar3.update_layout(title='무역수지 그래프(달러)', xaxis_title='기간', yaxis_title='액수 (달러)')
fig_bar3.update_traces(hovertemplate='%{x}: %{y}')
third_layer_col2.plotly_chart(fig_bar3, use_container_width=True)


third_layer_col3.header("수출금액")
fig_bar4 = px.bar(df_korean_column, x="년월", y=["수출금액(달러)"], 
                 barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Dark24)
fig_bar4.update_layout(title='수출금액 그래프(달러)', xaxis_title='기간', yaxis_title='액수 (달러)')
fig_bar4.update_traces(hovertemplate='%{x}: %{y}')
third_layer_col3.plotly_chart(fig_bar4, use_container_width=True)


#%% streamlit base dataframe show 그리도 파일 다운로드 (csv)

st.header("무역 통계 표")

fourth_layer_column = st.columns(3)
#fourth_layer_column[1].dataframe(df_for_nice_view_and_download)
from st_aggrid import AgGrid, GridOptionsBuilder, ColumnsAutoSizeMode
AgGrid(df_for_nice_view_and_download,
       height = 300,
       columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS
       
       )
st.download_button(
    label="CSV파일 다운로드",
    data=csv,
    file_name='월간수출입통계_byMr21percent.csv',
    mime='text/csv',
)



