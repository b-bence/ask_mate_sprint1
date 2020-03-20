from flask import Flask, render_template, request, redirect
import data_handler
import os

app = Flask(__name__)
APP_ROUTE = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def main_page():
    return render_template('main_page.html')


@app.route("/list")
@app.route("/list<header>&<direction>")
def list(header=None, direction=None):
    questions = data_handler.get_questions_data()
    table_headers = data_handler.question_table_headers[1:-1]
    if header not in data_handler.question_table_headers or direction not in ['asc', 'desc']:
        return render_template('list.html', table_headers=table_headers, questions=questions)
    else:
        valid_header = header.replace(' ', '_').lower()
        sorted_questions = data_handler.sort_by(valid_header, direction)
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
        if request.files:
            target = os.path.join(APP_ROUTE, 'static/')
            image = request.files['image']
            filename = ".".join([str(submission), "jpg"])
            image.save("/".join([target, filename]))

        data = [id, submission, view, vote, title, message]

        data_handler.write_new_data(data, 'questions.csv')

        return redirect(f'/question/{id}')
    return render_template('add-question.html', button_text='Add new question',
                           title_text='Add a question', action_text='/add-question')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit(question_id):
    questions = data_handler.get_questions_data()
    question = [row for row in questions if row['id'] == question_id]

    if request.method == 'POST':
        title = request.form['title'].capitalize()
        message = request.form['message'].capitalize()
        list_index = questions.index(question[0])
        question[0]['title'] = title
        question[0]['message'] = message
        questions[list_index] = question[0]
        data_handler.update_question_view_number(questions)
        return redirect('/list')

    return render_template('add-question.html', title=question[0]['title'], message=question[0]['message'], question_id=question_id,
                           button_text='Save', title_text='Edit a question', action_text=f'/question/{question_id}/edit')


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def id(question_id):
    questions = data_handler.get_questions_data()
    answers = data_handler.get_answers(question_id)
    row_num = data_handler.get_row(question_id, questions)
    question_data = questions[row_num]

    if request.method == 'GET':
        questions[row_num]['view_number'] = int(question_data['view_number']) + 1
        data_handler.update_question_view_number(questions)

    return render_template('display_question.html', question_id=question_id, question_data=question_data, answer_data=answers)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def new_answer(question_id):
    questions = data_handler.get_questions_data()
    row_num = data_handler.get_row(question_id, questions)
    question_data = questions[row_num]

    if request.method == 'POST':
        id = data_handler.generate_new_id('answers.csv')
        submission_time = data_handler.current_time()
        vote_number = 0
        question_id = question_id
        message = request.form['answer']
        if request.files:
            target = os.path.join(APP_ROUTE, 'static/')
            image = request.files['image']
            filename = ".".join([str(submission_time), "jpg"])
            image.save("/".join([target, filename]))
        data = [id, submission_time, vote_number, question_id, message]
        data_handler.write_new_data(data, 'answers.csv')

        return redirect(f'/question/{question_id}')
    return render_template('new-answer.html', question_data=question_data, question_id=question_id)


@app.route('/question/<question_id>/vote_up')
def question_vote_up(question_id):
    questions = data_handler.change_question_vote_count(question_id, +1)
    data_handler.update_question_view_number(questions)
    return redirect('/list')


@app.route('/question/<question_id>/vote_down')
def question_vote_down(question_id):
    questions = data_handler.change_question_vote_count(question_id, -1)
    data_handler.update_question_view_number(questions)
    return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
def answer_vote_up(answer_id):
    answers = data_handler.change_answer_vote_count(answer_id, +1)
    row_num = data_handler.get_row(answer_id, answers)
    question_id = answers[row_num]['question_id']
    data_handler.update_answer_view_number(answers)
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/vote_down')
def answer_vote_down(answer_id):
    answers = data_handler.change_answer_vote_count(answer_id, -1)
    row_num = data_handler.get_row(answer_id, answers)
    question_id = answers[row_num]['question_id']
    data_handler.update_answer_view_number(answers)
    return redirect(f'/question/{question_id}')


@app.route('/question/<item_id>&<is_question>/delete')
def delete_question(item_id, is_question):
    if is_question == 'True':
        data_handler.delete(item_id, True)
        return redirect('/list')
    else:
        data_handler.delete(item_id, False)
        return redirect('/list')


if __name__ == "__main__":
    app.run(
        debug='true',
        port=5000,
        host='0.0.0.0'
    )
