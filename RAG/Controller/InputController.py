from flask import Flask, request, jsonify
import Service.PdfService as pdfservice

app = Flask(__name__)

@app.route('/get_query', methods=['POST'])
def get_roll_number():
    # Parse the JSON input
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "input is required"}), 400
    
    query = data['query']
    print(query)
    # Fetch the answer
    print("service started...")
    answer = pdfservice.pdfServiceExe(query)
    print(answer)
    print("service ended...")
   # roll_number = students.get(student_name)
    if answer:
        return jsonify({"answer": answer})
    else:
        return jsonify({"error": "answer not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
