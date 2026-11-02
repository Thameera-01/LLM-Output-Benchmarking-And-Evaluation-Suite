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
        "name": "Llama-3.1-8B (Groq)",
        "client": groq_client,
        "model_id": "llama-3.1-8b-instant"
    },
    {
        "name": "Gemma-2-9B (Groq)",
        "client": groq_client,
        "model_id": "gemma2-9b-it"
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
        return str(e), latency, False

def main():
    if not os.path.exists("data/test_cases.json"):
        print("Error: data/test_cases.json not found.")
        return

    with open("data/test_cases.json", "r") as f:
        test_cases = json.load(f)

    results = []
    print(f">>> Loaded {len(test_cases)} GRC test cases. Running benchmark...\n")

    for tc in test_cases:
        for model in MODELS:
            print(f"Testing {tc['id']} on {model['name']}...")
            raw_output, latency, success = run_inference(model["client"], model["model_id"], tc["prompt"])

            if success:
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
    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/benchmark_results.csv", index=False)

    print("\n" + "=" * 65)
    print("BENCHMARK EXECUTION SUMMARY")
    print("=" * 65)
    print(df.to_markdown(index=False))
    print("\nSaved detailed results to reports/benchmark_results.csv")

if __name__ == "__main__":
    main()