import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# 🌍 UNSDCF Evaluation Dashboard
# ==========================================================
st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")

st.title("🌍 United Nations Sustainable Development Cooperation Framework Evaluation Dashboard")

st.markdown("""
This dashboard visualizes **evaluation expenditures**, **synthesized findings**, 
and **text analysis** from UNSDCF evaluations under OECD-DAC criteria.
---
""")

# ==========================================================
# 📊 PART I: Evaluation Expenditures Visualization
# ==========================================================
st.header("Part I: Evaluation Expenditure Visualization")

# ----------------------------------------------------------
# 📂 Load & Clean Data
# ----------------------------------------------------------
file_path = "2021-2023evaluationexpendituresanalysis.xlsx"

try:
    df_spend = pd.read_excel(file_path)
    # 清理隐藏空格和多余空格
    df_spend.columns = df_spend.columns.str.strip().str.replace(r"\s+", " ", regex=True)

    # 重命名列
    df_spend.rename(columns={
        "Evaluation expenditure($)": "Evaluation Spending ($)",
        "Program Expenditure": "Program Expenditure",
        "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)"
    }, inplace=True)

    # 确保数值列为数值型
    for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
        if c in df_spend.columns:
            df_spend[c] = pd.to_numeric(df_spend[c], errors="coerce")

    df_spend.dropna(subset=["Eval Ratio (%)"], inplace=True)

    st.success("✅ Data loaded successfully!")
    st.write("**Loaded columns:**", list(df_spend.columns))

except Exception as e:
    st.error(f"❌ Failed to load data: {e}")

# ----------------------------------------------------------
# 🌍 Global Evaluation Map
# ----------------------------------------------------------
try:
    st.subheader("🌍 Global Evaluation Map (2021–2023)")
    st.markdown("This map visualizes all countries that completed evaluations between 2021–2023.")

    fig_map = px.scatter_geo(
        df_spend,
        locations="Country",
        locationmode="country names",
        hover_name="Country",
        hover_data={"Evaluation year": True, "Eval Ratio (%)": True},
        text="Evaluation year",
        projection="natural earth",
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig_map, use_container_width=True)
except Exception as e:
    st.error(f"❌ Failed to load data for map: {e}")

# ----------------------------------------------------------
# 💰 Scatter Plot: Evaluation vs Program Expenditure
# ----------------------------------------------------------
try:
    st.subheader("💰 Evaluation vs Programme Expenditure")
    st.markdown("Each bubble shows one country’s evaluation ratio compared with total programme expenditure.")

    # 确保 Eval Ratio 是百分比
    if df_spend["Eval Ratio (%)"].max() <= 1:
        df_spend["Eval Ratio (%)"] = df_spend["Eval Ratio (%)"] * 100

    fig_scatter = px.scatter(
        df_spend,
        x="Program Expenditure",
        y="Eval Ratio (%)",
        size="Evaluation Spending ($)",
        color="Region" if "Region" in df_spend.columns else "Country",
        hover_name="Country",
        template="plotly_white",
        size_max=40
    )

    fig_scatter.update_layout(
        xaxis_title="Program Expenditure (USD)",
        yaxis_title="Evaluation Ratio (%)",
        yaxis_ticksuffix="%",
        plot_bgcolor="white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
except Exception as e:
    st.error(f"❌ Failed to load scatter plot: {e}")

# ----------------------------------------------------------
# 📈 OECD-DAC Radar Chart
# ----------------------------------------------------------
st.header("Part II: Synthesizing the Evaluation Findings")

st.subheader("🕸️ Radar Chart on OECD-DAC Criteria")
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
                          r="Score", theta="Criterion", line_close=True,
                          color_discrete_sequence=["#1f77b4"])
st.plotly_chart(fig_radar, use_container_width=True)

# ----------------------------------------------------------
# 🧠 Text Analysis Section (Placeholder)
# ----------------------------------------------------------
st.header("Part III: Text Analysis of Evaluations")
st.markdown("""
This section analyzes extracted text data from UNSDCF evaluation reports, focusing on **DCO**, **RC**, and **UNCT** mentions.
""")

try:
    df_mentions = pd.read_csv("relevant_sentences_UNSDCF.csv")
    df_words = pd.read_csv("word_frequency_UNSDCF.csv")

    st.subheader("📑 Sample Extracted Mentions")
    st.dataframe(df_mentions.head(10))

    st.subheader("📊 Sentiment Distribution")
    sent_summary = df_mentions.groupby(["Entity", "Sentiment_Label"]).size().reset_index(name="Count")
    fig_sent = px.bar(
        sent_summary,
        x="Entity",
        y="Count",
        color="Sentiment_Label",
        barmode="group",
        template="plotly_white",
        title="Sentiment Distribution by Entity (RC / UNCT / DCO)"
    )
    st.plotly_chart(fig_sent, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Text analysis results not found or failed to load: {e}")

st.markdown("---")
st.markdown("© United Nations DCO – Data visualization for learning purposes")
