from __future__ import annotations

from pathlib import Path
from collections import Counter
import csv
import re


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ANALYSIS_DIR = BASE_DIR / "analysis"

TEXT_FILES = {
    "Germany": DATA_DIR / "germany.txt",
    "Japan": DATA_DIR / "japan.txt",
}

KEYWORD_CATEGORIES = {
    "responsibility_accountability": [
        "responsibility",
        "crime",
        "genocide",
        "atrocity",
        "regime",
        "state",
    ],
    "victim_moral_framing": [
        "victim",
        "victims",
        "humanity",
        "persecution",
    ],
    "war_suffering_recovery": [
        "war",
        "violence",
        "peace",
        "tragedy",
        "loss",
        "suffering",
        "recovery",
    ],
}


def load_text(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")
    return file_path.read_text(encoding="utf-8")


def tokenize(text: str) -> list[str]:
    cleaned = re.sub(r"[^a-zA-Z\\s]", " ", text.lower())
    return cleaned.split()


def count_keywords(words: list[str], categories: dict[str, list[str]]) -> tuple[dict[str, int], dict[str, int]]:
    word_counter = Counter(words)
    keyword_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}

    for category, keywords in categories.items():
        total = 0
        for keyword in keywords:
            count = word_counter[keyword]
            keyword_counts[keyword] = count
            total += count
        category_counts[category] = total

    return keyword_counts, category_counts


def save_keyword_csv(output_path: Path, keyword_counts: dict[str, int]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "count"])
        for term, count in keyword_counts.items():
            writer.writerow([term, count])


def save_category_summary(output_path: Path, all_category_counts: dict[str, dict[str, int]]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    category_names = list(KEYWORD_CATEGORIES.keys())

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text"] + category_names)

        for text_name, counts in all_category_counts.items():
            row = [text_name] + [counts.get(category, 0) for category in category_names]
            writer.writerow(row)


def build_comparison_text(all_category_counts: dict[str, dict[str, int]]) -> str:
    germany = all_category_counts["Germany"]
    japan = all_category_counts["Japan"]

    return f"""## Comparison

This project compares how historical atrocities are framed in German and Japanese texts using exploratory keyword frequency analysis.

In the German text, responsibility-related language appears {germany["responsibility_accountability"]} times, while victim and moral-framing language appears {germany["victim_moral_framing"]} times. Terms related to war, suffering, and recovery appear {germany["war_suffering_recovery"]} times.

In the Japanese text, responsibility-related language appears {japan["responsibility_accountability"]} times, while victim and moral-framing language appears {japan["victim_moral_framing"]} times. Terms related to war, suffering, and recovery appear {japan["war_suffering_recovery"]} times.

These results suggest that the German text places stronger emphasis on institutional responsibility and moral framing, while the Japanese text places stronger emphasis on war, suffering, peace, and recovery.

Because this is a small-scale exploratory analysis based on limited text samples, these findings should be interpreted cautiously.
"""


def save_text(output_path: Path, content: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    all_category_counts: dict[str, dict[str, int]] = {}

    for text_name, file_path in TEXT_FILES.items():
        raw_text = load_text(file_path)
        words = tokenize(raw_text)

        keyword_counts, category_counts = count_keywords(words, KEYWORD_CATEGORIES)
        all_category_counts[text_name] = category_counts

        output_csv = ANALYSIS_DIR / f"{text_name.lower()}_results.csv"
        save_keyword_csv(output_csv, keyword_counts)

    summary_csv = ANALYSIS_DIR / "category_summary.csv"
    save_category_summary(summary_csv, all_category_counts)

    comparison_md = ANALYSIS_DIR / "comparison.md"
    comparison_text = build_comparison_text(all_category_counts)
    save_text(comparison_md, comparison_text)

    print("Analysis complete.")
    print(f"Created: {ANALYSIS_DIR / 'germany_results.csv'}")
    print(f"Created: {ANALYSIS_DIR / 'japan_results.csv'}")
    print(f"Created: {summary_csv}")
    print(f"Created: {comparison_md}")


if __name__ == "__main__":
    main()
