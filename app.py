# ==========================================================
# 🌍 UNSDCF Evaluation Dashboard (Stable Version for Zoya)
# ==========================================================
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------
# 🧭 Page Setup
# ----------------------------------------------------------
st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")
st.title("🌍 United Nations Sustainable Development Cooperation Framework Evaluation Dashboard")

# ----------------------------------------------------------
# 📊 Load and Clean Data
# ----------------------------------------------------------
file_path = "2021-2023 evaluationexpendituresanalysis .xlsx"

try:
    df_spend = pd.read_excel(file_path)
    df_spend.columns = df_spend.columns.str.strip()  # 去除隐藏空格
    st.success("✅ Data loaded successfully!")
    st.write("**Loaded columns:**", list(df_spend.columns))
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# rename 列名（注意空格）
rename_map = {
    "Evaluation expenditure($)": "Evaluation Spending ($)",
    "Program  Expenditure": "Program Expenditure",  # 双空格非常重要
    "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)"
}
df_spend.rename(columns=rename_map, inplace=True)

# 检查关键列
required_cols = ["Country", "Region", "Evaluation year", "Evaluation Spending ($)",
                 "Program Expenditure", "Eval Ratio (%)"]
missing = [c for c in required_cols if c not in df_spend.columns]
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.stop()

# 转换数据类型
for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
    df_spend[c] = pd.to_numeric(df_spend[c], errors="coerce")
df_spend.dropna(subset=["Eval Ratio (%)"], inplace=True)

# ----------------------------------------------------------
# 🌍 Global Evaluation Map
# ----------------------------------------------------------
st.subheader("🌍 Evaluation Countries (2021–2023)")

try:
    fig_map = px.scatter_geo(
        df_spend,
        locations="Country",
        locationmode="country names",
        color="Region",
        size="Evaluation Spending ($)",
        hover_data={
            "Region": True,
            "Evaluation year": True,
            "Program Expenditure": True,
            "Eval Ratio (%)": True
        },
        projection="natural earth"
    )
    st.plotly_chart(fig_map, use_container_width=True)
except Exception as e:
    st.warning(f"⚠️ Map could not be displayed: {e}")

# ----------------------------------------------------------
# 💰 Evaluation Expenditure vs Programme Spending
# ----------------------------------------------------------
st.subheader("💰 Evaluation vs Programme Expenditure")
fig_scatter = px.scatter(
    df_spend,
    x="Program Expenditure",
    y="Eval Ratio (%)",
    size="Evaluation Spending ($)",
    color="Region",
    hover_name="Country",
    hover_data={"Evaluation year": True},
    title="Evaluation Investment Ratio by Country"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ----------------------------------------------------------
# 📈 Radar Chart (OECD-DAC Criteria)
# ----------------------------------------------------------
st.subheader("📈 OECD-DAC Performance by Country")

CRITERIA = ['Relevance', 'Coherence', 'Effectiveness', 'Efficiency',
            'Orientation towards Impact', 'Sustainability']
countries_eval = ["Azerbaijan", "Uganda", "Serbia", "Indonesia", "Panama", "Bosnia and Herzegovina"]
scores = {
    "Azerbaijan": [4, 3, 4, 3, 3, 3],
    "Uganda": [4, 2, 4, 3, 3, 3],
    "Serbia": [4, 2, 4, 3, 3, 3],
    "Indonesia": [5, 3, 4, 3, 4, 3],
    "Panama": [4, 3, 3, 3, 3, 2],
    "Bosnia and Herzegovina": [4, 2, 4, 3, 3, 3]
}

df_scores = pd.DataFrame([
    {"Country": c, "Criterion": crit, "Score": scores[c][i]}
    for c in countries_eval for i, crit in enumerate(CRITERIA)
])

country = st.sidebar.selectbox("Select Country", countries_eval)
fig_radar = px.line_polar(
    df_scores[df_scores["Country"] == country],
    r="Score",
    theta="Criterion",
    line_close=True,
    range_r=[0, 5],
    title=f"OECD-DAC Criteria Performance — {country}"
)
fig_radar.update_traces(fill='toself')
st.plotly_chart(fig_radar, use_container_width=True)

# ----------------------------------------------------------
# 🧠 Text Analysis Placeholder (可选模块)
# ----------------------------------------------------------
st.subheader("🧠 Text Analysis (Pilot Section)")
st.info("""
This module is designed for analyzing qualitative insights from evaluation reports.
If a CSV file with extracted text (e.g. `/content/relevant_sentences_UNSDCF.csv`) is available,
it can be loaded and visualized here in the future version.
""")

