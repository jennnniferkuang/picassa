from flask import Flask, request, jsonify, send_file
import os
from flask_cors import CORS
import time
import base64
import json
from datetime import datetime
from openai import OpenAI  
from dotenv import load_dotenv
import io
from PIL import Image

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

image_dir = "captured_images"
feedback_interval = 10
cleanup_interval = feedback_interval * 2

# Ensure the image directory exists
os.makedirs(image_dir, exist_ok=True)

def get_sorted_images():
    files = [f for f in os.listdir(image_dir) if f.endswith(".png")]
    files.sort(key=lambda f: os.path.getctime(os.path.join(image_dir, f)))
    return files

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def give_feedback(image_path):
    image_b64 = image_to_base64(image_path)
    image_url = f"data:image/png;base64,{image_b64}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an art critic. Provide constructive, kind feedback on a drawing work in progress."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Here is my current drawing. What should I improve on?"},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
        )
        feedback = response.choices[0].message.content
        timestamp = datetime.now().strftime("%H:%M:%S")
        return {
            "feedback": feedback,
            "timestamp": timestamp,
            "image_name": os.path.basename(image_path)
        }
    except Exception as e:
        return {"error": str(e)}

def delete_oldest_image():
    images = get_sorted_images()
    if images:
        oldest = os.path.join(image_dir, images[0])
        os.remove(oldest)
        return {"deleted": os.path.basename(oldest)}
    return {"deleted": None}


@app.route('/feedback/latest', methods=['GET'])
def get_latest_feedback():
    """Get feedback for the latest image in the captured_images directory"""
    try:
        images = get_sorted_images()
        if not images:
            return jsonify({"error": "No images found in captured_images directory"}), 404
        
        latest_image = os.path.join(image_dir, images[-1])
        result = give_feedback(latest_image)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback/image/<filename>', methods=['GET'])
def get_feedback_for_image(filename):
    """Get feedback for a specific image by filename"""
    try:
        image_path = os.path.join(image_dir, filename)
        if not os.path.exists(image_path):
            return jsonify({"error": f"Image {filename} not found"}), 404
        
        result = give_feedback(image_path)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_image():
    """Upload an image for feedback"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and file.filename.lower().endswith('.png'):
            # Save the uploaded image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"upload_{timestamp}.png"
            filepath = os.path.join(image_dir, filename)
            file.save(filepath)
            
            # Get feedback for the uploaded image
            result = give_feedback(filepath)
            
            if "error" in result:
                return jsonify(result), 500
            
            return jsonify({
                "message": "Image uploaded and feedback generated",
                "filename": filename,
                "feedback": result
            })
        else:
            return jsonify({"error": "Only PNG files are supported"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images', methods=['GET'])
def list_images():
    """List all images in the captured_images directory"""
    try:
        images = get_sorted_images()
        image_info = []
        
        for img in images:
            filepath = os.path.join(image_dir, img)
            stat = os.stat(filepath)
            image_info.append({
                "filename": img,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "size": stat.st_size
            })
        
        return jsonify({"images": image_info})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    """Get a specific image by filename"""
    try:
        filepath = os.path.join(image_dir, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": f"Image {filename} not found"}), 404
        
        return send_file(filepath, mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cleanup', methods=['POST'])
def cleanup_old_images():
    """Delete the oldest image in the directory"""
    try:
        result = delete_oldest_image()
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/feedback/stream/<filename>', methods=['GET'])
def stream_feedback_for_image(filename):
    """Stream feedback for a specific image (Server-Sent Events)"""
    from flask import Response
    
    def generate():
        try:
            image_path = os.path.join(image_dir, filename)
            if not os.path.exists(image_path):
                yield f"data: {json.dumps({'error': f'Image {filename} not found'})}\n\n"
                return
            
            image_b64 = image_to_base64(image_path)
            image_url = f"data:image/png;base64,{image_b64}"

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an art critic. Provide constructive, kind feedback on a drawing work in progress."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here is my current drawing. What should I improve on?"},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                stream=True 
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

@app.route('/critique/stream', methods=['POST'])
def stream_critique():
    """Stream critique response for an uploaded image"""
    from flask import Response
    
    def generate():
        try:
            if 'image' not in request.files:
                yield f"data: {json.dumps({'error': 'No image file provided'})}\n\n"
                return
            
            file = request.files['image']
            if file.filename == '':
                yield f"data: {json.dumps({'error': 'No file selected'})}\n\n"
                return
            
            if not file.filename.lower().endswith('.png'):
                yield f"data: {json.dumps({'error': 'Only PNG files are supported'})}\n\n"
                return
            
            # Save the uploaded image temporarily
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"critique_{timestamp}.png"
            filepath = os.path.join(image_dir, filename)
            file.save(filepath)
            
            # Convert image to base64
            image_b64 = image_to_base64(filepath)
            image_url = f"data:image/png;base64,{image_b64}"

            # Stream the critique response
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an art critic. Provide constructive, kind feedback on a drawing work in progress. Be specific about what works well and what could be improved."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here is my current drawing. What should I improve on?"},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                stream=True 
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            # Clean up the temporary file
            try:
                os.remove(filepath)
            except:
                pass
                
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/critique/latest/stream', methods=['GET'])
def stream_critique_latest():
    """Stream critique response for the latest image in captured_images directory"""
    from flask import Response
    
    def generate():
        try:
            images = get_sorted_images()
            if not images:
                yield f"data: {json.dumps({'error': 'No images found in captured_images directory'})}\n\n"
                return
            
            latest_image = os.path.join(image_dir, images[-1])
            
            # Convert image to base64
            image_b64 = image_to_base64(latest_image)
            image_url = f"data:image/png;base64,{image_b64}"

            # Stream the critique response
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an art critic. Provide constructive, kind feedback on a drawing work in progress. Be specific about what works well and what could be improved."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Here is my current drawing. What should I improve on?"},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                stream=True 
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
                
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 