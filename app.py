from flask import Flask, request, jsonify, render_template
import matplotlib.pyplot as plt
import numpy as np
import os
import uuid
import math

app = Flask(__name__)

# Static directory for images
STATIC_DIR = os.path.join(app.root_path, 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

def safe_eval(func_str):
    """
    Safely evaluate mathematical functions
    """
    # Predefined safe functions
    safe_functions = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'arcsin': np.arcsin, 'arccos': np.arccos, 'arctan': np.arctan,
        'sinh': np.sinh, 'cosh': np.cosh, 'tanh': np.tanh,
        'log': np.log10, 'ln': np.log, 
        'sqrt': np.sqrt, 'abs': np.abs, 
        'exp': np.exp
    }
    
    # Replace mathematical symbols
    func_str = func_str.replace('^', '**').replace('π', 'pi')
    
    # Compile function for later use
    def compiled_func(x):
        try:
            # Create a local copy of function string to avoid scope issues
            local_func_str = func_str
            
            # Replace function names with their numpy equivalents
            for name, func in safe_functions.items():
                local_func_str = local_func_str.replace(name, f'safe_functions["{name}"]')
            
            # Evaluate the function
            return eval(local_func_str, 
                        {"__builtins__": None, "x": x, "pi": np.pi, "e": np.e}, 
                        {"safe_functions": safe_functions})
        except Exception as e:
            raise ValueError(f"خطأ في الدالة: {str(e)}")
    
    return compiled_func

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot_graph():
    try:
        # Get function from request
        data = request.get_json()
        func = data.get('function', '').strip()

        if not func:
            return jsonify({"error": "الدالة مطلوبة"}), 400

        # Prepare x values
        x = np.linspace(-10, 10, 1000)

        try:
            # Compile and evaluate function
            func_eval = safe_eval(func)
            y = func_eval(x)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        # Handle undefined values
        y = np.nan_to_num(y, nan=0, posinf=0, neginf=0)

        # Plot configuration
        plt.figure(figsize=(10, 6), dpi=100)
        plt.plot(x, y, color='#007bff', linewidth=2, label=f"f(x) = {func}")
        plt.title("LechHeb Hocine Math", fontsize=15)
        plt.xlabel("x", fontsize=12)
        plt.ylabel("f(x)", fontsize=12)
        plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
        plt.axvline(0, color='black', linewidth=0.8, linestyle='--')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.legend()

        # Save graph
        filename = f"{uuid.uuid4().hex}.png"
        filepath = os.path.join(STATIC_DIR, filename)
        plt.savefig(filepath, bbox_inches='tight')
        plt.close()

        return jsonify({"image": filename})
    except Exception as e:
        return jsonify({"error": f"خطأ غير متوقع: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=False,host = '0.0.0.0')