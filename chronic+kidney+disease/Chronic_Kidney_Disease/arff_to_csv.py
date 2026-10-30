\"\"\"Convert the official UCI ARFF file to CSV.

UCI (id 336) ships Chronic Kidney Disease only as ARFF, so this one-off
script turns it into chronic_kidney_disease.csv with a real header row.

Handles two glitches in the raw file:
  * one row has a stray trailing comma
  * one row has an extra empty field (missing values are normally "?")
\"\"\"
import re
from pathlib import Path

import pandas as pd

SRC = Path(__file__).with_name("chronic_kidney_disease.arff")
OUT = Path(__file__).with_name("chronic_kidney_disease.csv")

attrs, rows, in_data = [], [], False
for line in SRC.read_text(encoding="utf-8", errors="replace").splitlines():
    s = line.strip()
    if not s or s.startswith("%"):
        continue
    if s.lower().startswith("@attribute"):
        m = re.match(r"@attribute\s+'?\"?([^'\"]+?)'?\"?\s+(\{.*\}|numeric|real|string|integer)", s, re.I)
        attrs.append((m.group(1), m.group(2)))
    elif s.lower().startswith("@data"):
        in_data = True
    elif in_data:
        vals = [v.strip() for v in s.split(",")]
        if len(vals) == len(attrs) + 1 and vals[-1] == "":
            vals = vals[:-1]
        if len(vals) == len(attrs) + 1 and "" in vals:
            vals.pop(vals.index(""))
        rows.append(vals)

cols = [a for a, _ in attrs]
df = pd.DataFrame(rows, columns=cols)
for (_, typ), col in zip(attrs, cols):
    df[col] = df[col].replace({"?": None})
    if typ.lower() in ("numeric", "real", "integer"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

df.to_csv(OUT, index=False)
print(f"{df.shape[0]} rows x {df.shape[1]} columns -> {OUT.name}")
