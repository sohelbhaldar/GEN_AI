from flask import Flask, jsonify, render_template
from flask_cors import CORS
import threading
import speech_recognition as sr
import Service.PdfService as pdfservice
import pyttsx3

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # Enable Cross-Origin Resource Sharing

# Global variables
is_listening = False  # Initially, the system is not listening for commands
recognized_text = []
engine = pyttsx3.init()
# Set properties (optional)
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 1)  # Volume level (0.0 to 1.0)

def continuous_recognition():
    """
    Continuously listen for the wake word 'Hey Brightly' and then start recognizing speech.
    """
    global is_listening, recognized_text
    recognizer = sr.Recognizer()
    count = 0

    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening for 'Hey Brightly' to start...")

        while True:
            try:
                # Listen for the wake word
                audio_data = recognizer.listen(source, timeout=20)
                text = recognizer.recognize_google(audio_data)
                print(f"Detected: {text}")

                if "brightly" in text.lower():
                    # Wake word detected, start listening for speech commands
                    print("Wake word detected. Now listening for commands.")
                    is_listening = True
                    recognized_text.append("Listening please speak now")
                    listining = "Listening please speak now"
                    # Convert text to speech
                    engine.say(listining)
                    engine.runAndWait()

                    while is_listening:
                        try:
                            audio_data = recognizer.listen(source, timeout=7)
                            text = recognizer.recognize_google(audio_data)
                            print(f"You said: {text}")
                            answer = pdfservice.pdfServiceExe(text)
                            recognized_text.append(text)
                            recognized_text.append(answer)
                            # Convert text to speech
                            engine.say(answer)
                            print(answer)
                            # Wait for the speech to finish before closing the program
                            engine.runAndWait()
                            count = 0
                            if "stop" in text.lower():
                                print("Stop command detected. Stopping recognition...")
                                is_listening = False
                                break
                            break
                        except sr.UnknownValueError:
                            recognized_text.append("Sorry, I couldn't understand.")
                        except Exception as e:
                            recognized_text.append(f"Error: {e}")
                            is_listening = False
                            break

            except sr.UnknownValueError:
                if(count < 2):
                    text = "Say heyy Brightly!!!"
                    # Convert text to speech
                    engine.say(text)
                    engine.runAndWait()
                    count = count+1

                recognized_text.append("Say heyy Brightly!!!")
            except Exception as e:
                recognized_text.append(f"Error: {e}")

@app.route('/')
def index():
    """
    Serve the UI.
    """
    return render_template('index.html')

@app.route('/get_text', methods=['GET'])
def get_text():
    """
    Get the recognized text.
    """
    global recognized_text
    data = {"text": recognized_text.copy()}
    recognized_text.clear()  # Clear after sending to prevent duplicate fetching
    return jsonify(data)

if __name__ == '__main__':
    # Start the speech recognition in a separate thread
    recognition_thread = threading.Thread(target=continuous_recognition, daemon=True)
    recognition_thread.start()

    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)

#WORKING..!! Speech recog with axios and polling
# from flask import Flask, jsonify, render_template
# from flask_cors import CORS
# import threading
# import speech_recognition as sr
# import Service.PdfService as pdfservice
# app = Flask(__name__, template_folder="templates", static_folder="static")
# CORS(app)  # Enable Cross-Origin Resource Sharing

# # Global variables
# is_listening = True
# recognized_text = []

# def continuous_recognition():
#     """
#     Continuously listen to the microphone and update recognized text.
#     """
#     global is_listening, recognized_text
#     recognizer = sr.Recognizer()

#     with sr.Microphone() as source:
#         print("Adjusting for ambient noise... Please wait.")
#         recognizer.adjust_for_ambient_noise(source, duration=2)
#         print("Listening for speech. Say 'stop' to terminate.")

#         while is_listening:
#             try:
#                 print("Listening...")
#                 audio_data = recognizer.listen(source, timeout=5)

#                 # Recognize the speech
#                 text = recognizer.recognize_google(audio_data)
#                 print(f"Recognized: {text}")
#                 answer = pdfservice.pdfServiceExe(text)
#                 recognized_text.append(text)
#                 recognized_text.append(answer)

#                 # Stop if "stop" command is detected
#                 if text.lower() == "stop":
#                     print("Stopping speech recognition...")
#                     is_listening = False
#                     break

#             except sr.UnknownValueError:
#                 print("Could not understand, try again.")
#             except Exception as e:
#                 print(f"Error: {e}")

# @app.route('/')
# def index():
#     """
#     Serve the UI.
#     """
#     return render_template('index.html')

# @app.route('/get_text', methods=['GET'])
# def get_text():
#     """
#     Get the recognized text.
#     """
#     global recognized_text
#     data = {"text": recognized_text.copy()}
#     recognized_text.clear()  # Clear after sending to prevent duplicate fetching
#     return jsonify(data)

# if __name__ == '__main__':
#     # Start the speech recognition in a separate thread
#     recognition_thread = threading.Thread(target=continuous_recognition, daemon=True)
#     recognition_thread.start()

#     # Start the Flask app
#     app.run(debug=True, host='0.0.0.0', port=5000)


#Speech text on UI with socket IO
# from flask import Flask, render_template
# from flask_socketio import SocketIO
# import threading
# import speech_recognition as sr

# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
# socketio = SocketIO(app)

# # Global variable to control the listening thread
# is_listening = False

# def continuous_recognition():
#     """
#     Continuously listen to the microphone and send recognized text to the UI.
#     """
#     global is_listening
#     recognizer = sr.Recognizer()

#     with sr.Microphone() as source:
#         print("Adjusting for ambient noise... Please wait.")
#         recognizer.adjust_for_ambient_noise(source, duration=3)
#         print("Listening... Say 'stop' to exit.")

#         while is_listening:
#             try:
#                 print("Listening for your command...")
#                 audio_data = recognizer.listen(source, timeout=12)

#                 # Recognize the speech
#                 print("Processing...")
#                 text = recognizer.recognize_google(audio_data)
#                 print(f"You said: {text}")

#                 # Send recognized text to the UI
#                 #socketio.emit('speech_text', {'text': text}, broadcast=True)
#                 socketio.emit('speech_text', {'text': text}, namespace='/')

#                 # Exit loop if "stop" is detected
#                 if text.lower() == "stop":
#                     print("Stop command detected. Stopping recognition...")
#                     is_listening = False
#                     break

#             except sr.UnknownValueError:
#                 socketio.emit('speech_text', {'text': "Couldn't understand. Try again."}, namespace='/')
#             except sr.RequestError as e:
#                 socketio.emit('speech_text', {'text': f"API error: {e}"}, namespace='/')
#                 is_listening = False
#             except Exception as e:
#                 socketio.emit('speech_text', {'text': f"Error: {e}"}, namespace='/')
#                 is_listening = False

# @app.route('/')
# def home():
#     """
#     Render the UI.
#     """
#     return render_template('index.html')

# @app.route('/start', methods=['POST'])
# def start_recognition():
#     """
#     Start the continuous speech recognition process.
#     """
#     global is_listening

#     if is_listening:
#         return {"message": "Recognition is already running."}, 400

#     is_listening = True
#     threading.Thread(target=continuous_recognition).start()
#     return {"message": "Speech recognition started."}, 200

# @app.route('/stop', methods=['POST'])
# def stop_recognition():
#     """
#     Stop the continuous speech recognition process.
#     """
#     global is_listening

#     if not is_listening:
#         return {"message": "Recognition is not running."}, 400

#     is_listening = False
#     return {"message": "Speech recognition stopped."}, 200

# if __name__ == '__main__':
#     socketio.run(app, debug=True, host='0.0.0.0', port=5000)

#Voice Recognition with UI
# from flask import Flask, jsonify, render_template
# import threading
# import speech_recognition as sr

# app = Flask(__name__)

# # Global variable to control the listening thread
# is_listening = False

# def continuous_recognition():
#     """
#     Continuously listen to the microphone until "stop" is detected.
#     """
#     global is_listening
#     recognizer = sr.Recognizer()

#     with sr.Microphone() as source:
#         print("Adjusting for ambient noise... Please wait.")
#         recognizer.adjust_for_ambient_noise(source, duration=2)
#         print("Listening... Say 'stop' to exit.")

#         while is_listening:
#             try:
#                 print("Listening for your command...")
#                 audio_data = recognizer.listen(source, timeout=12)

#                 # Recognize the speech
#                 print("Processing...")
#                 text = recognizer.recognize_google(audio_data)
#                 print(f"You said: {text}")

#                 # Exit loop if "stop" is detected
#                 if text.lower() == "stop":
#                     print("Stop command detected. Stopping recognition...")
#                     is_listening = False
#                     break

#             except sr.UnknownValueError:
#                 print("Sorry, I couldn't understand. Please try again.")
#             except sr.RequestError as e:
#                 print(f"API request error: {e}")
#                 is_listening = False
#             except Exception as e:
#                 print(f"An error occurred: {e}")
#                 is_listening = False

# @app.route('/')
# def home():
#     """
#     Render the UI.
#     """
#     return render_template('index.html')

# @app.route('/start', methods=['POST'])
# def start_recognition():
#     """
#     Start the continuous speech recognition process.
#     """
#     global is_listening

#     if is_listening:
#         return jsonify({"message": "Recognition is already running."}), 400

#     is_listening = True
#     threading.Thread(target=continuous_recognition).start()
#     return jsonify({"message": "Speech recognition started."}), 200

# @app.route('/stop', methods=['POST'])
# def stop_recognition():
#     """
#     Stop the continuous speech recognition process.
#     """
#     global is_listening

#     if not is_listening:
#         return jsonify({"message": "Recognition is not running."}), 400

#     is_listening = False
#     return jsonify({"message": "Speech recognition stopped."}), 200

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5000)

# from flask import Flask, render_template, request, jsonify
# from students_data import students

# app = Flask(__name__)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     roll_number = None
#     if request.method == "POST":
#         student_name = request.form.get("student_name")
#         roll_number = students.get(student_name, "Roll number not found")
#     return render_template("index.html", roll_number=roll_number)

# @app.route("/api/get_roll_number", methods=["POST"])
# def get_roll_number():
#     data = request.json
#     student_name = data.get("student_name")
#     roll_number = students.get(student_name, "Roll number not found")
#     return jsonify({"student_name": student_name, "roll_number": roll_number})

# if __name__ == "__main__":
#     app.run(debug=True)
