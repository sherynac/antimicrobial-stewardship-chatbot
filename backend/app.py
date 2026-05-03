from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/chat', methods=['POST'])
def chat():
    if request.method == 'POST':
        name = request.form['username']
        return f"Hello {name}, POST request received"
    return render_template('name.html')

if __name__ == '__main__':
    app.run()