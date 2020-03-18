from flask import Flask, render_template, request, redirect
import data_handler

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template('main_page.html')


@app.route("/list")
@app.route("/list<header>&<direction>")
def list(header=None, direction=None):
    questions = data_handler.get_questions()
    table_headers = data_handler.question_table_headers
    if header not in data_handler.csv_question_headers or direction not in ['asc', 'desc']:
        return render_template('list.html', table_headers=table_headers, questions=questions)
    else:
        sorted_questions = data_handler.sort_by(questions, header, direction)
        return render_template('list.html', table_headers=table_headers, questions=sorted_questions)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        id = data_handler.generate_new_id('questions.csv')
        submission = data_handler.current_time()
        view = 0
        vote = 0
        title = request.form['title'].capitalize()
        message = request.form['message'].capitalize()
        data = [id, submission, view, vote, title, message]

        data_handler.write_new_data(data, 'questions.csv')

        return redirect(f'/question/{id}')
    return render_template('add-question.html')


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def id(question_id):
    row_num = 0
    questions = data_handler.get_questions()
    answers = data_handler.get_answers(question_id)
    for index, row in enumerate(questions):
        if row['id'] == question_id:
            row_num = index
    question_data = questions[row_num]

    if request.method == 'GET':
        csv_question_headers = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
        questions[row_num]['view_number'] = int(question_data['view_number']) + 1
        data_handler.update_view_number(questions)

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


@app.route('/question/<question_id>/delete')
def delete_question(question_id):
    questions = data_handler.get_questions()
    question = None
    for row in questions:
        if row['id'] == question_id:
            question = row
            break
    print(question)
    print(questions.index(question))
    questions.pop(questions.index(question))
    data_handler.update_view_number(questions)
    return render_template('main_page.html')


if __name__ == "__main__":
    app.run(
        debug='true',
        port=5000,
        host='0.0.0.0'
    )
