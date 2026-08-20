"""
Loop over all files 'response_simulator_*.txt'.
For each file:
  * parse
  * create a diagram using https://altair-viz.github.io/gallery/simple_histogram.html
    * name of the diagram: filename, bin_width_s=160.0ns, 143101 measurements
  * save diagram as svg
"""

from __future__ import annotations

import dataclasses
import pathlib

import altair

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent


@dataclasses.dataclass(frozen=True)
class Metadata:
    bin_width_s: float
    total_count: int

    @staticmethod
    def factory(metadata: dict[str, str]) -> Metadata:
        bin_width_s_str = metadata["bin_width_s"]
        assert bin_width_s_str.endswith("ns")
        bin_width_s = float(bin_width_s_str.replace("ns", "")) * 1e-9

        total_count = int(metadata["total_count"])

        return Metadata(
            bin_width_s=bin_width_s,
            total_count=total_count,
        )


@dataclasses.dataclass(frozen=True)
class Histogram:
    bins: list[int]
    counts: list[int]
    metadata: Metadata

    @property
    def duration_max_s(self) -> float:
        return self.bins[0] * self.metadata.bin_width_s


def parse_histogram_file(filepath: pathlib.Path) -> Histogram:
    """Parse a histogram data file and return bins, counts, and metadata."""
    bins: list[int] = []
    counts: list[int] = []
    metadata: dict[str, str] = {}

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
                continue

            # Parse bin/count pairs
            parts = line.split()
            if len(parts) == 3:
                bins.append(int(parts[0]))
                counts.append(int(parts[2]))

    return Histogram(
        bins=bins,
        counts=counts,
        metadata=Metadata.factory(metadata),
    )


def create_diagram(histogram: Histogram, filename: str) -> altair.Chart:
    """Create an Altair histogram chart from bin data."""
    # Parse bin width and convert to nanoseconds
    factor = 1e6
    time_unit = "us"
    if histogram.duration_max_s < 1e-06:
        factor = 1e9
        time_unit = "ns"
    time_x = [bin * histogram.metadata.bin_width_s * factor for bin in histogram.bins]

    time_field = f"time_{time_unit}"
    data = [
        {time_field: time_value, "count": count}
        for time_value, count in zip(time_x, histogram.counts, strict=True)
        if count > 0
    ]

    chart = (
        altair.Chart(altair.Data(values=data))
        # .mark_bar()
        .mark_point(filled=True, radius=2)
        .encode(
            x=altair.X(f"{time_field}:Q", title=f"Response Time ({time_unit})"),
            y=altair.Y(
                "count:Q", title="Count", scale=altair.Scale(type="log", domainMin=0.9)
            ),
        )
        .properties(
            width=800,
            height=400,
            title=f"{filename}: bin_width_s={histogram.metadata.bin_width_s}, "
            f"{histogram.metadata.total_count} measurements",
        )
    )

    return chart


def main() -> None:
    for txt_file in sorted(DIRECTORY_OF_THIS_FILE.glob("*/response_simulator_*.txt")):
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
