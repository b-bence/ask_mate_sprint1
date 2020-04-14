from flask import Flask, render_template, request, redirect, url_for, session
import data_handler
import os

app = Flask(__name__)
APP_ROUTE = os.path.dirname(os.path.abspath(__file__))
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route("/")
def main_page():
    questions = data_handler.get_latest_questions()
    if 'username' in session:
        logged_in = True
        user = session['username']
        return render_template('main_page.html', questions=questions, logged_in=logged_in, user=user)
    return render_template('main_page.html', questions=questions)


@app.route("/list")
@app.route("/list<header>&<direction>")
def list(header=None, direction=None):
    if 'username' in session:
        logged_in = True
    else:
        logged_in = False
    questions = data_handler.get_questions_data()
    table_headers = data_handler.question_table_headers[1:-1]
    if header not in data_handler.question_table_headers or direction not in ['asc', 'desc']:
        return render_template('list.html', table_headers=table_headers, questions=questions, logged_in=logged_in)
    else:
        valid_header = header.replace(' ', '_').lower()
        sorted_questions = data_handler.sort_by(valid_header, direction)
        return render_template('list.html', table_headers=table_headers, questions=sorted_questions, logged_in=logged_in)


@app.route("/search")
def search():
    search_phrase = request.args.get('search')
    table_headers = data_handler.question_table_headers[1:-1]

    if search_phrase:
        question_details = data_handler.search(search_phrase)
        replace_to = f'<span style="background-color: yellow;">{search_phrase}</span>'
        answer_message = data_handler.fancy_search(search_phrase)

    return render_template('list.html', questions=question_details, table_headers=table_headers,
                           search_phrase=search_phrase, replace_to=replace_to, answer_message=answer_message)


