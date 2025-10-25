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

try:
    # 明确 header 并清理空格
    df_spend = pd.read_excel(file_path, header=0)
    df_spend.columns = df_spend.columns.str.strip()

    # 打印调试信息（在 Streamlit Cloud 上方便看列名）
    st.write("✅ Loaded columns:", df_spend.columns.tolist())

    # 自动识别相似列名，防止 KeyError
    rename_map = {}
    for col in df_spend.columns:
        col_lower = col.lower().replace(" ", "")
        if "evaluation" in col_lower and "expenditure" in col_lower and "$" in col_lower:
            rename_map[col] = "Evaluation Spending ($)"
        elif "program" in col_lower and "expenditure" in col_lower:
            rename_map[col] = "Program Expenditure"
        elif "proportion" in col_lower or "ratio" in col_lower:
            rename_map[col] = "Eval Ratio (%)"

    df_spend.rename(columns=rename_map, inplace=True)

    # 确保关键列存在
    required_cols = ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]
    missing = [c for c in required_cols if c not in df_spend.columns]
    if missing:
        st.error(f"❌ Missing required columns: {missing}")
    else:
        for c in required_cols:
            df_spend[c] = pd.to_numeric(df_spend[c], errors="coerce")
        df_spend.dropna(subset=["Eval Ratio (%)"], inplace=True)

except Exception as e:
    st.error(f"⚠️ Error loading Excel file: {e}")
    st.stop()

# ----------------------------------------------------------
# 🌍 地图
# ----------------------------------------------------------
st.subheader("🌍 Evaluation Countries (2021–2023)")
if "Country" in df_spend.columns:
    fig_map = px.scatter_geo(
        df_spend,
        locations="Country",
        locationmode="country names",
        hover_name="Country",
        hover_data={"Evaluation year ": True} if "Evaluation year " in df_spend.columns else None,
        text="Evaluation year " if "Evaluation year " in df_spend.columns else None,
        projection="natural earth",
    )
    st.plotly_chart(fig_map, use_container_width=True)
else:
    st.warning("⚠️ Column 'Country' not found in dataset. Please verify the Excel file.")

# ----------------------------------------------------------
# 💰 散点图
# ----------------------------------------------------------
st.subheader("💰 Evaluation vs Programme Expenditure")
if all(c in df_spend.columns for c in ["Program Expenditure", "Eval Ratio (%)", "Evaluation Spending ($)"]):
    color_col = "Region" if "Region" in df_spend.columns else "Country"
    fig_scatter = px.scatter(
        df_spend,
        x="Program Expenditure",
        y="Eval Ratio (%)",
        size="Evaluation Spending ($)",
        color=color_col,
        hover_name="Country" if "Country" in df_spend.columns else None,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.warning("⚠️ Missing data for scatter plot.")

# ----------------------------------------------------------
# 📈 雷达图
# ----------------------------------------------------------
st.subheader("📈 UNCT Performance across OECD-DAC Criteria")

CRITERIA = ['relevance', 'coherence', 'effectiveness', 'efficiency', 'orientation towards impact', 'sustainability']
countries_eval = ["Azerbaijan", "Uganda", "Serbia", "Indonesia", "Panama", "Bosnia and Herzegovina"]
scores = {
    "Azerbaijan": [4, 3, 4, 3, 3, 3],
    "Uganda": [4, 2, 4, 3, 3, 3],
    "Serbia": [4, 2, 4, 3, 3, 3],
    "Indonesia": [5, 3, 4, 3, 4, 3],
    "Panama": [4, 3, 3, 3, 3, 2],
    "Bosnia and Herzegovina": [4, 2, 4, 3, 3, 3],
}
df_scores = pd.DataFrame(
    [{"Country": c, "Criterion": crit, "Score": scores[c][i]} for c in countries_eval for i, crit in enumerate(CRITERIA)]
)

country = st.sidebar.selectbox("Select Country", countries_eval)
fig_radar = px.line_polar(
    df_scores[df_scores["Country"] == country],
    r="Score",
    theta="Criterion",
    line_close=True,
    title=f"OECD-DAC Criteria Performance: {country}",
)
fig_radar.update_traces(fill='toself')
st.plotly_chart(fig_radar, use_container_width=True)

