from flask import Flask, render_template
import data_handler

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template('main_page.html')


@app.route("/list")
def list():
    table_headers = data_handler.question_table_headers
    return render_template('list.html', table_headers=table_headers)


if __name__ == "__main__":
    app.run(
        debug='true'
    )
