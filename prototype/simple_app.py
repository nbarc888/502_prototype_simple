from flask import Flask

app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return """
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>NYS Medical - Rural Hospital</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background-color: #DBDBDB;
            color: #0F0F0F;
            text-align: center;
            margin: 50px;
          }
          h1 {
            color: #C90000;
          }
          p {
            font-size: 1.2em;
          }
          .footer {
            margin-top: 40px;
            font-size: 0.9em;
            color: #777;
          }
        </style>
      </head>
      <body>
        <h1> Remote Instance Connected Successfully.  </h1>
        <p>
          John Doe 68M - MRN 006767<br>
          Admitted: 10/15/2026<br>
            Chief Complaint:Right Femur fx s/p IM nailing <br>
            Patient had mechanical fall at home, slipped on porch, fell on right side. No HS, LOC or AC.  <br>
        </p>

          <p> History Provided by Patient </p>
          <p> HTN, HLD </p>
          <p> No known allergies </p>
          <p> Medications: Atorvastatin 10mg daily, Metoprolol 25mg daily </p>
      
      </body>
    </html>
    """
        


if __name__ == "__main__":
    # Run on all interfaces (so it's accessible via public IP), port 5003
    app.run(host="0.0.0.0", port=5003)