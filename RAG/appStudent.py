from flask import Flask, request, jsonify
from students_data import students

app = Flask(__name__)

@app.route('/get_roll_number', methods=['POST'])
def get_roll_number():
    # Parse the JSON input
    data = request.json
    if not data or 'student_name' not in data:
        return jsonify({"error": "Student name is required"}), 400
    
    student_name = data['student_name']
    
    # Fetch the roll number
    roll_number = students.get(student_name)
    if roll_number:
        return jsonify({"student_name": student_name, "roll_number": roll_number})
    else:
        return jsonify({"error": "Student not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
