"""Optional visualizations for the exercise toolkit."""

from pathlib import Path
from typing import Union

from substitution_cipher import letter_frequencies


def ensure_outputs_dir(outputs_dir: Union[str, Path] = "outputs") -> Path:
    """Create and return the directory used for generated output files."""
    path = Path(outputs_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_frequency_bar_chart(
    text: str, output_path: Union[str, Path] = "outputs/cipher_frequencies.png"
) -> Path:
    """Save a bar chart of ciphertext letter frequencies."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - depends on local install
        raise RuntimeError("matplotlib is required for charts; install requirements.txt") from exc

    path = Path(output_path)
    ensure_outputs_dir(path.parent)
    frequencies = letter_frequencies(text)
    letters = [row[0] for row in frequencies]
    counts = [row[1] for row in frequencies]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(letters, counts, color="#2f6f9f")
    ax.set_title("Ciphertext Letter Frequencies")
    ax.set_xlabel("Letter")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
    return path
