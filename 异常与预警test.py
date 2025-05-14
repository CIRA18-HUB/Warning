import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="测试应用", layout="wide")

st.title("测试应用")

# 列出当前目录的文件
st.subheader("当前目录文件")
files = os.listdir(".")
st.write(files)

# 尝试加载一个文件
try:
    st.subheader("尝试加载Excel文件")
    if "单价.xlsx" in files:
        df = pd.read_excel("单价.xlsx")
        st.write(df.head())
    else:
        st.warning("未找到单价.xlsx文件")
except Exception as e:
    st.error(f"加载文件时出错: {str(e)}")