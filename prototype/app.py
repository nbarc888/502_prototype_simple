import csv
import os
from flask import Flask, render_template_string

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(BASE_DIR, "csv")
CSV_PATH = os.path.join(CSV_DIR, "meetinglist.csv")
# CSV_PATH = os.path.join(CSV_DIR, "sample_prototype.csv")


def ensure_sample_csv():
    """Create a small FAKE sample CSV if one doesn't exist yet."""
    os.makedirs(CSV_DIR, exist_ok=True)
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Medication", "Dose", "Frequency"])
            writer.writerow(["10/15/2026", "Atorvastatin", "10 mg", "Daily"])
            writer.writerow(["10/15/2026", "Metoprolol", "25 mg", "Daily"])


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


@app.route("/")
def home():
    return render_template_string(HOME_HTML, style=STYLE)


@app.route("/table")
def table():
    ensure_sample_csv()
    # utf-8-sig also handles the hidden BOM character Excel adds to CSV files
    with open(CSV_PATH, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        header = next(reader, [])  # [] instead of crashing on an empty file
        data = list(reader)
    return render_template_string(TABLE_HTML, style=STYLE, header=header, data=data)


if __name__ == "__main__":
    ensure_sample_csv()
    # Public interface, port 5003. Keep debug OFF when exposed to the internet.
    app.run(host="0.0.0.0", port=5003, debug=False)


