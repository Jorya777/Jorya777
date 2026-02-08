# UNSDCF Evaluation Dashboard (2021–2024)
# United Nations Development Coordination Office (DCO)

import streamlit as st
import pandas as pd
import plotly.express as px
import re
from pathlib import Path

st.set_page_config(page_title="UNSDCF Evaluation Dashboard", layout="wide")

# -----------------------------
# Paths (robust on Streamlit Cloud)
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent

# If you keep data in repo root, keep as is.
# If you prefer /data folder, change to: BASE_DIR / "data" / "<file>"
EXP_FILE = BASE_DIR / "2021-2023evaluationexpendituresanalysis.xlsx"
TEXT_FILE = BASE_DIR / "relevant_sentences_UNSDCF.csv"
WORD_FILE = BASE_DIR / "word_frequency_UNSDCF.csv"

# -----------------------------
# Header (avoid breaking app if remote image fails)
# -----------------------------
st.markdown(
    """
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
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helpers
# -----------------------------
def _clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [re.sub(r"\s+", " ", str(c)).strip() for c in df.columns]
    return df


@st.cache_data(show_spinner=False)
def load_excel(path: Path) -> pd.DataFrame:
    # Explicit engine to avoid pandas guessing issues
    return pd.read_excel(path, engine="openpyxl")


@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def file_uploader_fallback(label, type_):
    return st.file_uploader(label, type=type_)

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "",
    [
        "Part I: Evaluation Implementation",
        "Part II: Synthesizing Evaluation Findings",
        "Part III: Text Analysis of Evaluations",
    ],
)

# -----------------------------
# Part I
# -----------------------------
if page == "Part I: Evaluation Implementation":
    st.header("Part I: Visualizing the Implementation of Evaluations")

    # Load data (file check + upload fallback)
    df = None
    if EXP_FILE.exists():
        try:
            df = load_excel(EXP_FILE)
        except ImportError:
            st.error(
                "Excel dependency missing. Please add `openpyxl` to requirements.txt "
                "or upload the Excel file below."
            )
        except Exception as e:
            st.error(f"Error reading Excel from repo: {e}")

    if df is None:
        up = file_uploader_fallback("Upload the Excel file (.xlsx)", ["xlsx"])
        if up is not None:
            try:
                df = pd.read_excel(up, engine="openpyxl")
            except Exception as e:
                st.error(f"Error reading uploaded Excel: {e}")

    if df is None:
        st.info("Waiting for data… (Excel file not found or unreadable).")
        st.stop()

    # Clean + normalize
    df = _clean_columns(df)

    # Flexible renaming for known variants
    rename_map = {
        "Evaluation expenditure($)": "Evaluation Spending ($)",
        "Evaluation Expenditure ($)": "Evaluation Spending ($)",
        "Evaluation Spending($)": "Evaluation Spending ($)",
        "The proportion of Evaluation Expenditure to Program Expenditure": "Eval Ratio (%)",
        "Program Expenditure": "Program Expenditure",
        "Programme Expenditure": "Program Expenditure",
    }

    # Try to detect a program expenditure column if named differently
    prog_col = [c for c in df.columns if re.search(r"program(me)?\s*expenditure", c, re.I)]
    if prog_col:
        rename_map[prog_col[0]] = "Program Expenditure"

    df = df.rename(columns=rename_map)

    # Validate required columns
    required = {"Country", "Evaluation year", "Eval Ratio (%)"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing required columns in Excel: {missing}")
        st.stop()

    # Numeric coercion (only if columns exist)
    for c in ["Evaluation Spending ($)", "Program Expenditure", "Eval Ratio (%)"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df = df.dropna(subset=["Eval Ratio (%)"])

    # Convert ratio to percent if appears 0-1 scale
    if df["Eval Ratio (%)"].max(skipna=True) <= 1:
        df["Eval Ratio (%)"] = df["Eval Ratio (%)"] * 100

    st.subheader("🌍 Global Evaluation Map (2021–2023)")
    try:
        fig_map = px.scatter_geo(
            df,
            locations="Country",
            locationmode="country names",
            hover_name="Country",
            hover_data={"Evaluation year": True, "Eval Ratio (%)": True},
            text="Evaluation year",
            projection="natural earth",
        )
        st.plotly_chart(fig_map, use_container_width=True)
    except Exception as e:
        st.warning(f"Map could not be rendered (often due to country-name matching): {e}")

    st.subheader("💰 Evaluation Expenditure vs Programme Expenditure")
    # Validate columns for scatter
    if "Program Expenditure" not in df.columns:
        st.warning("Cannot draw scatter plot: `Program Expenditure` column not found.")
    else:
        try:
            size_col = "Evaluation Spending ($)" if "Evaluation Spending ($)" in df.columns else None
            color_col = "Region" if "Region" in df.columns else "Country"
            fig_scatter = px.scatter(
                df,
                x="Program Expenditure",
                y="Eval Ratio (%)",
                size=size_col,
                color=color_col,
                hover_name="Country",
                template="plotly_white",
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        except Exception as e:
            st.error(f"Error rendering scatter plot: {e}")

# -----------------------------
# Part II
# -----------------------------
elif page == "Part II: Synthesizing Evaluation Findings":
    st.header("Part II: Synthesizing the Evaluation Findings")

    CRITERIA = [
        "relevance",
        "coherence",
        "effectiveness",
        "efficiency",
        "orientation towards impact",
        "sustainability",
    ]

    countries = ["Azerbaijan", "Uganda", "Serbia", "Indonesia", "Panama", "Bosnia and Herzegovina"]
    scores = {
        "Azerbaijan": [4, 3, 4, 3, 3, 3],
        "Uganda": [4, 2, 4, 3, 3, 3],
        "Serbia": [4, 2, 4, 3, 3, 3],
        "Indonesia": [5, 3, 4, 3, 4, 3],
        "Panama": [4, 3, 3, 3, 3, 2],
        "Bosnia and Herzegovina": [4, 2, 4, 3, 3, 3],
    }

    df_scores = pd.DataFrame(
        [{"Country": c, "Criterion": crit, "Score": scores[c][i]} for c in countries for i, crit in enumerate(CRITERIA)]
    )

    country_sel = st.sidebar.selectbox("Select Country", countries)
    fig_radar = px.line_polar(
        df_scores[df_scores["Country"] == country_sel],
        r="Score",
        theta="Criterion",
        line_close=True,
    )
    fig_radar.update_traces(fill="toself")
    st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("Strengths and Weaknesses in UNCT Performance")

    strengths = [
        ("Aligned with national priorities and SDG frameworks", 5),
        ("Trusted as neutral conveners", 4),
        ("Systematic gender and LNOB integration", 4),
        ("Evidence-based policymaking", 3),
        ("High government ownership", 5),
    ]
    weaknesses = [
        ("Fragmented programming", 5),
        ("Weak Theory of Change", 4),
        ("Limited joint resource mobilization", 4),
        ("Output-focused monitoring", 3),
        ("Low visibility of results", 5),
    ]

    df_s = pd.DataFrame(strengths, columns=["Aspect", "Value"])
    df_s["Type"] = "Strength"
    df_w = pd.DataFrame(weaknesses, columns=["Aspect", "Value"])
    df_w["Value"] = -df_w["Value"]
    df_w["Type"] = "Weakness"

    df_comb = pd.concat([df_s, df_w], ignore_index=True)

    fig_bar = px.bar(
        df_comb,
        x="Value",
        y="Aspect",
        color="Type",
        orientation="h",
        template="plotly_white",
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -----------------------------
# Part III
# -----------------------------
elif page == "Part III: Text Analysis of Evaluations":
    st.header("Part III: Text Analysis of Evaluations")

    df_mentions = None
    df_words = None

    # Mentions CSV
    if TEXT_FILE.exists():
        try:
            df_mentions = load_csv(TEXT_FILE)
        except Exception as e:
            st.error(f"Error reading mentions CSV from repo: {e}")

    if df_mentions is None:
        up1 = file_uploader_fallback("Upload relevant_sentences_UNSDCF.csv", ["csv"])
        if up1 is not None:
            try:
                df_mentions = pd.read_csv(up1)
            except Exception as e:
                st.error(f"Error reading uploaded mentions CSV: {e}")

    # Words CSV
    if WORD_FILE.exists():
        try:
            df_words = load_csv(WORD_FILE)
        except Exception as e:
            st.error(f"Error reading word frequency CSV from repo: {e}")

    if df_words is None:
        up2 = file_uploader_fallback("Upload word_frequency_UNSDCF.csv", ["csv"])
        if up2 is not None:
            try:
                df_words = pd.read_csv(up2)
            except Exception as e:
                st.error(f"Error reading uploaded word frequency CSV: {e}")

    if df_mentions is None or df_words is None:
        st.info("Waiting for data… (one or more CSV files not found or unreadable).")
        st.stop()

    # Validate expected columns
    expected_mentions = {"Actor", "Sentiment_Label", "Country", "Sentence"}
    missing_m = [c for c in expected_mentions if c not in df_mentions.columns]
    if missing_m:
        st.error(f"Mentions CSV missing columns: {missing_m}")
        st.stop()

    expected_words = {"word", "count"}
    missing_w = [c for c in expected_words if c not in df_words.columns]
    if missing_w:
        st.error(f"Word frequency CSV missing columns: {missing_w}")
        st.stop()

    st.subheader("📊 Sentiment Distribution by Actor")
    try:
        sent_summary = df_mentions.groupby(["Actor", "Sentiment_Label"]).size().reset_index(name="Count")
        fig_sent = px.bar(
            sent_summary,
            x="Actor",
            y="Count",
            color="Sentiment_Label",
            barmode="group",
            template="plotly_white",
        )
        st.plotly_chart(fig_sent, use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering sentiment chart: {e}")

    st.subheader("🗝️ Top Keywords in Evaluation Mentions")
    try:
        df_words = df_words.copy()
        df_words["count"] = pd.to_numeric(df_words["count"], errors="coerce")
        df_words = df_words.dropna(subset=["count"]).sort_values("count", ascending=False)
        fig_words = px.bar(df_words.head(20), x="word", y="count", template="plotly_white")
        st.plotly_chart(fig_words, use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering keyword chart: {e}")

    st.subheader("🔍 Concordance Sampling")
    actor_choice = st.selectbox("Choose actor:", sorted(df_mentions["Actor"].dropna().unique().tolist()))
    if st.button(f"Show sample for {actor_choice}"):
        df_actor = df_mentions[df_mentions["Actor"] == actor_choice]
        if len(df_actor) > 0:
            st.write(df_actor.sample(n=min(10, len(df_actor)), random_state=42)[["Country", "Sentiment_Label", "Sentence"]])
        else:
            st.info("No mentions found.")

st.markdown("---")
st.markdown("<p style='text-align:center; color:#666;'>© UNDCO | Built for learning purposes</p>", unsafe_allow_html=True)

