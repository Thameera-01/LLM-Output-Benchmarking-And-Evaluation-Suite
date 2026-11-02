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
    json_path = os.path.join(os.path.dirname(__file__), "..", "data", "test_cases.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    with open(json_path, "r") as f:
        test_cases = json.load(f)

    results = []
    print(f"\n>>> Loaded {len(test_cases)} GRC test cases. Running benchmark...\n")

    for tc in test_cases:
        for model in MODELS:
            print(f"Testing {tc['id']} on {model['name']}...")
            raw_output, latency, success = run_inference(model["client"], model["model_id"], tc["prompt"])

            if success:
                print(f"[RAW OUTPUT SAMPLE]: {raw_output[:120]}...\n")
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
    reports_dir = os.path.join(os.path.dirname(__file__), "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    df.to_csv(os.path.join(reports_dir, "benchmark_results.csv"), index=False)

    print("\n" + "=" * 65)
    print("BENCHMARK EXECUTION SUMMARY")
    print("=" * 65)
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    main()