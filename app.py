import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# 🌍 UNSDCF Evaluation Dashboard
# ==========================================================
st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")
st.title("🌍 United Nations Sustainable Development Cooperation Framework Evaluation Dashboard")

# ==========================================================
# 📊 PART I: Visualizing the Implementation of Evaluations
# ==========================================================
st.header("Part I: Visualizing the Implementation of Evaluations")

# ----------------------------------------------------------
# 📘 Load and Clean Data
# ----------------------------------------------------------
file_path = "2021-2023evaluationexpendituresanalysis.xlsx"

try:
    df_spend = pd.read_excel(file_path)
    df_spend.columns = df_spend.columns.str.strip()

    df_spend.rename(columns={
        "Evaluation expenditure($)": "Evaluation Spending ($)",
        "Program  Expenditure": "Program Expenditure",
        "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)"
    }, inplace=True)

    for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
        df_spend[c] = pd.to_numeric(df_spend[c], errors="coerce")
    df_spend.dropna(subset=["Eval Ratio (%)"], inplace=True)

    st.success("✅ Data loaded successfully!")
except Exception as e:
    st.error(f"❌ Failed to load data: {e}")
    st.stop()

# ----------------------------------------------------------
# 🌍 Global Evaluation Map
# ----------------------------------------------------------
st.subheader("🌍 Global Evaluation Map")
st.markdown("A scatter-geo map visualizing all countries that completed evaluations between 2021–2023. Hovering over a country displays its evaluation year and expenditure ratio.")

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

# ----------------------------------------------------------
# 💰 Expenditure Scatter Plot
# ----------------------------------------------------------
st.subheader("💰 Expenditure Scatter Plot")
st.markdown("This scatter plot compares total program expenditure with evaluation ratios, sized by evaluation spending. It provides a quick way to identify under- or over-investment in evaluation relative to total programme budgets.")

fig_scatter = px.scatter(
    df_spend,
    x="Program Expenditure",
    y="Eval Ratio (%)",
    size="Evaluation Spending ($)",
    color="Region" if "Region" in df_spend.columns else "Country",
    hover_name="Country",
    template="plotly_white"
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================================
# 📈 PART II: Synthesizing the Evaluation Findings
# ==========================================================
st.header("Part II: Synthesizing the Evaluation Findings")

# ----------------------------------------------------------
# 🕸️ Radar Chart on OECD-DAC Criteria
# ----------------------------------------------------------
st.subheader("🕸️ Radar Chart on OECD-DAC Criteria")
st.markdown("""
Based on a synthesized scoring from six evaluation reports, this radar chart 
shows performance across six OECD-DAC criteria — relevance, coherence, effectiveness, efficiency, orientation towards impact, and sustainability.
Users can select a country in the sidebar to dynamically update the radar.
""")

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
df_scores = pd.DataFrame([
    {"Country":c,"Criterion":crit,"Score":scores[c][i]}
    for c in countries_eval for i,crit in enumerate(CRITERIA)
])
country = st.sidebar.selectbox("Select Country", countries_eval)
fig_radar = px.line_polar(
    df_scores[df_scores["Country"]==country],
    r="Score", theta="Criterion", line_close=True,
    color_discrete_sequence=["#1f77b4"]
)
st.plotly_chart(fig_radar, use_container_width=True)

# ----------------------------------------------------------
# 🔴🔵 Symmetrical Red-Blue Bar Chart
# ----------------------------------------------------------
st.subheader("🔴🔵 Symmetrical Red-Blue Bar Chart")
st.markdown("""
This dual-axis bar chart summarizes common strengths and weaknesses across UNCT evaluations. 
Strengths appear in blue on the right, weaknesses in red on the left. 
Each bar’s length reflects the frequency of occurrence across reports, offering a visual balance between positive and negative patterns.
""")

strengths = [
    ("Aligned with national priorities and SDG frameworks", 5),
    ("Trusted as neutral conveners between government and partners", 4),
    ("Systematic gender and LNOB integration", 4),
    ("Evidence-based policymaking and SDG data", 3),
    ("High government ownership and long-term partnership", 5)
]
weaknesses = [
    ("Fragmented programming across agencies", 5),
    ("Weak Theory of Change linking outcomes", 4),
    ("Limited joint resource mobilization", 4),
    ("Output-focused monitoring and learning", 3),
    ("Low visibility of UNCT results", 5)
]

df_strength = pd.DataFrame(strengths, columns=["Aspect","Frequency"])
df_strength["Type"] = "Strength"
df_weak = pd.DataFrame(weaknesses, columns=["Aspect","Frequency"])
df_weak["Frequency"] = -df_weak["Frequency"]
df_weak["Type"] = "Weakness"
df_bal = pd.concat([df_strength, df_weak])

fig_balance = px.bar(
    df_bal,
    x="Frequency", y="Aspect", color="Type",
    color_discrete_map={"Strength":"steelblue","Weakness":"#d62728"},
    orientation="h",
    template="plotly_white"
)
fig_balance.update_layout(
    title="Strengths (Blue, Right) vs Weaknesses (Red, Left)",
    yaxis=dict(title=None),
    xaxis=dict(title="Frequency of Mentions", showgrid=False),
    plot_bgcolor="white",
    height=600
)
st.plotly_chart(fig_balance, use_container_width=True)

# ==========================================================
# 🧠 PART III: Text Analysis of Evaluations
# ==========================================================
st.header("Part III: Text Analysis of Evaluations")
st.markdown("""
Using the preprocessed CSV files (`relevant_sentences_UNSDCF.csv` and `word_frequency_UNSDCF.csv`),
this module presents:
- A sample of extracted sentences mentioning DCO / RC / UNCT
- Sentiment distribution (positive, neutral, negative)
- A keyword frequency chart built from word counts
""")

try:
    df_mentions = pd.read_csv("relevant_sentences_UNSDCF.csv")
    df_words = pd.read_csv("word_frequency_UNSDCF.csv")

    st.subheader("📑 Sample Extracted Mentions")
    st.dataframe(df_mentions.head(10))

    st.subheader("📊 Sentiment Distribution")
    if "Sentiment_Label" in df_mentions.columns:
        sent_summary = df_mentions.groupby("Sentiment_Label").size().reset_index(name="Count")
        fig_sent = px.bar(sent_summary, x="Sentiment_Label", y="Count", color="Sentiment_Label", template="plotly_white")
        st.plotly_chart(fig_sent, use_container_width=True)

    st.subheader("🔤 Keyword Frequency in Mentions")
    top_words = df_words.head(20)
    fig_words = px.bar(top_words, x="word", y="count", color="count",
                       title="Top 20 Keywords in DCO/RC/UNCT Mentions", template="plotly_white")
    st.plotly_chart(fig_words, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Text analysis results not found or failed to load: {e}")

st.markdown("---")
st.markdown("© United Nations DCO – Data visualization for learning purposes")

