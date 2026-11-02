import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from evaluator import evaluate_llm_response

load_dotenv()

groq_client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY", "")
)

MODELS = [
    {
        "name": "GPT-OSS-20B (Groq)",
        "client": groq_client,
        "model_id": "openai/gpt-oss-20b"
    },
    {
        "name": "Qwen-3.8-27B (Groq)",
        "client": groq_client,
        "model_id": "qwen/qwen3.8-27b"
    }
]

def run_inference(client: OpenAI, model_id: str, prompt: str):
    """
    Run inference on the given model with the provided prompt."""
    start = time.time()
    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional Governance, Risk, and Compliance (GRC) audit evaluator. Output only valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.0
        )
        latency = round(time.time() - start, 3)
        return response.choices[0].message.content, latency, True
    except Exception as e:
        latency = round(time.time() - start, 3)
        print(f"\n[API ERROR on {model_id}]: {e}\n")
        return str(e), latency, False

def main():

    cwd = os.getcwd()
    json_path = os.path.join(cwd, "data", "test_cases.json")

    if not os.path.exists(json_path):
        print(f"[ERROR]: {json_path} not found. Please make sure you are in the project root folder.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    results = []
    print(f"\n>>> Loaded {len(test_cases)} GRC test cases. Running benchmark...\n")

    for tc in test_cases:
        for model in MODELS:
            print(f"Testing {tc['id']} on {model['name']}...")
            raw_output, latency, success = run_inference(model["client"], model["model_id"], tc["prompt"])

            if success:
                print(f"[RAW OUTPUT SAMPLE]: {raw_output[:90]}...\n")
                eval_metrics = evaluate_llm_response(raw_output, tc)
            else:
                eval_metrics = {
                    "valid_json": False,
                    "term_coverage": 0.0,
                    "severity_assertion_pass": False
                }

            results.append({
                "Test ID": tc["id"],
                "Category": tc["category"],
                "Model": model["name"],
                "Latency (s)": latency,
                "Valid JSON": eval_metrics["valid_json"],
                "Term Coverage": eval_metrics["term_coverage"],
                "Severity Assertion": eval_metrics["severity_assertion_pass"]
            })

    df = pd.DataFrame(results)

    reports_dir = os.path.join(cwd, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    csv_file_path = os.path.join(reports_dir, "benchmark_results.csv")
    df.to_csv(csv_file_path, index=False, encoding="utf-8")

    print("\n" + "=" * 65)
    print("BENCHMARK EXECUTION SUMMARY")
    print("=" * 65)
    print(df.to_markdown(index=False))

    if os.path.exists(csv_file_path):
        print(f"\n[SUCCESS] CSV File created successfully!")
        print(f"Path: {csv_file_path}")
        print(f"File Size: {os.path.getsize(csv_file_path)} bytes")
    else:
        print("\n[ERROR] File could not be written to disk.")

if __name__ == "__main__":
    main()