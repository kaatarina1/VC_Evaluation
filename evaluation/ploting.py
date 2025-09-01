# pip install matplotlib pandas seaborn
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load results
df = pd.read_csv("voice_conversion_eval.csv")

# Use seaborn style
sns.set(style="whitegrid")

# --- Plot relative WER per model and language ---
plt.figure(figsize=(10,6))
sns.boxplot(data=df, x="model", y="rel_wer", hue="language")
plt.title("Relative WER (conversion vs input)")
plt.ylabel("Relative WER (out / in)")
plt.xlabel("Model")
plt.axhline(1.0, color="red", linestyle="--", label="Baseline = 1.0")
plt.legend(title="Language")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("rel_wer_boxplot.png", dpi=300)
plt.show()

# --- Plot relative CER per model and language ---
plt.figure(figsize=(10,6))
sns.boxplot(data=df, x="model", y="rel_cer", hue="language")
plt.title("Relative CER (conversion vs input)")
plt.ylabel("Relative CER (out / in)")
plt.xlabel("Model")
plt.axhline(1.0, color="red", linestyle="--", label="Baseline = 1.0")
plt.legend(title="Language")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig("rel_cer_boxplot.png", dpi=300)
plt.show()

# --- Optional: aggregate mean table ---
agg = df.groupby(["model", "language"])[["rel_wer","rel_cer"]].mean().reset_index()
print("Mean relative WER/CER per model:")
print(agg)
