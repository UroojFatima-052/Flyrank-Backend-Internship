from flask import Flask

app = Flask(__name__)

@app.route("/")
def student_details():
    return {
        "Name" : "Urooj Fatima",
        "Father Name" : "Mukhtar Ali",
        "Gender" : "Female"
    }

@app.route("/marks")
def student_marks():
    return {
        "Backend" : 95,
        "AI-Fluency" : 80
    }

if __name__ == "__main__":
    app.run(debug=True)

