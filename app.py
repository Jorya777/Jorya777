# ==========================================================
# 🌍 UNSDCF Evaluation Dashboard (Final Version)
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------
#  Page Config
# ----------------------------------------------------------
st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")

st.title("🌍 United Nations Sustainable Development Cooperation Framework (UNSDCF) Evaluation Dashboard")

# ----------------------------------------------------------
# File Paths 
# ----------------------------------------------------------
EXP_FILE = "2021-2023evaluationexpendituresanalysis.xlsx"
TEXT_FILE = "relevant_sentences_UNSDCF_filtered.csv"
WORD_FILE = "word_frequency_UNSDCF.csv"

# ----------------------------------------------------------
# 🧭 Sidebar Navigation
# ----------------------------------------------------------
st.sidebar.title("🔍 Navigation")
page = st.sidebar.radio(
    "Select Section:",
    [
        "Part I: Evaluation Implementation",
        "Part II: Synthesizing Evaluation Findings",
        "Part III: Text Analysis of Evaluations"
    ]
)

# ==========================================================
# 📊 PART I: Evaluation Implementation
# ==========================================================
if page == "Part I: Evaluation Implementation":
    st.header("Part I: Visualizing the Implementation of Evaluations")

    # Load Data
    df_spend = pd.read_excel(EXP_FILE)
    df_spend.columns = df_spend.columns.str.strip()

    df_spend.rename(columns={
        "Evaluation expenditure($)": "Evaluation Spending ($)",
        "Program Expenditure": "Program Expenditure",
        "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)"
    }, inplace=True)

    # Ensure numeric and percentage format
    for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
        df_spend[c] = pd.to_numeric(df_spend[c], errors="coerce")
    df_spend.dropna(subset=["Eval Ratio (%)"], inplace=True)

    # Convert ratio to percentage (if < 1)
    if df_spend["Eval Ratio (%)"].max() < 1:
        df_spend["Eval Ratio (%)"] = df_spend["Eval Ratio (%)"] * 100

    # 🌍 Map
    st.subheader("🌍 Global Evaluation Map")
    st.markdown("A scatter-geo map visualizing all countries that completed evaluations between 2021–2023.")

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

    # 💰 Scatter Plot
    st.subheader("💰 Evaluation Expenditure vs Programme Expenditure")
    st.markdown("This scatter plot compares total program expenditure with evaluation ratios (in %), sized by evaluation spending.")

    fig_scatter = px.scatter(
        df_spend,
        x="Program Expenditure",
        y="Eval Ratio (%)",
        size="Evaluation Spending ($)",
        color="Region" if "Region" in df_spend.columns else "Country",
        hover_name="Country",
        labels={"Eval Ratio (%)": "Evaluation Ratio (%)"},
        template="plotly_white"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================================
# 📈 PART II: Synthesizing Evaluation Findings
# ==========================================================
elif page == "Part II: Synthesizing Evaluation Findings":
    st.header("Part II: Synthesizing the Evaluation Findings")

    # 🕸️ Radar Chart
    st.subheader("🕸️ OECD-DAC Criteria Performance")
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
    df_scores = pd.DataFrame([{"Country":c,"Criterion":crit,"Score":scores[c][i]} for c in countries_eval for i,crit in enumerate(CRITERIA)])
    country = st.sidebar.selectbox("Select Country", countries_eval)
    fig_radar = px.line_polar(df_scores[df_scores["Country"]==country], r="Score", theta="Criterion", line_close=True, color_discrete_sequence=["#1f77b4"])
    st.plotly_chart(fig_radar, use_container_width=True)

    # 🔴🔵 Symmetrical Bar
    st.subheader("🔴🔵 Strengths vs Weaknesses of UNCT Evaluations")
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
    fig_balance = px.bar(df_bal, x="Frequency", y="Aspect", color="Type",
                         color_discrete_map={"Strength":"steelblue","Weakness":"#d62728"},
                         orientation="h", template="plotly_white")
    fig_balance.update_layout(title="Strengths (Blue, Right) vs Weaknesses (Red, Left)",
                              yaxis=dict(title=None), xaxis=dict(title="Frequency of Mentions", showgrid=False))
    st.plotly_chart(fig_balance, use_container_width=True)

# ==========================================================
# 🧠 PART III: Text Analysis of Evaluations
# ==========================================================
elif page == "Part III: Text Analysis of Evaluations":
    st.header("Part III: Text Analysis of Evaluations")

    try:
        df_mentions = pd.read_csv(TEXT_FILE)
        df_words = pd.read_csv(WORD_FILE)

        st.markdown("""
        This section visualizes AI-assisted text analysis results from UNSDCF evaluation reports, 
        focusing on mentions of **RC (Resident Coordinator)**, **UNCT (UN Country Team)**, and **DCO (Development Coordination Office)**.
        """)

        # 📑 Table preview
        st.subheader("📑 Sample Extracted Sentences")
        st.dataframe(df_mentions[["Country","Actor","Sentiment_Label","Sentence"]].head(10))

        # 📊 Sentiment Distribution by Actor
        st.subheader("📊 Sentiment Distribution by Actor")
        sent_summary = df_mentions.groupby(["Actor","Sentiment_Label"]).size().reset_index(name="Count")
        fig_sent = px.bar(sent_summary, x="Actor", y="Count", color="Sentiment_Label",
                          barmode="group", template="plotly_white",
                          color_discrete_map={"Positive":"#1f77b4","Neutral":"#7f7f7f","Negative":"#d62728"})
        st.plotly_chart(fig_sent, use_container_width=True)

        # 🔤 Keyword Frequency
        st.subheader("🔤 Keyword Frequency in Mentions")
        top_words = df_words.head(20)
        fig_words = px.bar(top_words, x="word", y="count", color="count",
                           title="Top 20 Keywords in Evaluation Mentions", template="plotly_white")
        st.plotly_chart(fig_words, use_container_width=True)

    except Exception as e:
        st.warning(f"⚠️ Text analysis results not found or failed to load: {e}")

# ==========================================================
st.markdown("---")
st.markdown("© United Nations DCO — Data Visualization for Learning Purposes (Built with Python & Streamlit)")
