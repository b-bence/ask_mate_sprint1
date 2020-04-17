import csv
import bcrypt
import os
from datetime import datetime
from operator import itemgetter
from psycopg2 import sql
from psycopg2._psycopg import cursor
from psycopg2.extras import RealDictCursor
import database_common

csv_question_headers = ['id','submission_time','view_number','vote_number','title','message', 'image']
csv_answer_headers = ['id','submission_time','vote_number', 'question_id','message','image']

question_table_headers = ['ID', 'Submission time', 'View number', 'Vote number', 'Title', 'Message', 'Image']


def hash_password(plain_text_password):
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def verify_password(plain_text_password, hashed_password):
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_bytes_password)


@database_common.connection_handler
def add_user(cursor: RealDictCursor, email, password, registration_date):
    sql = """
        INSERT INTO users(email, password, registration_date)
        VALUES (%s, %s, %s)
    """
    cursor.execute(sql, (email, password, registration_date))


@database_common.connection_handler
def get_user_data(cursor:RealDictCursor, email):
    sql = """
        SELECT * FROM users
        WHERE email = %(email)s
    """
    cursor.execute(sql,{'email':email})
    data = cursor.fetchall()
    return data


@database_common.connection_handler
def get_answer_data(cursor:RealDictCursor, email):
    sql = """
        SELECT * FROM answer
        WHERE email = %(email)s
    """
    cursor.execute(sql,{'email':email})
    data = cursor.fetchall()
    return data


def current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


@database_common.connection_handler
def get_questions_data(cursor: RealDictCursor, sort=False,) -> list:
    query = """
        SELECT *
        FROM question"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_single_question(cursor: RealDictCursor, id) -> list:
    query = """
        SELECT *
        FROM question
        WHERE id=%(id)s"""
    cursor.execute(query, {'id':id})
    [data] = cursor.fetchall()
    return data


@database_common.connection_handler
def get_single_answer(cursor: RealDictCursor, id) -> list:
    query = """
            SELECT *
            FROM answer
            WHERE id=%(id)s"""
    cursor.execute(query, {'id': id})
    [data] = cursor.fetchall()
    return data


@database_common.connection_handler
def get_answers_data(cursor: RealDictCursor) -> list:
    query = """
        SELECT *
        FROM answer"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_views(cursor: RealDictCursor, id):
    query = """
        SELECT view_number
        FROM question
        WHERE id=%(id)s"""
    cursor.execute(query, {'id': id})
    [view_num] = cursor.fetchall()
    return int(view_num['view_number'])


@database_common.connection_handler
def generate_new_id(cursor: RealDictCursor, filename):
    query = """SELECT MAX(id) FROM {}"""
    cursor.execute(sql.SQL(query).format(sql.Identifier(filename)))
    [max_value] = cursor.fetchall()
    return int(max_value['max']) + 1


@database_common.connection_handler
def write_question_data(cursor: RealDictCursor, new_question):
    sql = """
        INSERT INTO question
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(sql, (new_question['id'], new_question['submission'], new_question['view'],
                         new_question['vote'], new_question['title'], new_question['message'],
                         new_question['filename'], new_question['user_id']))


@database_common.connection_handler
def write_answer_data(cursor: RealDictCursor, new_answer):
    sql = """
        INSERT INTO answer
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(sql, (new_answer['id'], new_answer['submission'],new_answer['vote'], new_answer['question_id'],
                         new_answer['message'], new_answer['filename'], new_answer['user_id']))


@database_common.connection_handler
def get_answers(cursor: RealDictCursor, id) -> list:
    query = """
        SELECT 
	        users.email user_email, 
	        answer.*
        FROM users
        JOIN answer
        ON users.id = answer.user_id
        WHERE answer.question_id =%(id)s"""
    cursor.execute(query, {'id': id})
    answer = cursor.fetchall()
    return answer


@database_common.connection_handler
def get_answer_message(cursor: RealDictCursor, search_phrase) -> list:
    query = """
        SELECT message
        FROM answer
        WHERE message ILIKE %(search_phrase)s
    """
    cursor.execute(query, {'search_phrase': '%' + search_phrase + '%'})
    return cursor.fetchall()


