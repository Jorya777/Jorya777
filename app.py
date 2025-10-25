import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================================
# 🌍 UNSDCF Evaluation Dashboard (Multi-Page Version)
# ==========================================================
st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")

st.sidebar.title("📊 Navigation")
page = st.sidebar.radio(
    "Select a section:",
    ["📈 Evaluation Dashboard", "📘 Synthesized Findings", "🧠 Text Analysis"]
)

# ----------------------------------------------------------
# 📈 PAGE 1: Evaluation Dashboard
# ----------------------------------------------------------
if page == "📈 Evaluation Dashboard":
    st.title("📈 UNSDCF Evaluation Expenditure Dashboard")
    file_path = "2021-2023_evaluation_expenditures_analysis.xlsx"

    try:
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

        # 🌍 Map
        st.subheader("🌍 Global Evaluation Map (2021–2023)")
        fig_map = px.scatter_geo(
            df_spend,
            locations="Country",
            locationmode="country names",
            hover_name="Country",
            hover_data={"Evaluation year ": True, "Eval Ratio (%)": True},
            text="Evaluation year ",
            projection="natural earth",
            color_discrete_sequence=["#1f77b4"]
        )
        st.plotly_chart(fig_map, use_container_width=True)

        # 💰 Scatter plot (as %)
        st.subheader("💰 Evaluation vs Programme Expenditure")
        df_spend["Eval Ratio (%)"] = df_spend["Eval Ratio (%)"] * 100
        fig_scatter = px.scatter(
            df_spend,
            x="Program Expenditure",
            y="Eval Ratio (%)",
            size="Evaluation Spending ($)",
            color="Region" if "Region" in df_spend.columns else "Country",
            hover_name="Country",
            template="plotly_white"
        )
        fig_scatter.update_layout(
            yaxis_tickformat=".2f",
            yaxis_title="Evaluation Ratio (%)",
            xaxis_title="Program Expenditure (USD)",
            plot_bgcolor="white"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")

# ----------------------------------------------------------
# 📘 PAGE 2: Synthesized Findings
# ----------------------------------------------------------
elif page == "📘 Synthesized Findings":
    st.title("📘 Synthesized Evaluation Findings")

    # 🕸️ Radar Chart
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

    # 🔴🔵 Strength vs Weakness
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

    fig_balance = px.bar(df_bal, x="Frequency", y="Aspect", color="Type",
        color_discrete_map={"Strength":"steelblue","Weakness":"#d62728"},
        orientation="h", template="plotly_white")
    fig_balance.update_layout(
        title="Strengths (Blue) vs Weaknesses (Red)",
        yaxis_title=None, xaxis_title="Frequency of Mentions",
        height=600, plot_bgcolor="white"
    )
    st.plotly_chart(fig_balance, use_container_width=True)

# ----------------------------------------------------------
# 🧠 PAGE 3: Text Analysis
# ----------------------------------------------------------
elif page == "🧠 Text Analysis":
    st.title("🧠 Text Analysis of Evaluation Reports")

    try:
        df_mentions = pd.read_csv("relevant_sentences_UNSDCF.csv")
        df_words = pd.read_csv("word_frequency_UNSDCF.csv")

        st.subheader("📑 Sample Extracted Mentions")
        st.dataframe(df_mentions.head(10))

        # 📊 Sentiment by Entity
        st.subheader("📊 Sentiment Distribution by Entity (RC / UNCT / DCO)")
        if all(col in df_mentions.columns for col in ["Entity", "Sentiment_Label"]):
            sent_entity = (
                df_mentions.groupby(["Entity", "Sentiment_Label"])
                .size()
                .reset_index(name="Count")
            )
            fig_sent_entity = px.bar(
                sent_entity, x="Entity", y="Count", color="Sentiment_Label",
                barmode="group", text="Count",
                color_discrete_map={"Positive": "#2ca02c","Neutral": "#ff7f0e","Negative": "#d62728"},
                title="Sentiment Distribution across RC / UNCT / DCO",
                template="plotly_white"
            )
            fig_sent_entity.update_traces(textposition="outside")
            st.plotly_chart(fig_sent_entity, use_container_width=True)
        else:
            st.warning("⚠️ The dataset must include 'Entity' and 'Sentiment_Label' columns.")

        # 🔤 Keyword Frequency
        st.subheader("🔤 Keyword Frequency in Mentions")
        top_words = df_words.head(20)
        fig_words = px.bar(
            top_words, x="word", y="count", color="count",
            title="Top 20 Keywords in DCO/RC/UNCT Mentions",
            template="plotly_white"
        )
        st.plotly_chart(fig_words, use_container_width=True)

    except Exception as e:
        st.warning(f"⚠️ Text analysis failed to load: {e}")

st.markdown("---")
st.markdown("© United Nations DCO – Data visualization for learning purposes")

