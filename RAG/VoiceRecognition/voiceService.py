from flask import Flask, jsonify
import threading
import speech_recognition as sr

app = Flask(__name__)

# Global variable to control the listening thread
is_listening = False

def continuous_recognition():
    """
    Continuously listen to the microphone until "stop" is detected.
    """
    global is_listening
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait.")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        print("Listening... Say 'stop' to exit.")

        while is_listening:
            try:
                print("Listening for your command...")
                audio_data = recognizer.listen(source, timeout=12)

                # Recognize the speech
                print("Processing...")
                text = recognizer.recognize_google(audio_data)
                print(f"You said: {text}")

                # Exit loop if "stop" is detected
                if text.lower() == "stop":
                    print("Stop command detected. Stopping recognition...")
                    is_listening = False
                    break

            except sr.UnknownValueError:
                print("Sorry, I couldn't understand. Please try again.")
            except sr.RequestError as e:
                print(f"API request error: {e}")
                is_listening = False
            except Exception as e:
                print(f"An error occurred: {e}")
                is_listening = False

@app.route('/start', methods=['POST'])
def start_recognition():
    """
    Start the continuous speech recognition process.
    """
    global is_listening

    if is_listening:
        return jsonify({"message": "Recognition is already running."}), 400

    is_listening = True
    threading.Thread(target=continuous_recognition).start()
    return jsonify({"message": "Speech recognition started."}), 200

@app.route('/stop', methods=['POST'])
def stop_recognition():
    """
    Stop the continuous speech recognition process.
    """
    global is_listening

    if not is_listening:
        return jsonify({"message": "Recognition is not running."}), 400

    is_listening = False
    return jsonify({"message": "Speech recognition stopped."}), 200

@app.route('/')
def health_check():
    """
    Health check endpoint.
    """
    return jsonify({"message": "Voice Recognition Microservice is running!"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

#--------------Continuous listning----------------------
# import speech_recognition as sr

# def continuous_recognition():
#     # Initialize the recognizer
#     recognizer = sr.Recognizer()

#     # Use the microphone as the audio source
#     with sr.Microphone() as source:
#         print("Adjusting for ambient noise... Please wait.")
#         recognizer.adjust_for_ambient_noise(source, duration=2)
#         print("Listening... Say 'stop' to exit.")

#         while True:
#             try:
#                 # Capture audio data
#                 print("Listening for your command...")
#                 audio_data = recognizer.listen(source, timeout=10)

#                 # Recognize the speech
#                 print("Processing...")
#                 text = recognizer.recognize_google(audio_data)
#                 print(f"You said: {text}")

#                 # Exit the loop if the user says "stop"
#                 if text.lower() == "stop":
#                     print("Stopping the recognition...")
#                     break

#             except sr.UnknownValueError:
#                 print("Sorry, I couldn't understand what you said. Please try again.")
#             except sr.RequestError as e:
#                 print(f"Could not request results from the API: {e}")
#                 break
#             except Exception as e:
#                 print(f"An unexpected error occurred: {e}")
#                 break

# if __name__ == "__main__":
#     print("Starting continuous voice recognition...")
#     continuous_recognition()
#     print("Voice recognition stopped.")



#---------------LISTEN ONE TIME------------------------
# import speech_recognition as sr

# def recognize_speech():
#     # Initialize the recognizer
#     recognizer = sr.Recognizer()

#     # Use the microphone as the audio source
#     with sr.Microphone() as source:
#         print("Adjusting for ambient noise... Please wait.")
#         recognizer.adjust_for_ambient_noise(source, duration=2)
#         print("Listening... Speak now.")

#         try:
#             # Capture the audio
#             audio_data = recognizer.listen(source, timeout=10)
#             print("Recognizing...")
            
#             # Recognize the speech using Google Web Speech API
#             text = recognizer.recognize_google(audio_data)
#             print("You said: ", text)
#             return text

#         except sr.UnknownValueError:
#             print("Sorry, I couldn't understand what you said.")
#             return None
#         except sr.RequestError as e:
#             print(f"Could not request results from Google Speech Recognition service: {e}")
#             return None
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             return None

# if __name__ == "__main__":
#     print("Starting voice recognition...")
#     result = recognize_speech()
#     if result:
#         print(f"Recognized text: {result}")
#     else:
#         print("No valid speech recognized.")
