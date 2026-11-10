import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import subprocess

st.set_page_config(page_title="GRC Benchmark Dashboard", layout="wide")

st.title(" Enterprise GRC LLM Benchmarking Dashboard")
st.markdown("Visualizing inference latency, strict JSON adherence, and audit terminology accuracy for Open-Weight LLMs via Groq LPU.")

project_root = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(project_root, "reports", "benchmark_results.csv")
benchmark_script = os.path.join(project_root, "src", "benchmark.py")
data_dir = os.path.join(project_root, "data")

st.sidebar.header(" Controls")

uploaded_file = st.sidebar.file_uploader(" Upload Test Cases (CSV)", type=["csv"])
save_path = None

if uploaded_file is not None:
    os.makedirs(data_dir, exist_ok=True)
    save_path = os.path.join(data_dir, "test_cases.csv")
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.success("File uploaded successfully!")

if st.sidebar.button(" Run New Benchmark"):
    with st.spinner("Executing multi-model inference via Groq API..."):
        if save_path:
            subprocess.run([sys.executable, benchmark_script, save_path], cwd=project_root)
        else:
            subprocess.run([sys.executable, benchmark_script], cwd=project_root)
    st.sidebar.success("Benchmark Completed & Data Updated!")

# data loading part
@st.cache_data(ttl=5)
def load_data():
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return None

df = load_data()

if df is not None and not df.empty:
    st.sidebar.markdown("---")
    st.sidebar.subheader(" Filters")
    selected_models = st.sidebar.multiselect("Select Models", df["Model"].unique(), default=df["Model"].unique())
    df_filtered = df[df["Model"].isin(selected_models)]

    if df_filtered.empty:
        st.warning("Please select at least one model from the sidebar filter.")
    else:
        st.subheader(" Executive Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fastest_model = df_filtered.groupby("Model")["Latency (s)"].mean().idxmin()
            fastest_time = df_filtered.groupby("Model")["Latency (s)"].mean().min()
            st.metric(" Fastest Model (Avg)", fastest_model, f"{fastest_time:.2f} s")
        with col2:
            valid_json_rate = df_filtered["Valid JSON"].mean() * 100
            st.metric(" Valid JSON Rate", f"{valid_json_rate:.0f}%")
        with col3:
            severity_rate = df_filtered["Severity Assertion"].mean() * 100
            st.metric(" Severity Accuracy", f"{severity_rate:.0f}%")
        with col4:
            avg_coverage = df_filtered["Term Coverage"].mean() * 100
            st.metric("Avg Term Coverage", f"{avg_coverage:.0f}%")

        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.subheader("⏱ Inference Latency by Test Case")
            fig_latency = px.bar(
                df_filtered, x="Test ID", y="Latency (s)", color="Model", barmode="group",
                text_auto='.2f', title="Latency Comparison (Lower is better)"
            )
            st.plotly_chart(fig_latency, use_container_width=True)

        with col_chart2:
            st.subheader(" Audit Term Coverage")
            fig_terms = px.bar(
                df_filtered, x="Test ID", y="Term Coverage", color="Model", barmode="group",
                text_auto='.2f', title="Term Coverage % (Higher is better)"
            )
            st.plotly_chart(fig_terms, use_container_width=True)

        st.subheader(" Detailed Benchmark Matrix")
        st.dataframe(
            df_filtered.style.highlight_max(subset=['Term Coverage'], color='lightgreen')
                       .highlight_min(subset=['Latency (s)'], color='lightgreen'),
            use_container_width=True
        )
else:
    st.warning(f"No benchmark data found at `{csv_path}`. Please upload a CSV and click 'Run New Benchmark' in the sidebar.")