#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 20:11:37 2023

@author: woneunglee
"""

import pandas as pd
import streamlit as st 
from st_aggrid import AgGrid
import datetime
import plotly.express as px
import plotly.io as io


io.renderers.default='browser'
st.set_page_config(page_title='금리스프레드조회',  layout='wide')
st.title("금리 스프레드 (기간 및 신용) 조회")


인증키 = st.secrets["BOK_API_KEY"]
통계조회 = "StatisticSearch"
통계표코드 = "817Y002"
주기 = "D"
검색시작일자 = "20230201"
검색종료일자 = "20230228"

resample_key = {'년' : "A",
                '분기' : "Q",
                '월' : "M",
                "반월" : "SM",
                "주" : "W",
                '일' : "D",
 }


#%% 검색 데이터 받는 위치
inputWigetColumns = st.columns(3)

# 주기

조회주기 = inputWigetColumns[0].radio(
    "원하시는 데이터 조회 주기를 선택하시오.",
    ('년', '분기', '월', '반월', '주', '일'))

# 시작일자
start_d = inputWigetColumns[1].date_input(
    "조회 시작일을 설정하시오.",
    value = datetime.date(2020, 1, 1),
    min_value = datetime.date(2000, 12, 18),
    max_value = datetime.datetime.today()
    )
# 종료일자
end_d = inputWigetColumns[2].date_input(
    "조회 종료일을 설정하시오.",
    min_value = start_d,
    max_value = datetime.datetime.today())

# 통안채 2년의 시작일은 1999/02/10
# 국고채 3년의 시작일은 1998/11/13
# 국고채 5년의 시작일은 2000/01/04
# 국고채 1년의 시작일은 2000/02/01
# 국고채기 10년의 시작일은 2000/12/18
# 회사채 BBB-의 시작일은 2000/09/30
# 회사채 BBB-의 시작일은 2000/09/30

#%% 금리 데이터 확보
#url = "https://ecos.bok.or.kr/api/" + 통계조회 +"/" + 인증키 + "/xml/kr/1/2000/" + 통계표코드 + "/" + "D" + "/" + 검색시작일자 + "/" + 검색종료일자



url = "https://ecos.bok.or.kr/api/" + 통계조회 +"/" + 인증키 + "/xml/kr/1/100000/" + 통계표코드 + "/" + "D" + "/" + start_d.strftime("%Y%m%d") + "/" + end_d.strftime("%Y%m%d")

with st.spinner('조회중입니다~'):
    if pd.read_xml(url)["list_total_count"].dropna().iloc[0] < 100000 :
        rawDf = pd.read_xml(url, xpath = "//row")
    else :
        rawDf_list = []

        first_cur_df_url = "https://ecos.bok.or.kr/api/" + 통계조회 +"/" + 인증키 + "/xml/kr/1/100000/" + 통계표코드 + "/" + "D" + "/" + start_d.strftime("%Y%m%d") + "/" + str(start_d.year) +"1231"
        first_cur_df = pd.read_xml(first_cur_df_url, xpath = "//row")
        rawDf_list.append(first_cur_df)
        
        for idx_year in range(start_d.year+1, end_d.year):
            loop_url = "https://ecos.bok.or.kr/api/" + 통계조회 +"/" + 인증키 + "/xml/kr/1/100000/" + 통계표코드 + "/" + "D" + "/" + str(idx_year) +"0101" + "/" + str(idx_year) + "1231"
            curDf = pd.read_xml(loop_url, xpath = "//row")
            rawDf_list.append(curDf)
            
        last_cur_df_url = "https://ecos.bok.or.kr/api/" + 통계조회 +"/" + 인증키 + "/xml/kr/1/100000/" + 통계표코드 + "/" + "D" + "/" + str(end_d.year) +"0101" + "/" + end_d.strftime("%Y%m%d")
        last_cur_df = pd.read_xml(last_cur_df_url, xpath = "//row")
        rawDf_list.append(last_cur_df)
        
        rawDf=pd.concat(rawDf_list)
#%% 스프레드 만들기

interestRate_Df = rawDf[["ITEM_NAME1", "TIME", "DATA_VALUE"]].dropna().pivot(index = "TIME", columns = "ITEM_NAME1", values ="DATA_VALUE")
interestRate_Df.index = pd.to_datetime(interestRate_Df.index, format='%Y%m%d')
if 조회주기 != "일":
    interestRate_Df = interestRate_Df.dropna().resample("D").ffill().resample(resample_key[조회주기]).ffill()
# =============================================================================
# 'CD(91일)', 'CMA(수시형)', 'CP(91일)', 'KORIBOR(12개월)', 'KORIBOR(3개월)',
# 'KORIBOR(6개월)', 'MMF(7일)', '국고채(10년)', '국고채(1년)', '국고채(20년)', '국고채(2년)',
# '국고채(30년)', '국고채(3년)', '국고채(50년)', '국고채(5년)', '국민주택채권1종(5년)', '산금채(1년)',
# '콜금리(1일, 은행증권금융차입)', '콜금리(1일, 전체거래)', '콜금리(1일, 중개회사거래)', '통안증권(1년)',
# '통안증권(2년)', '통안증권(91일)', '회사채(3년, AA-)', '회사채(3년, AA-, 민평)',
# '회사채(3년, BBB-)'
# =============================================================================
spreadRate_Df = pd.DataFrame()

spreadRate_Df["creditSpread (AA-)"] = interestRate_Df['회사채(3년, AA-)'] - interestRate_Df['국고채(3년)']
spreadRate_Df["creditSpread (BBB-)"] = interestRate_Df['회사채(3년, BBB-)'] - interestRate_Df['국고채(3년)']
#spreadRate_Df["creditSpread (AA- 민평)"] = interestRate_Df['회사채(3년, AA-, 민평)'] - interestRate_Df['국고채(3년)']



spreadRate_Df["timeSpread ( 국고채 3년 - Call금리(전체) )"] = interestRate_Df['국고채(3년)'] - interestRate_Df['콜금리(1일, 전체거래)']
spreadRate_Df["timeSpread ( 국고채 5년 - Call금리(전체) )"] = interestRate_Df['국고채(5년)'] - interestRate_Df['콜금리(1일, 전체거래)']
spreadRate_Df["timeSpread ( 국고채 10년 - Call금리(전체) )"] = interestRate_Df['국고채(10년)'] - interestRate_Df['콜금리(1일, 전체거래)']

spreadRate_Df["timeSpread ( 국고채 3년 - CD(91일) )"] = interestRate_Df['국고채(3년)'] - interestRate_Df['CD(91일)']
spreadRate_Df["timeSpread ( 국고채 5년 - CD(91일) )"] = interestRate_Df['국고채(5년)'] - interestRate_Df['CD(91일)']
spreadRate_Df["timeSpread ( 국고채 10년 - CD(91일) )"] = interestRate_Df['국고채(10년)'] - interestRate_Df['CD(91일)']

spreadRate_Df["timeSpread ( 국고채 3년 - 국고채 1년 )"] = interestRate_Df['국고채(3년)'] - interestRate_Df['국고채(1년)']
spreadRate_Df["timeSpread ( 국고채 5년 - 국고채 1년 )"] = interestRate_Df['국고채(5년)'] - interestRate_Df['국고채(1년)']
spreadRate_Df["timeSpread ( 국고채 10년 - 국고채 1년 )"] = interestRate_Df['국고채(10년)'] - interestRate_Df['국고채(1년)']

spreadRate_Df["timeSpread ( 국고채 5년 - 통안채 2년 )"] = interestRate_Df['국고채(5년)'] - interestRate_Df['통안증권(2년)']
spreadRate_Df["timeSpread ( 국고채 10년 - 통안채 2년 )"] = interestRate_Df['국고채(10년)'] - interestRate_Df['통안증권(2년)']

spreadRate_Df["timeSpread ( 국고채 5년 - 국고채 3년 )"] = interestRate_Df['국고채(5년)'] - interestRate_Df['국고채(3년)']
spreadRate_Df["timeSpread ( 국고채 10년 - 국고채 3년 )"] = interestRate_Df['국고채(10년)'] - interestRate_Df['국고채(3년)']


#%% 스프레드 선 차트

fig = px.line(spreadRate_Df, 
              labels={"value": "금리 (%)"},
              title="스프레드 그래프"
              )
st.plotly_chart(fig, use_container_width = True)


#%% streamlit csv 변환 함수 - cash 조정

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


#%% 금리 DataFrame 위젯 (연이율) - 다운 가능

intRate_csv = convert_df(interestRate_Df)
spread_csv = convert_df(spreadRate_Df)

st.header(" 시트 데이터 ")
st.caption("로딩에 매우 많은 시간이 걸릴 수 있습니다.")
sheet_column = st.columns(2)

    

with sheet_column[0] :
    st.subheader(" 금리 데이터 시트 ")
    AgGrid(interestRate_Df.reset_index(), 
           height = 300,
           )
    
    st.download_button(
        label="CSV파일 다운로드",
        data=intRate_csv,
        file_name='금리_byMr21.csv',
        mime='text/csv',
        )
    
with sheet_column[1] :
    st.subheader(" 스프레드 데이터 시트 ")
    AgGrid(spreadRate_Df.reset_index(), 
           height = 300,)
    st.download_button(
        label="CSV파일 다운로드",
        data=spread_csv,
        file_name='스프레드_byMr21.csv',
        mime='text/csv',
    )