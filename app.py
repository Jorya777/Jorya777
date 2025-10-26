# UNSDCF Evaluation Dashboard (2021–2024)
# United Nations Development Coordination Office (DCO)

import streamlit as st
import pandas as pd
import plotly.express as px
import re

st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")

# ---- Header ----
st.markdown("""
<div style="
    background-color:#005EB8;
    padding:35px 45px;
    border-radius:12px;
    display:flex;
    align-items:center;">
    <img src="https://raw.githubusercontent.com/Jorya777/Jorya777/main/UNDCO_Logo_2020_Hz_RGB_White.png"
         style="height:95px; margin-right:30px;">
    <div>
        <h1 style="color:white; font-size:36px; margin:0;">
            UN Sustainable Development Cooperation Framework Evaluation Dashboard (2021–2024)
        </h1>
    </div>
</div>
""", unsafe_allow_html=True)

# file paths
EXP_FILE = "2021-2023evaluationexpendituresanalysis.xlsx"
TEXT_FILE = "relevant_sentences_UNSDCF.csv"
WORD_FILE = "word_frequency_UNSDCF.csv"

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "",
    ["Part I: Evaluation Implementation",
     "Part II: Synthesizing Evaluation Findings",
     "Part III: Text Analysis of Evaluations"]
)

# -------------------------------
# Part I
# -------------------------------
if page == "Part I: Evaluation Implementation":
    st.header("Part I: Visualizing the Implementation of Evaluations")

    try:
        df = pd.read_excel(EXP_FILE)
        df.columns = [re.sub(r'\s+', ' ', c).strip() for c in df.columns]

        rename_map = {
            "Evaluation expenditure($)": "Evaluation Spending ($)",
            "Evaluation Expenditure ($)": "Evaluation Spending ($)",
            "Evaluation Spending($)": "Evaluation Spending ($)",
            "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)",
            "Program Expenditure": "Program Expenditure"
        }

        prog_col = [c for c in df.columns if re.search("program.*expenditure", c, re.I)]
        if prog_col:
            rename_map[prog_col[0]] = "Program Expenditure"

        df.rename(columns=rename_map, inplace=True)

        for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df.dropna(subset=["Eval Ratio (%)"], inplace=True)
        if df["Eval Ratio (%)"].max() < 1:
            df["Eval Ratio (%)"] *= 100

        st.subheader("🌍 Global Evaluation Map (2021–2023)")
        fig_map = px.scatter_geo(
            df, locations="Country", locationmode="country names",
            hover_name="Country",
            hover_data={"Evaluation year": True, "Eval Ratio (%)": True},
            text="Evaluation year",
            projection="natural earth",
            color_discrete_sequence=["#0077C8"]
        )
        st.plotly_chart(fig_map, use_container_width=True)

        st.subheader("💰 Evaluation Expenditure vs Programme Expenditure")
        fig_scatter = px.scatter(
            df, x="Program Expenditure", y="Eval Ratio (%)",
            size="Evaluation Spending ($)",
            color="Region" if "Region" in df.columns else "Country",
            hover_name="Country",
            template="plotly_white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        st.error(f"Error loading data: {e}")

# -------------------------------
# Part II
# -------------------------------
elif page == "Part II: Synthesizing Evaluation Findings":
    st.header("Part II: Synthesizing the Evaluation Findings")

    CRITERIA = ['relevance', 'coherence', 'effectiveness', 'efficiency', 'orientation towards impact', 'sustainability']
    countries = ["Azerbaijan","Uganda","Serbia","Indonesia","Panama","Bosnia and Herzegovina"]
    scores = {
        "Azerbaijan":[4,3,4,3,3,3],
        "Uganda":[4,2,4,3,3,3],
        "Serbia":[4,2,4,3,3,3],
        "Indonesia":[5,3,4,3,4,3],
        "Panama":[4,3,3,3,3,2],
        "Bosnia and Herzegovina":[4,2,4,3,3,3]
    }

    df_scores = pd.DataFrame([
        {"Country":c, "Criterion":crit, "Score":scores[c][i]} 
        for c in countries for i, crit in enumerate(CRITERIA)
    ])

    country_sel = st.sidebar.selectbox("Select Country", countries)
    fig_radar = px.line_polar(df_scores[df_scores["Country"]==country_sel],
                              r="Score", theta="Criterion", line_close=True,
                              color_discrete_sequence=["#0077C8"])
    st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("Strengths and Weaknesses in UNCT Performance")
    strengths = [
        ("Aligned with national priorities and SDG frameworks", 5),
        ("Trusted as neutral conveners", 4),
        ("Systematic gender and LNOB integration", 4),
        ("Evidence-based policymaking", 3),
        ("High government ownership", 5)
    ]
    weaknesses = [
        ("Fragmented programming", 5),
        ("Weak Theory of Change", 4),
        ("Limited joint resource mobilization", 4),
        ("Output-focused monitoring", 3),
        ("Low visibility of results", 5)
    ]
    df_s = pd.DataFrame(strengths, columns=["Aspect","Value"])
    df_s["Type"] = "Strength"
    df_w = pd.DataFrame(weaknesses, columns=["Aspect","Value"])
    df_w["Value"] = -df_w["Value"]
    df_w["Type"] = "Weakness"
    df_comb = pd.concat([df_s, df_w])

    fig_bar = px.bar(df_comb, x="Value", y="Aspect", color="Type",
                     color_discrete_map={"Strength":"#005DA4","Weakness":"#C0392B"},
                     orientation="h", template="plotly_white")
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------
# Part III
# -------------------------------
elif page == "Part III: Text Analysis of Evaluations":
    st.header("Part III: Text Analysis of Evaluations")

    try:
        df_mentions = pd.read_csv(TEXT_FILE)
        df_words = pd.read_csv(WORD_FILE)

        st.subheader("📊 Sentiment Distribution by Actor")
        sent_summary = df_mentions.groupby(["Actor", "Sentiment_Label"]).size().reset_index(name="Count")
        fig_sent = px.bar(sent_summary, x="Actor", y="Count", color="Sentiment_Label",
                          barmode="group", template="plotly_white",
                          color_discrete_map={"Positive":"#0077C8", "Neutral":"#7f8c8d", "Negative":"#C0392B"})
        st.plotly_chart(fig_sent, use_container_width=True)

        st.subheader("🗝️ Top Keywords in Evaluation Mentions")
        fig_words = px.bar(df_words.head(20), x="word", y="count", color="count",
                           template="plotly_white", color_continuous_scale="Blues")
        st.plotly_chart(fig_words, use_container_width=True)

        st.subheader("🔍 Concordance Sampling")
        actor_choice = st.selectbox("Choose actor:", ["UNCT", "RC", "DCO"])
        if st.button(f"Show sample for {actor_choice}"):
            df_actor = df_mentions[df_mentions["Actor"] == actor_choice]
            if len(df_actor) > 0:
                st.write(df_actor.sample(n=min(10, len(df_actor)))[["Country","Sentiment_Label","Sentence"]])
            else:
                st.info("No mentions found.")

    except Exception as e:
        st.warning(f"Error loading text data: {e}")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#666;'>© UNDCO | Built for learning purposes</p>", unsafe_allow_html=True)

