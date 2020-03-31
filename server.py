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


@app.route("/search")
def search():
    search_phrase = request.args.get('search')
    table_headers = data_handler.question_table_headers[1:-1]
    if search_phrase:
        question_details = data_handler.search(search_phrase)

    return render_template('list.html', questions=question_details, table_headers=table_headers)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        id = data_handler.generate_new_id('question')
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

        data = {'id':id, 'submission': submission, 'view':view, 'vote':vote, 'title':title, 'message':message}

        data_handler.write_question_data(data)

        return redirect(f'/question/{id}')
    return render_template('add-question.html', button_text='Add new question',
                           title_text='Add a question', action_text='/add-question')


@app.route('/question/<question_id>/edit', methods=['GET', 'POST'])
def edit(question_id):
    question = data_handler.get_single_question(question_id)

    if request.method == 'POST':
        title = request.form['title'].capitalize()
        message = request.form['message'].capitalize()
        data_handler.update_question(title, message, question_id)

        new_view_number = data_handler.get_views(question_id) + 1
        data_handler.update_question_view_number(new_view_number, question_id)
        return redirect('/list')

    return render_template('add-question.html', title=question['title'], message=question['message'], question_id=question_id,
                           button_text='Save', title_text='Edit a question', action_text=f'/question/{question_id}/edit')


@app.route('/question/<question_id>', methods=['GET', 'POST'])
def id(question_id):
    answers = data_handler.get_answers(question_id)
    question_data = data_handler.get_single_question(question_id)

    if request.method == 'GET':
        new_view_number = data_handler.get_views(question_id) + 1
        data_handler.update_question_view_number(new_view_number, question_id)

    return render_template('display_question.html', question_id=question_id, question_data=question_data, answer_data=answers)


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def new_answer(question_id):
    question_data = data_handler.get_single_question(question_id)

    if request.method == 'POST':
        id = data_handler.generate_new_id('answer')
        submission_time = data_handler.current_time()
        vote_number = 0
        question_id = question_id
        message = request.form['answer']
        if request.files:
            target = os.path.join(APP_ROUTE, 'static/')
            image = request.files['image']
            filename = ".".join([str(submission_time), "jpg"])
            image.save("/".join([target, filename]))

        data = {'id': id, 'submission': submission_time, 'vote': vote_number, 'question_id': question_id, 'message': message}
        data_handler.write_answer_data(data)

        return redirect(f'/question/{question_id}')
    return render_template('new-answer.html', question_data=question_data, question_id=question_id)


@app.route('/question/<question_id>/vote_up')
def question_vote_up(question_id):
    vote_num_data = data_handler.get_question_vote_count(question_id)
    new_vote_num = vote_num_data['vote_number'] + 1
    data_handler.update_question_vote_number(new_vote_num, question_id)
    return redirect('/list')


@app.route('/question/<question_id>/vote_down')
def question_vote_down(question_id):
    vote_num_data = data_handler.get_question_vote_count(question_id)
    new_vote_num = vote_num_data['vote_number'] - 1
    data_handler.update_question_vote_number(new_vote_num, question_id)
    return redirect('/list')


@app.route('/answer/<answer_id>/vote_up')
def answer_vote_up(answer_id):
    vote_num_data = data_handler.get_answer_vote_count(answer_id)
    new_vote_num = vote_num_data['vote_number'] + 1
    question_id = vote_num_data['question_id']
    data_handler.update_answer_vote_number(new_vote_num, answer_id)
    return redirect(f'/question/{question_id}')


@app.route('/answer/<answer_id>/vote_down')
def answer_vote_down(answer_id):
    vote_num_data = data_handler.get_answer_vote_count(answer_id)
    new_vote_num = vote_num_data['vote_number'] - 1
    question_id = vote_num_data['question_id']
    data_handler.update_answer_vote_number(new_vote_num, answer_id)
    return redirect(f'/question/{question_id}')


@app.route('/question/<item_id>&<is_question>/delete')
def delete(item_id, is_question):
    if is_question == 'True':
        data_handler.delete_question(item_id)
    else:
        data_handler.delete_answer(item_id)
    return redirect('/list')


if __name__ == "__main__":
    app.run(
        debug='true',
        port=5000,
        host='0.0.0.0'
    )
