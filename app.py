import streamlit as st
import pandas as pd
import plotly.express as px
import os
import subprocess

st.set_page_config(page_title="GRC Benchmark Dashboard", layout="wide", page_icon="")

st.title("Enterprise GRC LLM Benchmarking Dashboard")
st.markdown("Visualizing inference latency, strict JSON adherence, and audit terminology accuracy for Open-Weight LLMs via Groq LPU.")