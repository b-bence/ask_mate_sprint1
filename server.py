from flask import Flask, render_template, request, redirect
import data_handler

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template('main_page.html')


@app.route("/list")
def list():
    questions = data_handler.get_questions()
    table_headers = data_handler.question_table_headers
    return render_template('list.html', table_headers=table_headers, questions=questions)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        id = data_handler.generate_question_id()
        submission = 'None'
        view = 0
        vote = 0
        title = request.form['title']
        message = request.form['message']
        data = [id, submission, view, vote, title, message]

        data_handler.write_question_data(data)

        return redirect(f'/question/{id}')
    return render_template('add-question.html')


@app.route('/question/<question_id>', methods=['GET','POST'])
def id(question_id):
    row_num = 0
    table_headers = data_handler.question_table_headers
    questions = data_handler.get_questions()
    answers=data_handler.get_answers()
    for index, row in enumerate(questions):
        if row['id'] == question_id:
            row_num = index
    question_data = questions[row_num]
    try:
        answer_data = answers[row_num]
    except IndexError:
        answer_data = "No answer yet"

    return render_template('display_question.html'
                           , question_data=question_data, answer_data=answer_data, table_headers=table_headers)


if __name__ == "__main__":
    app.run(
        debug='true'
    )
