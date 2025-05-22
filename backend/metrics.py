import pandas as pd

#change path based on your file location
input_csv = r"C:\Users\tiff6\Senior Design 24-25\SeniorProject2024\backend\evaluated_20250519_194944.csv"

df = pd.read_csv(input_csv)

total            = len(df)
avg_correctness  = df["Correctness score"].mean()
pass_rate        = (df["Correctness score"] >= 70).mean()
tool_match_rate  = df["Correct Tool?"].mean()
guardrail_rate   = df["Within guardrails?"].mean()

if df["Response Speed"].dtype == object:
    df["Response Speed"] = (
        df["Response Speed"]
          .astype(str)
          .str.rstrip("s")
          .replace("", pd.NA)
          .astype(float)
    )
avg_latency      = df["Response Speed"].mean()
p95_latency      = df["Response Speed"].quantile(0.95)

metrics = {
    "total_questions":      total,
    "avg_correctness":      avg_correctness,
    "pass_rate":            pass_rate,
    "tool_match_rate":      tool_match_rate,
    "guardrail_compliance": guardrail_rate,
    "avg_latency_s":        avg_latency,
    "95th_latency_s":       p95_latency
}
metrics_df = pd.DataFrame(list(metrics.items()), columns=["metric","value"])

#change path 
metrics_summary_csv = r"C:\Users\tiff6\Senior Design 24-25\SeniorProject2024\backend\evaluation_metrics_summary.csv"
metrics_df.to_csv(metrics_summary_csv, index=False)
print(f"Overall metrics written to:\n  {metrics_summary_csv}")

#tool breakdown
tool_stats = df.groupby("Invoked Tool").agg(
    calls            = ("Question",           "count"),
    tool_match_rate  = ("Correct Tool?",      "mean"),
    avg_correctness  = ("Correctness score",  "mean"),
    guardrail_rate   = ("Within guardrails?", "mean"),
    avg_latency_s    = ("Response Speed",     "mean")
).reset_index()

tool_breakdown_csv = r"C:\Users\tiff6\Senior Design 24-25\SeniorProject2024\backend\evaluation_tool_breakdown.csv"
tool_stats.to_csv(tool_breakdown_csv, index=False)
print(f"Tool breakdown written to:\n  {tool_breakdown_csv}")