from flask import Flask, request, jsonify, render_template
import matplotlib.pyplot as plt
import numpy as np
import os
import uuid
import numexpr as ne

app = Flask(__name__)

# Static directory for images
STATIC_DIR = os.path.join(app.root_path, 'static')
os.makedirs(STATIC_DIR, exist_ok=True)

def safe_eval(func_str):
    """
    Safely evaluate mathematical functions using numexpr
    """
    # Predefined safe functions
    safe_functions = {
        'sin': 'sin', 'cos': 'cos', 'tan': 'tan',
        'arcsin': 'arcsin', 'arccos': 'arccos', 'arctan': 'arctan',
        'sinh': 'sinh', 'cosh': 'cosh', 'tanh': 'tanh',
        'log': 'log10', 'ln': 'log', 
        'sqrt': 'sqrt', 'abs': 'abs', 
        'exp': 'exp'
    }
    
    # Replace mathematical symbols
    func_str = func_str.replace('^', '**').replace('π', 'pi')
    
    # Replace function names with their numexpr equivalents
    for name, func in safe_functions.items():
        func_str = func_str.replace(name, func)
    
    # Compile function for later use
    def compiled_func(x):
        try:
            # Evaluate the function using numexpr
            return ne.evaluate(func_str, local_dict={'x': x, 'pi': np.pi, 'e': np.e})
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

        # Remove values where tan(x) would be undefined (multiples of pi/2)
        x = x[np.abs(np.cos(x)) > 0.001]  # Avoid division by zero (tan(x) = sin(x)/cos(x))

        try:
            # Compile and evaluate function
            func_eval = safe_eval(func)
            y = func_eval(x)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        # Handle undefined values (like infinities from tan)
        y = np.nan_to_num(y, nan=0, posinf=0, neginf=0)

        # Plot configuration
        plt.figure(figsize=(10, 6), dpi=100)
        plt.plot(x, y, color='#007bff', linewidth=2, label=f"f(x) = {func}")
        plt.title("Lecheheb Hocine Math", fontsize=15)
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
    app.run(debug=False, host='0.0.0.0', port=5000)