@app.route("/add-question", methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        id = data_handler.generate_new_id('question')
        submission = data_handler.current_time()
        view = 0
        vote = 0
        title = request.form['title'].capitalize()
        message = request.form['message'].capitalize()
        user_data = data_handler.get_user_data(session['username'])
        remove_list = 0
        user_id = user_data[remove_list]['id']
        if request.files:
            target = os.path.join(APP_ROUTE, 'static/')
            image = request.files['image']
            filename = ".".join([str(submission), "jpg"])
            image.save("/".join([target, filename]))

        data = {'id': id, 'submission': submission, 'view': view, 'vote': vote,
                'title': title, 'message': message, 'filename': filename, 'user_id': user_id}
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
    all_tags = data_handler.get_all_tags()
    question_tags = data_handler.get_question_tags(question_id)
    answers = data_handler.get_answers(question_id)
    question_data = data_handler.get_single_question(question_id)
    comments = data_handler.get_comments()

    if request.method == 'GET':
        new_view_number = data_handler.get_views(question_id) + 1
        data_handler.update_question_view_number(new_view_number, question_id)

    if 'username' in session:
        logged_in = True
    else:
        logged_in = False

    return render_template('display_question.html', question_id=question_id, question_data=question_data,
                           answer_data=answers, question_tags=question_tags, comments=comments,
                           logged_in=logged_in)


@app.route('/question/<question_id>/new-tag', methods=['GET', 'POST'])
def tag_question(question_id):
    all_tags = data_handler.get_all_tags()
    tag_names = [x['name'] for x in all_tags]
    if request.method == 'POST':
        try:
            if request.form['new_tag'] not in tag_names:
                tag_name = request.form['new_tag']
                new_id = data_handler.get_max_tag_id() + 1
                data_handler.add_new_tag_to_list(new_id, tag_name)
                return redirect(f'/question/{question_id}/new-tag')
        except KeyError:
            tags = request.form.getlist('tags')
            for tag in tags:
                tag_id = data_handler.get_tag_id(tag)
                data_handler.add_tag_to_question(question_id, tag_id)
            return redirect(f'/question/{question_id}')
    return render_template('add_tag.html', all_tags=all_tags, question_id=question_id)


@app.route('/answer/<answer_id>/edit', methods=['GET', 'POST'])
def edit_answer(answer_id):
    answer_data = data_handler.get_single_answer(answer_id)
    question_id = answer_data['question_id']
    question_data = data_handler.get_single_question(question_id)

    if request.method == 'POST':
        message = request.form['answer']
        data_handler.update_answer(answer_id, message)
        return redirect(f'/question/{question_id}')
    return render_template('new-answer.html', answer_data=answer_data, question_data=question_data,
                           question_id=question_id, todo='Edit', action_text=f'/answer/{answer_id}/edit')


@app.route('/question/<question_id>/new-answer', methods=['GET', 'POST'])
def new_answer(question_id):
    question_data = data_handler.get_single_question(question_id)

    if request.method == 'POST':
        id = data_handler.generate_new_id('answer')
        submission_time = data_handler.current_time()
        vote_number = 0
        question_id = question_id
        message = request.form['answer']
        user_data = data_handler.get_user_data(session['username'])
        remove_list = 0
        user_id = user_data[remove_list]['id']
        filename=None
        if request.files and request.files['image']:
            target = os.path.join(APP_ROUTE, 'static/')
            image = request.files['image']
            filename = ".".join([str(submission_time), "jpg"])
            image.save("/".join([target, filename]))

        data = {'id': id, 'submission': submission_time, 'vote': vote_number, 'question_id': question_id,
                'message': message, 'filename': filename, 'user_id': user_id}
        data_handler.write_answer_data(data)

        return redirect(f'/question/{question_id}')
    return render_template('new-answer.html', question_data=question_data, question_id=question_id, todo='Add',
                           action_text=f'/question/{question_id}/new-answer', answer_data=None)


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
        data_handler.delete_answer_comments(item_id)
        data_handler.delete_answer(item_id)
    return redirect('/list')


@app.route('/question/<question_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_question(question_id):
    if request.method == 'POST':
        comment = request.form['comment']
        submission_time = data_handler.current_time()
        user_data = data_handler.get_user_data(session['username'])
        remove_list = 0
        user_id = user_data[remove_list]['id']
        data_handler.new_comment_for_question(question_id, comment, submission_time, user_id)
        return redirect(f'/question/{question_id}')
    return render_template('new_comment.html', action=f'/question/{question_id}/new-comment', title='Add comment')


@app.route('/answer/<answer_id>/new-comment', methods=['GET', 'POST'])
def add_comment_to_answer(answer_id):
    if request.method == 'POST':
        comment = request.form['comment']
        submission_time = data_handler.current_time()
        user_data = data_handler.get_user_data(session['username'])
        remove_list = 0
        user_id = user_data[remove_list]['id']
        data_handler.new_comment_for_answer(answer_id, comment, submission_time, user_id)
        question_id = data_handler.get_question_id_by_answer(answer_id)
        return redirect(f'/question/{question_id}')
    return render_template('new_comment.html', action=f'/answer/{answer_id}/new-comment', title='Add comment')


@app.route('/question/<question_id>/tag/<tag_id>/delete')
def delete_tag(question_id, tag_id):
    data_handler.delete_tag(question_id, tag_id)
    return redirect(f'/question/{question_id}')


@app.route('/comments/<comment_id>/delete')
def delete_comment(comment_id):
    question_id = data_handler.get_question_id_by_comment(comment_id)
    data_handler.delete_comment_by_id(comment_id)
    return redirect(f'/question/{question_id}')


@app.route('/comment/<comment_id>/edit', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comment = data_handler.get_comment_by_id(comment_id)
    edited_count = comment['edited_count']
    if request.method == 'POST':
        message = request.form['comment']
        if edited_count is None:
            edited_count = 1
        else:
            edited_count += 1
        question_id = data_handler.get_question_id_by_comment(comment_id)
        data_handler.update_comment_by_id(comment_id, message, edited_count)
        return redirect(f'/question/{question_id}')

    return render_template('new_comment.html', action=f'/comment/{comment_id}/edit',
                           title='Edit comment', input_value=comment["message"])


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    title_text = 'Register new account'

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = data_handler.hash_password(password)
        registration_date = data_handler.current_time()
        data_handler.add_user(email,hashed_password, registration_date)
        return redirect(url_for('main_page'))
    return render_template('registration.html', title_text=title_text)


@app.route('/login', methods=['GET', 'POST'])
def login():
    title_text = 'Login'

    if request.method == 'POST':
        email = request.form['email']
        input_password = request.form['password']
        correct_password = data_handler.get_user_data(email)
        remove_list = 0
        if correct_password \
                and data_handler.verify_password(input_password, correct_password[remove_list]['password']):
            session['username'] = email
            return redirect(url_for('main_page'))
        else:
            error_message = "Wrong password or email!"
            return render_template('login.html', title_text=title_text,error_message=error_message)
    return render_template('login.html', title_text=title_text)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('main_page'))


if __name__ == "__main__":
    app.run(
        debug='true',
        port=5000,
        host='0.0.0.0'
    )
