import pandas as pd
import numpy as np
import streamlit as st
import altair as alt


data = "data/df.csv"

df = pd.read_csv(data)

st.title("Blocker Fraud Comapny")
st.markdown(
"""
	**Dashboard with Predictions**
"""
)


#sidebar
st.sidebar.header("Filters")
st.sidebar.subheader("Transactions")

if st.sidebar.checkbox("Legitimate Transactions"):
	x = df[df['prediction'] == 0]
	st.write(x)

if st.sidebar.checkbox("Fraudulent Transactions"):
	x = df[df['prediction'] == 1]
	st.write(x)
	
st.sidebar.subheader("Amount")
entradas_selecionadas = st.empty()
amount = st.sidebar.slider("Select Amount", 0,2093400, 145047)
df_filtered = df[df['amount'] == amount]
entradas_selecionadas.text(df_filtered.shape[0])
c = alt.Chart(df).mark_circle().encode(x='step', y='amount')
st.write(c)

st.line_chart(df['error_balance_orig'])
