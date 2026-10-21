import csv
import os

import pandas as pd
import plotly.express as px
from flask import Flask, abort, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "csv")
DEFAULT_FILE = "meetinglist.csv"
CSV_PATH = os.path.join(CSV_DIR, DEFAULT_FILE)

NAME_COL = "Name (original name)"
ATTENDED_COL = "Attended (min)"


def ensure_sample_csv():
    """Create a small FAKE sample CSV if one doesn't exist yet."""
    os.makedirs(CSV_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Medication", "Dose", "Frequency"])
            writer.writerow(["10/15/2026", "Atorvastatin", "10 mg", "Daily"])
            writer.writerow(["10/15/2026", "Metoprolol", "25 mg", "Daily"])


# ---------------------------------------------------------------- templates

STYLE = """
body { font-family: Arial, sans-serif; background-color: #DBDBDB;
       color: #0F0F0F; text-align: center; margin: 50px; }
h1 { color: #C90000; }
p { font-size: 1.2em; }
a { color: #C90000; }
table { border-collapse: collapse; margin: 20px auto; background: white; }
th, td { border: 1px solid #777; padding: 6px 14px; }
th { background: #C90000; color: white; }
"""

HOME_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>NYS Medical - Rural Hospital</title>
  <style>{{ style }}</style>
</head>
<body>
  <h1>Remote Instance Connected Successfully.</h1>
  <p><a href="/table">View CSV table</a></p>
  <p><a href="/charts">View attendance charts</a></p>
</body>
</html>
"""

TABLE_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CSV Table</title>
  <style>{{ style }}</style>
</head>
<body>
  <h1>CSV Data</h1>
  <p><a href="/">&larr; Back to patient page</a></p>
  <table>
    <tr>
      {% for col in header %}<th>{{ col }}</th>{% endfor %}
    </tr>
    {% for row in data %}
    <tr>
      {% for cell in row %}<td>{{ cell }}</td>{% endfor %}
    </tr>
    {% endfor %}
  </table>
</body>
</html>
"""

CHARTS_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Meeting Duration</title>
  <style>{{ style }}</style>
</head>
<body>
  <h1>{{ title }}</h1>
  <p><a href="/">&larr; Back to patient page</a> |
     <a href="/table">View CSV table</a></p>
  {% if error %}
    <p>{{ error }}</p>
  {% else %}
    {{ bar | safe }}
    {{ hist | safe }}
  {% endif %}
</body>
</html>
"""


# ------------------------------------------------------------------- charts

def load_data(path):
    # utf-8-sig also handles the hidden BOM character Excel adds to CSV files
    df = pd.read_csv(path, encoding="utf-8-sig")

    # The Zoom export has two "Duration (minutes)" columns; pandas renames the
    # second one (time each participant attended) to "Duration (minutes).1".
    if NAME_COL not in df.columns or "Duration (minutes).1" not in df.columns:
        return None

    df = df.dropna(subset=[NAME_COL])  # drops totals row + blank rows
    df = df.rename(columns={"Duration (minutes).1": ATTENDED_COL})
    df = df.sort_values(ATTENDED_COL, ascending=False)
    return df


def render_charts(filename):
    path = os.path.join(CSV_DIR, os.path.basename(filename))
    if not os.path.isfile(path):
        abort(404)

    df = load_data(path)
    if df is None:
        return render_template_string(
            CHARTS_HTML,
            style=STYLE,
            title="Attendance",
            error=f"{os.path.basename(filename)} doesn't look like a meeting "
                  f"export (missing '{NAME_COL}' or the participant duration column).",
        )

    bar = px.bar(
        df,
        x=NAME_COL,
        y=ATTENDED_COL,
        title="Time attended per participant (meeting length: 120 min)",
        labels={NAME_COL: "Participant"},
    )
    bar.add_hline(y=120, line_dash="dash", annotation_text="Full meeting")

    hist = px.histogram(
        df,
        x=ATTENDED_COL,
        nbins=10,
        title="Distribution of attendance time",
    )

    topic = df["Topic"].dropna().iloc[0] if "Topic" in df.columns and df["Topic"].notna().any() else "Meeting"

    return render_template_string(
        CHARTS_HTML,
        style=STYLE,
        title=f"{topic}: Attendance",
        error=None,
        # Embed Plotly once in the first chart so it works offline too
        bar=bar.to_html(full_html=False, include_plotlyjs=True),
        hist=hist.to_html(full_html=False, include_plotlyjs=False),
    )


# ------------------------------------------------------------------- routes

@app.route("/")
def home():
    return render_template_string(HOME_HTML, style=STYLE)


@app.route("/table")
def table():
    ensure_sample_csv()
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        header = next(reader, [])  # [] instead of crashing on an empty file
        # skip rows that are completely empty (the export ends with a bunch)
        data = [row for row in reader if any(cell.strip() for cell in row)]
    return render_template_string(TABLE_HTML, style=STYLE, header=header, data=data)


@app.route("/charts")
def charts():
    ensure_sample_csv()
    return render_charts(DEFAULT_FILE)


@app.route("/charts/<filename>")
def charts_for_file(filename):
    return render_charts(filename)


if __name__ == "__main__":
    ensure_sample_csv()
    # Public interface, port 5003. Keep debug OFF when exposed to the internet.
    app.run(host="0.0.0.0", port=5003, debug=False)