from flask import Flask, render_template_string, request
import requests
import json
import base64

app = Flask(__name__)

OPENROUTER_API_KEY = "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"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Image Generator</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f7f7f7; }
        input, button { padding: 10px; font-size: 16px; width: 300px; margin-top: 10px; }
        img { margin-top: 30px; max-width: 500px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>🧠 AI Image Generator</h1>
    <form method="POST">
        <input name="prompt" placeholder="Enter your image description..." required>
        <br>
        <button type="submit">Generate Image</button>
    </form>
    {% if image_data %}
        <h2>Result:</h2>
        <img src="data:image/png;base64,{{ image_data }}" alt="Generated Image">
    {% elif error %}
        <p class="error">{{ error }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    image_data = None
    error = None

    if request.method == "POST":
        prompt = request.form.get("prompt", "")
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "X-Title": "Flask Image Bot",
                    "HTTP-Referer": "http://localhost:5000"
                },
                data=json.dumps({
                    "model": "google/gemini-2.5-flash-image",
                    "messages": [
                        {"role": "user", "content": [{"type": "text", "text": prompt}]}
                    ]
                }),
                timeout=60
            )

            data = response.json()
            print("🔍 API Response:\n", json.dumps(data, indent=2))

            # ✅ Correct Base64 path
            image_data = (
                data["choices"][0]["message"]["content"][0]["image_url"]["data"]
            )

            # Just to verify if it's valid Base64
            try:
                base64.b64decode(image_data)
            except Exception:
                error = "⚠️ Received data is not valid base64 image data."
                image_data = None

        except Exception as e:
            error = f"Error: {e}"

    return render_template_string(HTML_TEMPLATE, image_data=image_data, error=error)


if __name__ == "__main__":
    app.run(debug=True)