@database_common.connection_handler
def update_question_view_number(cursor: RealDictCursor, num, id):
    sql = """
            UPDATE question
            SET view_number = %(num)s
            WHERE id = %(id)s
            ;

    """
    cursor.execute(sql, {'num': num, 'id': id})


@database_common.connection_handler
def get_answer_vote_count(cursor: RealDictCursor, id) -> list:
    query = """
        SELECT vote_number, question_id
        FROM answer
        WHERE id=%(id)s"""
    cursor.execute(query, {'id': id})
    [vote_num_data] = cursor.fetchall()
    return vote_num_data


@database_common.connection_handler
def update_answer_vote_number(cursor: RealDictCursor, num, id):
    sql = """
            UPDATE answer
            SET vote_number = %(num)s
            WHERE id = %(id)s
            ;

    """
    cursor.execute(sql, {'num': num, 'id': id})


@database_common.connection_handler
def get_question_vote_count(cursor: RealDictCursor, id):
    query = """
        SELECT vote_number
        FROM question
        WHERE id=%(id)s"""
    cursor.execute(query, {'id': id})
    [vote_num_data] = cursor.fetchall()
    return vote_num_data


@database_common.connection_handler
def update_question_vote_number(cursor: RealDictCursor, num, id):
    sql = """
            UPDATE question
            SET vote_number = %(num)s
            WHERE id = %(id)s
            ;

    """
    cursor.execute(sql, {'num': num, 'id': id})


def sort_by(header, direction):
    questions = get_questions_data(True)
    reverse = False
    if direction == 'desc':
        reverse = True
    return sorted(questions, key=itemgetter(header), reverse=reverse)


@database_common.connection_handler
def delete_answer(cursor: RealDictCursor, answer_id: int):
    filename_query = """
        SELECT image
        FROM answer
        WHERE id = %(answer_id)s"""

    sql = """
        DELETE FROM answer
        WHERE id = %(answer_id)s;
    """
    cursor.execute(filename_query, {'answer_id': answer_id})
    [temp_result] = cursor.fetchall()
    filename = temp_result['image']
    delete_image(filename)

    cursor.execute(sql, {'answer_id': answer_id})


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id: int):
    answers = get_answers(question_id)
    for answer in answers:
        filename = answer['image']
        delete_image(filename)
        delete_answer_comments(answer['id'])

    filename_query = """
        SELECT image
        FROM question
        WHERE id = %(question_id)s"""

    delete_query = """
        DELETE FROM comment
        WHERE question_id = %(question_id)s;
        DELETE FROM answer
        WHERE question_id = %(question_id)s;
        DELETE FROM question
        WHERE id = %(question_id)s;"""
    cursor.execute(filename_query, {'question_id': question_id})
    [temp_result] = cursor.fetchall()
    filename = temp_result['image']
    delete_image(filename)
    cursor.execute(delete_query, {'question_id': question_id})


@database_common.connection_handler
def search(cursor: RealDictCursor, input):
    query = """
        SELECT A.*
        FROM question A
        WHERE title ILIKE %(input)s OR message ILIKE %(input)s
        OR A.id IN (SELECT B.question_id from answer B WHERE message ILIKE %(input)s)
    """
    cursor.execute(query, {'input': '%' + input + '%'})
    search_data = cursor.fetchall()
    return search_data


@database_common.connection_handler
def fancy_search(cursor: RealDictCursor, input):
    query = """
        SELECT message, question_id
        FROM answer
        WHERE message ILIKE %(input)s
        AND %(input)s NOT IN(SELECT title FROM question) AND %(input)s NOT IN(SELECT message FROM question)
    """
    cursor.execute(query, {'input':'%' + input + '%'})
    search_data = cursor.fetchall()
    return search_data


@database_common.connection_handler
def update_question(cursor: RealDictCursor, title: str, message: str, question_id: int, image: str):
    query = """
        UPDATE question
        SET title = %(title)s, message = %(message)s, image = %(image)s
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'title': title, 'message': message, 'question_id': question_id, 'image': image})


@database_common.connection_handler
def update_answer(cursor: RealDictCursor, id: int, message: str):
    query = """
        UPDATE answer
        SET message = %(message)s
        WHERE id = %(id)s
    """
    cursor.execute(query, {'id':id, 'message': message})


@database_common.connection_handler
def get_all_tags(cursor: RealDictCursor):
    query = """
        SELECT * FROM tag
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_tag_id(cursor: RealDictCursor, name):
    query = """
        SELECT id 
        FROM tag
        WHERE name = %(name)s
    """
    cursor.execute(query, {'name': name})
    [tag_id] = cursor.fetchall()
    return tag_id['id']


