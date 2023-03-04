# Libraries
import streamlit as st


# Confit
st.set_page_config(page_title='Cross Chain Monitoring Tool', page_icon=':bar_chart:', layout='wide')

# Title
st.title('자료 모음')

# Content

st.write(
    """
    경제관련자료 집합 : 현재는 api에서 확보한 자료를 csv 형태로 보관해서 사용하고 있습니다.
    추후에 api에 매번 접속하는 방향으로 수정하도록 하겠습니다
    """
)

st.subheader('21프로')
