from flask import Flask, request, render_template
import ast
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import spacy
import textwrap
app = Flask(__name__)

# Load the English language model
nlp = spacy.load("en_core_web_sm")

def generateExplanationText(code):
    if isinstance(code, dict):
        explanation = ""
        for key, value in code.items():
            explanation += f"The variable {key} has a value of {value}.\n"
        return explanation

    explanation = ""

    # Analyze the code snippet
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                explanation += f"The code assigns a value to the variable {node.targets[0].id}. This value is {ast.unparse(node.value)}.\n"
            elif isinstance(node, ast.Expr):
                explanation += f"The code evaluates the expression {ast.unparse(node.value)}. This means it calculates the result of the expression.\n"
            elif isinstance(node, ast.If):
                explanation += f"The code checks if the condition {ast.unparse(node.test)} is true. If it is, the code inside the if statement will run.\n"
            elif isinstance(node, ast.For):
                explanation += f"The code loops over the iterable {ast.unparse(node.iter)}. This means it will run the code inside the loop for each item in the iterable.\n"
            elif isinstance(node, ast.While):
                explanation += f"The code loops while the condition {ast.unparse(node.test)} is true. This means it will keep running the code inside the loop until the condition is no longer true.\n"
            # Add more cases for other types of nodes
    except SyntaxError:
        explanation = "Invalid syntax"

    return explanation

def analyze_code(code):
    try:
        tree = ast.parse(code)
        explanation = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                explanation.append({
                    'type': 'function',
                    'name': node.name,
                    'line': node.lineno,
                    'args': [arg.arg for arg in node.args.args]
                })
            elif isinstance(node, ast.For):
                explanation.append({
                    'type': 'for_loop',
                    'target': ast.dump(node.target),
                    'line': node.lineno
                })
            elif isinstance(node, ast.If):
                explanation.append({
                    'type': 'if_statement',
                    'condition': ast.dump(node.test),
                    'line': node.lineno
                })
            elif isinstance(node, ast.While):
                explanation.append({
                    'type': 'while_loop',
                    'condition': ast.dump(node.test),
                    'line': node.lineno
                })
            elif isinstance(node, ast.Assign):
                targets = [ast.dump(t) for t in node.targets]
                value = ast.dump(node.value)
                explanation.append({
                    'type': 'assignment',
                    'targets': targets,
                    'value': value,
                    'line': node.lineno
                })
        return explanation
    except Exception as e:
        return [{'type': 'error', 'message': str(e)}]

@app.route('/', methods=['GET', 'POST'])
def home():
    code = request.form.get('code', '')
    explanation = []
    highlighted_code = ''

    if request.method == 'POST':
        explanation = analyze_code(code)
        highlighted_code = highlight(code, PythonLexer(), HtmlFormatter(noclasses=True))

    return render_template('index.html', code=code, explanation=explanation, highlighted_code=highlighted_code,
                           generateExplanationText=generateExplanationText)

if __name__ == '__main__':
    app.run(debug=True)

