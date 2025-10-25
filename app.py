import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# 🌐 General Settings
# =========================================
st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")

# --- Global Header ---
st.title("🌐 UNSDCF Evaluation Dashboard (2021–2023)")
st.markdown("""
This dashboard consolidates **evaluation expenditure**, **synthesized findings**,  
and **textual analysis** from UNSDCF evaluations between 2021–2023.  
---
""")

# --- Sidebar Navigation ---
page = st.sidebar.radio(
    "📊 Navigation Menu",
    ["📍 Page 1: Evaluation Expenditure", 
     "📍 Page 2: Evaluation Findings", 
     "📍 Page 3: Text Analysis"]
)

# =========================================
# PAGE 1 — Evaluation Expenditure
# =========================================
if page == "📍 Page 1: Evaluation Expenditure":
    st.header("💰 Evaluation Expenditure Overview (2021–2023)")
    st.markdown("Visualizing how countries allocated evaluation budgets relative to total programme expenditure.")

    file_path = "2021-2023evaluationexpendituresanalysis.xlsx"

    try:
        df_spend = pd.read_excel(file_path)
        df_spend.columns = df_spend.columns.str.strip().str.replace(r"\s+", " ", regex=True)

        df_spend.rename(columns={
            "Evaluation expenditure($)": "Evaluation Spending ($)",
            "Program Expenditure": "Program Expenditure",
            "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)"
        }, inplace=True)

        for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
            if c in df_spend.columns:
                df_spend[c] = pd.to_numeric(df_spend[c], errors="coerce")

        df_spend.dropna(subset=["Eval Ratio (%)"], inplace=True)

        # --- 🌍 Global Evaluation Map ---
        st.subheader("🌍 Global Evaluation Map")
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

        # --- 📈 Scatter Plot ---
        st.subheader("📈 Evaluation Spending vs Programme Expenditure")
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
            xaxis_title="Programme Expenditure (USD)",
            yaxis_title="Evaluation Ratio (%)",
            yaxis_ticksuffix="%",
            plot_bgcolor="white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")

# =========================================
# PAGE 2 — Evaluation Findings
# =========================================
elif page == "📍 Page 2: Evaluation Findings":
    st.header("📊 Synthesizing the Evaluation Findings")
    st.markdown("Performance across OECD-DAC criteria and balance between strengths and weaknesses.")

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

    st.subheader("🕸️ Radar Chart on OECD-DAC Criteria")
    country = st.sidebar.selectbox("Select Country", countries_eval)
    fig_radar = px.line_polar(
        df_scores[df_scores["Country"]==country],
        r="Score", theta="Criterion", line_close=True,
        color_discrete_sequence=["#1f77b4"]
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # --- 🔴🔵 Strengths & Weaknesses Chart ---
    st.subheader("🔴🔵 Strengths vs Weaknesses")
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
        title="Strengths (Blue) vs Weaknesses (Red)",
        yaxis=dict(title=None),
        xaxis=dict(title="Frequency of Mentions", showgrid=False),
        plot_bgcolor="white",
        height=600
    )
    st.plotly_chart(fig_balance, use_container_width=True)

# =========================================
# PAGE 3 — Text Analysis
# =========================================
elif page == "📍 Page 3: Text Analysis":
    st.header("🧠 Text Analysis of Evaluations")
    st.markdown("""
    This section examines how UNCT, RC, and DCO are mentioned across evaluation reports,  
    highlighting frequency and sentiment patterns.
    """)

    try:
        df_mentions = pd.read_csv("relevant_sentences_UNSDCF.csv")
        df_words = pd.read_csv("word_frequency_UNSDCF.csv")

        st.subheader("📑 Sample Extracted Mentions")
        st.dataframe(df_mentions.head(10))

        st.subheader("📊 Sentiment Distribution by Entity")
        sent_summary = df_mentions.groupby(["Entity", "Sentiment_Label"]).size().reset_index(name="Count")
        fig_sent = px.bar(
            sent_summary,
            x="Entity",
            y="Count",
            color="Sentiment_Label",
            barmode="group",
            template="plotly_white",
            title="Sentiment Distribution for RC / UNCT / DCO"
        )
        st.plotly_chart(fig_sent, use_container_width=True)

        st.subheader("🔤 Keyword Frequency")
        top_words = df_words.head(20)
        fig_words = px.bar(
            top_words,
            x="word", y="count", color="count",
            title="Top 20 Keywords in Mentions",
            template="plotly_white"
        )
        st.plotly_chart(fig_words, use_container_width=True)

    except Exception as e:
        st.warning(f"⚠️ Text analysis results not found or failed to load: {e}")

# =========================================
# Footer
# =========================================
st.markdown("---")
st.markdown("© United Nations DCO – Data visualization for learning purposes")