@database_common.connection_handler
def get_question_tags(cursor: RealDictCursor, id) ->list:
    query = """
        SELECT A.*
        FROM tag A
        WHERE A.id IN (SELECT B.tag_id from question_tag B WHERE B.question_id = %(input)s)
    """
    cursor.execute(query, {'input':id})
    return cursor.fetchall()


@database_common.connection_handler
def get_max_tag_id(cursor: RealDictCursor):
    query = """
        SELECT MAX(id)
        FROM tag
    """
    cursor.execute(query)
    [max_value] = cursor.fetchall()
    return max_value['max']


@database_common.connection_handler
def add_new_tag_to_list(cursor: RealDictCursor, id, name):
    query="""
        INSERT INTO tag
        VALUES (%(id)s, %(name)s)
    """
    cursor.execute(query, {'id': id, 'name': name})


@database_common.connection_handler
def add_tag_to_question(cursor: RealDictCursor, question_id, tag_id):
    query="""
        INSERT INTO question_tag
        VALUES (%(question_id)s, %(tag_id)s)
    """
    try:
        cursor.execute(query, {'question_id': question_id, 'tag_id': tag_id})
    except:
        pass


@database_common.connection_handler
def new_comment_for_question(cursor: RealDictCursor, question_id: int, message: str, submission_time: str, user_id: int):
    query = """
        INSERT INTO comment (question_id, message, submission_time, user_id)
        VALUES (%(question_id)s, %(message)s, %(submission_time)s, %(user_id)s);"""
    cursor.execute(query, {'question_id': question_id, 'message': message, 'submission_time': submission_time, 'user_id': user_id})


@database_common.connection_handler
def new_comment_for_answer(cursor: RealDictCursor, answer_id: int, message: str, submission_time: str, user_id: int):
    query = """
        INSERT INTO comment (answer_id, message, submission_time, user_id)
        VALUES (%(answer_id)s, %(message)s, %(submission_time)s, %(user_id)s);"""
    cursor.execute(query, {'answer_id': answer_id, 'message': message, 'submission_time': submission_time, 'user_id': user_id})


@database_common.connection_handler
def get_question_id_by_answer(cursor: RealDictCursor, answer_id: int):
    query = """
        SELECT question_id
        FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})
    [data] = cursor.fetchall()
    return data['question_id']


@database_common.connection_handler
def delete_tag(cursor: RealDictCursor, question_id, tag_id):
    query = """
        DELETE FROM question_tag
        WHERE question_id = %(question_id)s
        AND tag_id = %(tag_id)s
    """
    cursor.execute(query, {'question_id': question_id, 'tag_id': tag_id})


@database_common.connection_handler
def get_comments(cursor: RealDictCursor) -> list:
    query = """
        SELECT *
        FROM comment
        ORDER BY submission_time"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def delete_answer_comments(cursor: RealDictCursor, answer_id: int):
    query = """
        DELETE FROM comment
        WHERE answer_id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})


@database_common.connection_handler
def get_comment_by_id(cursor: RealDictCursor, comment_id: int):
    query = """
        SELECT *
        FROM comment
        WHERE id = %(comment_id)s;"""
    cursor.execute(query, {'comment_id': comment_id})
    [data] = cursor.fetchall()
    return data


@database_common.connection_handler
def delete_comment_by_id(cursor: RealDictCursor, comment_id: int):
    query = """
            DELETE FROM comment
            WHERE id = %(comment_id)s"""
    cursor.execute(query, {'comment_id': comment_id})


@database_common.connection_handler
def update_comment_by_id(cursor: RealDictCursor, comment_id: int, message: str, edited_count: int):
    query = """
        UPDATE comment
        SET message = %(message)s, edited_count = %(edited_count)s
        WHERE id = %(comment_id)s"""
    cursor.execute(query, {'message': message, 'edited_count': edited_count, 'comment_id': comment_id})


@database_common.connection_handler
def get_question_id_by_comment(cursor: RealDictCursor, comment_id):
    query = """
        SELECT question_id
        FROM comment
        WHERE id = %(comment_id)s;"""
    cursor.execute(query, {'comment_id': comment_id})
    [data] = cursor.fetchall()
    question_id = data['question_id']
    if question_id is None:
        sec_query = """
            SELECT answer_id
            FROM comment
            WHERE id = %(comment_id)s;"""
        cursor.execute(sec_query, {'comment_id': comment_id})
        [sec_data] = cursor.fetchall()
        answer_id = sec_data['answer_id']
        question_id = get_question_id_by_answer(answer_id)
    return question_id


@database_common.connection_handler
def get_latest_questions(cursor: RealDictCursor) -> list:
    query = """
        SELECT *
        FROM question
        ORDER BY submission_time DESC
        LIMIT 5;"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def approve(cursor: RealDictCursor, id: int):
    query = """
        UPDATE answer
        SET accepted = TRUE 
        WHERE id= %(id)s
    """
    cursor.execute(query, {'id': id})


