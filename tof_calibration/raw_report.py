import csv
import re
from collections import defaultdict
from tof_raw import raw_data


summary = defaultdict(dict)
durations = set()

for key, values in raw_data.items():
    match = re.match(r"raw_(\d+)_(20sample|\d+)", key)
    if not match:
        continue
    dist, dur = match.groups()
    dist = int(dist)
    if dur != "20sample":
        dur = int(dur)
    durations.add(dur)
    avg = sum(values) / len(values)
    summary[dist][dur] = {
        "avg": avg,
        "max": max(values),
        "min": min(values)
    }

# Sort durations: numbers first, then "20samples"
sorted_durations = sorted([d for d in durations if isinstance(d, int)]) + \
                   [d for d in durations if isinstance(d, str)]

# CSV header
header = ["Distance (mm)"]
for dur in sorted_durations:
    header.extend([f"{dur}_avg", f"{dur}_max", f"{dur}_min"])

# Write CSV
with open("summary_output.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(header)

    for dist in sorted(summary.keys()):
        row = [dist]
        for dur in sorted_durations:
            if dur in summary[dist]:
                stats = summary[dist][dur]
                row.extend([f"{stats['avg']:.2f}", f"{stats['max']:.2f}", f"{stats['min']:.2f}"])
            else:
                row.extend(["", "", ""])
        writer.writerow(row)
