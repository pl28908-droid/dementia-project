"""Create simple EDA plots for the generated dataset."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "raw" / "synthetic_sessions.csv"
OUT = ROOT / "reports"

def main():
    if not DATA.exists():
        raise FileNotFoundError("Run python -m src.data.generate_dataset first.")
    OUT.mkdir(exist_ok=True)
    df = pd.read_csv(DATA)
    print("\nDataset info:")
    print(df.info())
    print("\nMissing values:\n", df.isna().sum())
    print("\nTarget distribution:\n", df["performance_band"].value_counts(normalize=True))

    ax = df["performance_band"].value_counts().plot(kind="bar", rot=0)
    ax.set_title("Synthetic target distribution")
    ax.set_xlabel("Performance band")
    ax.set_ylabel("Number of sessions")
    plt.tight_layout()
    plt.savefig(OUT / "target_distribution.png", dpi=150)
    plt.close()

    ax = df.boxplot(column="accuracy", by="difficulty")
    ax.set_title("Accuracy by game difficulty")
    plt.suptitle("")
    plt.tight_layout()
    plt.savefig(OUT / "accuracy_by_difficulty.png", dpi=150)
    plt.close()
    print(f"EDA plots saved in {OUT}")

if __name__ == "__main__":
    main()
