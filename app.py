import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# 📘 UNSDCF Evaluation Dashboard + Text Analysis
# ==========================================================
st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")

st.title("🌍 United Nations Sustainable Development Cooperation Framework Evaluation Dashboard")

# ----------------------------------------------------------
# 📊 加载 Evaluation Expenditure 数据
# ----------------------------------------------------------
file_path = "2021-2023_evaluation_expenditures_analysis.xlsx"
df_spend = pd.read_excel(file_path)
df_spend.columns = df_spend.columns.str.strip()
df_spend.rename(columns={
    "Evaluation expenditure($)": "Evaluation Spending ($)",
    "Program Expenditure": "Program Expenditure",
    "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)"
}, inplace=True)
for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
    df_spend[c] = pd.to_numeric(df_spend[c], errors="coerce")
df_spend.dropna(subset=["Eval Ratio (%)"], inplace=True)

# ----------------------------------------------------------
# 🌍 地图
# ----------------------------------------------------------
st.subheader("🌍 Evaluation Countries (2021–2023)")
fig_map = px.scatter_geo(df_spend, locations="Country", locationmode="country names",
                         hover_name="Country", hover_data={"Evaluation year ": True},
                         text="Evaluation year ", projection="natural earth")
st.plotly_chart(fig_map, use_container_width=True)

# ----------------------------------------------------------
# 💰 散点图
# ----------------------------------------------------------
st.subheader("💰 Evaluation vs Programme Expenditure")
fig_scatter = px.scatter(df_spend, x="Program Expenditure", y="Eval Ratio (%)",
                         size="Evaluation Spending ($)",
                         color="Region" if "Region" in df_spend.columns else "Country",
                         hover_name="Country")
st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------------------------------------------------
# 📈 雷达图
# ----------------------------------------------------------
CRITERIA = ['relevance','coherence','effectiveness','efficiency','orientation towards impact','sustainability']
countries_eval = ["Azerbaijan","Uganda","Serbia","Indonesia","Panama","Bosnia and Herzegovina"]
scores = {
    "Azerbaijan":[4,3,4,3,3,3],
    "Uganda":[4,2,4,3,3,3],
    "Serbia":[4,2,4,3,3,3],
    "Indonesia":[5,3,4,3,4,3],
    "Panama":[4,3,3,3,3,2],
    "Bosnia and Herzegovina":[4,2,4,3,3,3]
}
df_scores = pd.DataFrame([{"Country":c,"Criterion":crit,"Score":scores[c][i]}
                          for c in countries_eval for i,crit in enumerate(CRITERIA)])
country = st.sidebar.selectbox("Select Country", countries_eval)
fig_radar = px.line_polar(df_scores[df_scores["Country"]==country],
                          r="Score", theta="Criterion", line_close=True)
st.plotly_chart(fig_radar, use_container_width=True)
