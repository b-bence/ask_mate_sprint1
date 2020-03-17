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
        id = data_handler.generate_new_id('questions.csv')
        submission = data_handler.current_time()
        view = 0
        vote = 0
        title = request.form['title']
        message = request.form['message']
        data = [id, submission, view, vote, title, message]

        data_handler.write_new_data(data, 'questions.csv')

        return redirect(f'/question/{id}')
    return render_template('add-question.html')


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def id(question_id):
    row_num = 0
    questions = data_handler.get_questions()
    answers=data_handler.get_answers(question_id)
    for index, row in enumerate(questions):
        if row['id'] == question_id:
            row_num = index
    question_data = questions[row_num]
    return render_template('display_question.html', question_id=question_id, question_data=question_data, answer_data=answers)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def new_answer(question_id):
    questions = data_handler.get_questions()
    for index, row in enumerate(questions):
        if row['id'] == question_id:
            row_num = index
    question_data = questions[row_num]

    if request.method == 'POST':
        id = data_handler.generate_new_id('answers.csv')
        submission_time = data_handler.current_time()
        vote_number = 0
        question_id = question_id
        message = request.form['answer']
        image = None
        data = [id, submission_time, vote_number, question_id, message, image]
        data_handler.write_new_data(data, 'answers.csv')

        return redirect(f'/question/{question_id}')
    return render_template('new-answer.html', question_data=question_data, question_id=question_id)


if __name__ == "__main__":
    app.run(
        debug='true'
    )
