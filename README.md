# 🛡️ Enterprise GRC LLM Benchmarking & Evaluation Suite

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Groq](https://img.shields.io/badge/Inference-Groq_Cloud-orange.svg)
![Models](https://img.shields.io/badge/Models-Qwen%20%7C%20Llama%20%7C%20GPT--OSS-success.svg)
![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen.svg)

An automated LLM evaluation and benchmarking harness designed for **Governance, Risk, and Compliance (GRC)** workflows in enterprise ERP systems. 

This tool mathematically evaluates different open-weight Large Language Models (LLMs) to determine their safety, speed, and accuracy before deploying them into production environments like **IFS Cloud** or SAP for automated internal auditing.

---

## 🎯 The Problem It Solves

When deploying GenAI for enterprise audit and fraud detection, companies face three critical risks:
1. **Hallucinations:** The AI might classify a critical financial violation as "Low Risk".
2. **Unstructured Output:** The AI might return conversational text instead of strict `JSON`, crashing the ERP workflows.
3. **Latency:** Heavy models take too long to evaluate thousands of daily transactions.

**The Solution:** This benchmarking suite acts as an automated QA pipeline. It feeds complex GRC violation scenarios (GDPR, Financial Controls, SoD) to multiple LLMs concurrently and outputs a deterministic performance matrix.

---

## 🏗️ Architecture & Workflow

1. **Input Stage:** Loads deterministic GRC test cases (`data/test_cases.json`).
2. **Multi-Model Inference:** Prompts multiple models concurrently via the Groq Cloud API for ultra-low latency execution.
3. **Automated Evaluator (`src/evaluator.py`):**
   * **JSON Schema Adherence:** Validates if the LLM output can be parsed directly into an enterprise system.
   * **Risk Severity Assertion:** Checks if the LLM accurately identified the ground-truth risk level (e.g., `HIGH`).
   * **Audit Term Coverage:** Calculates the percentage of required compliance keywords used by the LLM.
   * **Latency Profiling:** Measures execution speed in milliseconds.
4. **Reporting:** Auto-generates a CSV dashboard matrix (`reports/benchmark_results.csv`).

---

## 🚀 Live Benchmark Results

*Benchmarked on Groq LPU inference using deterministic temperature (T=0.0)*

| Test Case | Compliance Domain | Model | Latency (s) | Valid JSON | Term Coverage | Severity Match |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-GRC-001** | Data Privacy (GDPR) | `GPT-OSS-20B` | 1.96s | ✅ True | 67% | ✅ Passed (HIGH) |
| **TC-GRC-001** | Data Privacy (GDPR) | `Qwen-3.8-27B` | 0.52s | ✅ True | 67% | ✅ Passed (HIGH) |
| **TC-GRC-002** | Financial Controls | `GPT-OSS-20B` | 0.56s | ✅ True | 67% | ✅ Passed (HIGH) |
| **TC-GRC-002** | Financial Controls | `Qwen-3.8-27B` | 0.32s | ✅ True | 33% | ✅ Passed (HIGH) |
| **TC-GRC-003** | Segregation of Duties | `GPT-OSS-20B` | 0.77s | ✅ True | 67% | ✅ Passed (HIGH) |
| **TC-GRC-003** | Segregation of Duties | `Qwen-3.8-27B` | 0.36s | ✅ True | 67% | ✅ Passed (HIGH) |

> **Executive Conclusion:** `Qwen-3.8-27B` demonstrates superior enterprise viability, achieving sub-second latency (~0.3s) while maintaining 100% risk assertion accuracy and perfect JSON schema adherence.

---

## 💻 How to Run Locally

### 1. Clone the repository
```bash
git clone [https://github.com/Thameera-01/GRC-LLM-Benchmarking-Suite.git](https://github.com/Thameera-01/GRC-LLM-Benchmarking-Suite.git)
cd GRC-LLM-Benchmarking-Suite
