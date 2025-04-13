from flask import Flask, request, jsonify
from rag.rag_engine import add_chunk_to_database, retrieve_relevant_chunks
from rag.llm_engine import get_response
from data_provider.main import get_current_data, compile_all, save_to_file
from utils.name_detection import detect_artist_from_query
from main import load_dataset_from_dict
import os

app = Flask(__name__)

@app.route('/ping', methods=['GET'])
def ping():
    print("✅ Ping received")
    return "pong"


@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        print("🔔 Incoming Request:", data)

        question = data.get("question", "")
        print("🧠 Question:", question)

        detected_artist = detect_artist_from_query(question)
        print("🎤 Detected Artist:", detected_artist)

        if detected_artist:
            artist_data = compile_all(detected_artist)
            save_to_file(artist_data)
        else:
            artist_data = get_current_data()

        dataset = load_dataset_from_dict(artist_data)

        # Clear and embed new chunks
        from rag.rag_engine import VECTOR_DB
        VECTOR_DB.clear()

        for chunk in dataset:
            add_chunk_to_database(chunk)

        top_chunks = retrieve_relevant_chunks(question, top_n=3)
        print("📚 Top Chunks:", top_chunks)

        response_stream = get_response(question, [chunk for chunk, _ in top_chunks])
        full_response = "".join(chunk["message"]["content"] for chunk in response_stream)

        print("💬 Final Response:", full_response)
        return jsonify({"answer": full_response})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500

    try:
        question = request.json.get("question", "")

        # Detect artist from query
        detected_artist = detect_artist_from_query(question)
        if detected_artist:
            print(f"🔍 Detected artist: {detected_artist}")
            data = compile_all(detected_artist)
            save_to_file(data)
        else:
            data = get_current_data()

        dataset = load_dataset_from_dict(data)

        # Clear vector DB each time (optional)
        from rag.rag_engine import VECTOR_DB
        VECTOR_DB.clear()

        for chunk in dataset:
            add_chunk_to_database(chunk)

        top_chunks = retrieve_relevant_chunks(question, top_n=3)
        response_stream = get_response(question, [chunk for chunk, _ in top_chunks])
        full_response = "".join(chunk["message"]["content"] for chunk in response_stream)

        return jsonify({ "answer": full_response })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
