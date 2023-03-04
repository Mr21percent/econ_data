import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import plotly.io as io
io.renderers.default='browser' #이거 해야 ploty 실시간 확인 가능 fig.show()가 인터넷 창에
st.set_page_config(page_title='월간수출입통계',  layout='wide')
    


url = "https://apis.data.go.kr/1220000/Itemtrade/getItemtradeList?"
인증키 = "WELKs76NiwpOK8rD5mIq4CrEEgswzBhwJOEaVc9S5vkmJL7mMUF03SBfmchN9BdnZCERARnfKOVQPNfj8t8mXA=="
시작년월 = "202201"
종료년월 = "202212"
#시작과 종료의 조회기간은 1년이내 기간만 가능합니다
#final_url = url + "serviceKey=" + 인증키 + "&strtYymm=" + 시작년월 + "&endYymm=" + 종료년월
#print(final_url)
#curdf = pd.read_xml(final_url , xpath=".//item")

# 해당 데이터의 hsCode는 강제적으로 10자리로 고정되어있음
# 즉 상위항목을 따로 추려내기 위해서는 21 ---- 와 같은 정규식 사용 필요


#데이터 공공 api에서 가져오는 코드
# =============================================================================
# '''
#     df_list = []
#     for year in range(1995, 2024):
#         시작년월 = str(year) + "01"
#         종료년월 = str(year) + "12"
#         print(year)
#         request_url = url + "serviceKey=" + 인증키 + "&strtYymm=" + 시작년월 + "&endYymm=" + 종료년월
#         curdf = pd.read_xml(request_url , xpath=".//item")
#         df_list.append(curdf)
#     df = pd.concat(df_list)
#     
#     df.to_csv("data2.csv")
# '''
# =============================================================================
#%% 데이터 불러들이기
df = pd.read_csv("data2.csv", dtype={"hsCode": str, "statKor" : str}, low_memory=False)
code_df = pd.read_excel("관세청조회코드_v1.0.xlsx", sheet_name="품목코드", dtype = {"품목명": str, "품목코드" : str} )

#%%
st.header("관세청 품목식별 코드")
from st_aggrid import AgGrid,GridOptionsBuilder, ColumnsAutoSizeMode
AgGrid(code_df, 
       height = 300,
       columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)
#%%
# 지정 항목 조회 (어느정도로 할지 고민중 - 중분류 하분류)
st.header("항목 수출입 추세")
selected = st.selectbox("품목을 선택하세요", pd.unique(code_df["품목명"]))
code = code_df.query("품목명 == @selected")["품목코드"].iloc[0]
regex = "^" + str(code)
testDf = df.query("hsCode.str.match(@regex)")
testDf["Name(code)"] = testDf["statKor"] +" (" +  testDf["hsCode"] + ")"

#%%

column1 , column2 = st.columns(2)



수출입액수df =  pd.melt(testDf, id_vars=["Name(code)", "year"], value_vars=['expDlr', 'impDlr'])
수출입무게df = pd.melt(testDf, id_vars=["Name(code)", "year"], value_vars=['expWgt', 'impWgt'])
항목list = 수출입액수df["Name(code)"].unique()



fig1 = go.Figure()

fig1.update_layout(
    template="simple_white",
    title = "수출입 액수 ($)",
    xaxis=dict(title_text="기간"),
    yaxis=dict(title_text="금액"),
    barmode="stack",
)

for r in 항목list:
    plot_df = 수출입액수df[수출입액수df["Name(code)"] == r]
    fig1.add_trace(
        go.Bar(x=[plot_df.year, plot_df.variable], y=plot_df.value, name=r),
    )
    
column1.plotly_chart(fig1)


fig2 = go.Figure()

fig2.update_layout(
    template="simple_white",
    xaxis=dict(title_text="기간"),
    yaxis=dict(title_text="금액"),
    barmode="stack",
    title = "수출입 무게 (kg)",
)

for r in 항목list:
    plot_df = 수출입무게df[수출입액수df["Name(code)"] == r]
    fig2.add_trace(
        go.Bar(x=[plot_df.year, plot_df.variable], y=plot_df.value, name=r),
    )

column2.plotly_chart(fig2)

st.header("데이터 표")
st.write("""
         blaPayments : 무역수지
         expDlr : 수출액
         expWgt : 수출무게
         impDlr : 수입액
         impWgt : 수입무게
         statKor : 항목명
         hsCode : 품목코드
         year : Yyyy.M
         """)
AgGrid(testDf, height = 500,
       columns_auto_size_mode=ColumnsAutoSizeMode.FIT_CONTENTS)

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')

csv = convert_df(testDf)
st.download_button(
    label="CSV파일 다운로드",
    data=csv,
    file_name='수출입중량과액수.csv',
    mime='text/csv',
)
























