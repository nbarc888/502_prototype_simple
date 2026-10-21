import os
from flask import Flask, abort
import pandas as pd
import plotly.express as px

import os
from flask import Flask, abort
import pandas as pd
import plotly.express as px

app = Flask(__name__)

CSV_DIR = os.path.join(app.root_path, "csv")
DEFAULT_FILE = "meetinglist.csv"


def load_data(path):
    df = pd.read_csv(path)
    df = df.dropna(subset=["Name (original name)"])  # drops totals + blank rows
    df = df.rename(columns={"Duration (minutes).1": "Attended (min)"})
    df = df.sort_values("Attended (min)", ascending=False)
    return df


def render_charts(filename):
    path = os.path.join(CSV_DIR, os.path.basename(filename))
    if not os.path.isfile(path):
        abort(404)

    df = load_data(path)

    bar = px.bar(
        df,
        x="Name (original name)",
        y="Attended (min)",
        title="Time attended per participant (meeting length: 120 min)",
        labels={"Name (original name)": "Participant"},
    )
    bar.add_hline(y=120, line_dash="dash", annotation_text="Full meeting")

    hist = px.histogram(
        df,
        x="Attended (min)",
        nbins=10,
        title="Distribution of attendance time",
    )

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Meeting Duration</title>
</head>
<body>
  <h1>Fall Group A: Attendance</h1>
  {bar.to_html(full_html=False, include_plotlyjs=True)}
  {hist.to_html(full_html=False, include_plotlyjs=False)}
</body>
</html>"""


@app.route("/")
def index():
    return render_charts(DEFAULT_FILE)


@app.route("/<filename>")
def show(filename):
    return render_charts(filename)


if __name__ == "__main__":
    app.run(debug=True)