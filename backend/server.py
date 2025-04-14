import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from rag.rag_engine import add_chunk_to_database, retrieve_relevant_chunks, vector_db
from rag.llm_engine import get_response
from data_provider.main import get_current_data, compile_all, save_to_file
from utils.name_detection import detect_artist_from_query
from main import load_dataset_from_dict

# ✅ Force Ollama client to use the correct base URL adsda
os.environ['OLLAMA_HOST'] = "http://localhost:11434"

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/ping', methods=['GET'])
def ping():
    print("✅ Ping received")
    return jsonify({"status": "ok", "message": "pong"})

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        print("🔔 Incoming Request:", data)

        question = data.get("question", "")
        if not question:
            return jsonify({"error": "No question provided"}), 400

        print("🧠 Question:", question)

        # Detect artist name
        detected_artist = detect_artist_from_query(question)
        print("🎤 Detected Artist:", detected_artist)

        if not detected_artist:
            return jsonify({"error": "Could not detect an artist in the question"}), 400

        # Get current data and check if we need to update
        current_data = get_current_data(detected_artist)
        current_artist = current_data.get("query", "")
        
        if current_artist.lower() != detected_artist.lower():
            print(f"🔄 Updating data from {current_artist} to {detected_artist}")
            # Compile new data and save to current.txt
            new_data = compile_all(detected_artist)
            save_to_file(new_data)
            current_data = new_data

        # Extract and embed text
        dataset = load_dataset_from_dict(current_data)
        vector_db.clear()  # Clear the vector database
        
        # Add chunks to vector database
        for i, chunk in enumerate(dataset):
            try:
                add_chunk_to_database(chunk)
            except Exception as embed_err:
                print(f"❌ Embedding failed on chunk {i}: {embed_err}")
                continue

        # Get top relevant chunks and stream response
        top_chunks = retrieve_relevant_chunks(question, top_n=3)
        print("📚 Top Chunks:", top_chunks)

        response_stream = get_response(question, [chunk for chunk, _ in top_chunks])
        full_response = "".join(chunk["message"]["content"] for chunk in response_stream)

        print("💬 Final Response:", full_response)
        return jsonify({"answer": full_response})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