@database_common.connection_handler
def get_question_user_id(cursor: RealDictCursor, question_id: int):
    query = """
        SELECT user_id
        FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    [result] = cursor.fetchall()
    return result['user_id']


@database_common.connection_handler
def get_answer_user_id(cursor: RealDictCursor, answer_id: int):
    query = """
        SELECT user_id
        FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})
    [result] = cursor.fetchall()
    return result['user_id']


@database_common.connection_handler
def update_reputation(cursor: RealDictCursor, gained_points: int, user_id: int):
    query = """
        UPDATE users
        SET reputation = reputation + %(gained_points)s
        WHERE id = %(user_id)s"""
    cursor.execute(query, {'gained_points': gained_points, 'user_id': user_id})


@database_common.connection_handler
def get_user_page_data(cursor: RealDictCursor, user_id: int) -> list:
    pass


@database_common.connection_handler
def tag_occurence(cursor: RealDictCursor):
    query = """
        SELECT 
            tag.name as tag_name,
            COUNT(question_tag.question_id) as occurence
        FROM tag
        JOIN question_tag
        ON tag.id = question_tag.tag_id
        GROUP BY tag_name;
    """
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def list_user_data(cursor:RealDictCursor, user_id=False):
    query = """
        SELECT 
            users.id,
            users.email,
            users.registration_date,
            COUNT(question.id) as asked_questions,
            COUNT(distinct answer.id) as answer,
	        COUNT(distinct comment.id) as comment,
            users.reputation
        FROM users
        LEFT JOIN question
            ON users.id = question.user_id
        LEFT JOIN answer
            ON users.id = answer.user_id
        LEFT JOIN comment
            ON users.id = comment.user_id"""
    if user_id:
        query += f"""
            WHERE users.id={user_id}"""
    query += """
        GROUP BY users.id;"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_user_activities(cursor:RealDictCursor, user_id: int) -> list:
    id = {'user_id': user_id}
    question_query = """
        SELECT title AS question, id AS question_id
        FROM question
        WHERE question.user_id = %(user_id)s"""
    answer_query = """
        SELECT message AS answer, question_id
        FROM answer
        WHERE answer.user_id = %(user_id)s"""
    comment_query = """
        SELECT message AS comment,
        CASE
            WHEN question_id IS NULL THEN
                (SELECT question_id
                FROM answer
                WHERE id = comment.answer_id)
            WHEN answer_id IS NULL THEN question_id
        END AS question_id
        FROM comment
        WHERE comment.user_id = %(user_id)s"""
    cursor.execute(question_query, id)
    question = cursor.fetchall()
    cursor.execute(answer_query, id)
    answer = cursor.fetchall()
    cursor.execute(comment_query, id)
    comment = cursor.fetchall()
    return question, answer, comment


@database_common.connection_handler
def get_emails(cursor:RealDictCursor):
    query = """
        SELECT users.email
        FROM users;
    """
    cursor.execute(query)
    return cursor.fetchall()


def delete_image(filename):
    path = f'static/{filename}'
    if os.path.exists(path):
        os.remove(path)
