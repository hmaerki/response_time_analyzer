"""
Loop over all files 'response_simulator_*.txt'.
For each file:
  * parse
  * create a diagram using https://altair-viz.github.io/gallery/simple_histogram.html
    * name of the diagram: filename, bin_width_s=160.0ns, 143101 measurements
  * save diagram as svg
"""

from pathlib import Path
import pandas as pd
import altair as alt


def parse_histogram_file(filepath: Path) -> dict:
    """Parse a histogram data file and return bins, counts, and metadata."""
    bins = []
    counts = []
    metadata = {}

    with filepath.open("r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue

            # Parse metadata lines (contain ':')
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                metadata[key] = value
            else:
                # Parse bin/count pairs
                parts = line.split()
                if len(parts) == 3:
                    bins.append(int(parts[0]))
                    counts.append(int(parts[2]))

    return {
        "bins": bins,
        "counts": counts,
        "metadata": metadata,
    }


def create_diagram(data: dict, filename: str) -> alt.Chart:
    """Create an Altair histogram chart from bin data."""
    # Parse bin width and convert to nanoseconds
    bin_width_s_str = data['metadata']["bin_width_s"]
    bin_width_s = float(bin_width_s_str.replace("ns", "")) * 1e-9

    duration_max_s = data["bins"][0] * bin_width_s
    factor = 1e6
    time_unit = "us"
    if duration_max_s < 1e-06:
        factor = 1e9
        time_unit = "ns"
    time_x = [bin * bin_width_s * factor for bin in data["bins"]]

    df = pd.DataFrame({f"time_{time_unit}": time_x, "count": data["counts"]})

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"time_{time_unit}:Q", title=f"Response Time ({time_unit})"),
            y=alt.Y("count:Q", title="Count"),
        )
        .properties(
            width=800,
            height=400,
            title=f"{filename}: bin_width_s={data['metadata']['bin_width_s']}, "
            f"{data['metadata']['total_count']} measurements",
        )
    )

    return chart


def main():
    testdata_dir = Path(__file__).parent

    for txt_file in sorted(testdata_dir.glob("response_simulator_*.txt")):
        print(f"Processing {txt_file.name}...")

        # Parse file
        data = parse_histogram_file(txt_file)

        # Create diagram
        chart = create_diagram(data, txt_file.stem)

        # Save as SVG
        svg_file = txt_file.with_suffix(".svg")
        chart.save(str(svg_file))
        print(f"  Saved to {svg_file.name}")


if __name__ == "__main__":
    main()
