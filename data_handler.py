import csv
from datetime import datetime
from operator import itemgetter
from psycopg2 import sql
from psycopg2._psycopg import cursor
from psycopg2.extras import RealDictCursor
import database_common

csv_question_headers = ['id','submission_time','view_number','vote_number','title','message', 'image']
csv_answer_headers = ['id','submission_time','vote_number', 'question_id','message','image']

question_table_headers = ['ID', 'Submission time', 'View number', 'Vote number', 'Title', 'Message', 'Image']


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
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.execute(sql, (new_question['id'], new_question['submission'], new_question['view'],
                         new_question['vote'], new_question['title'], new_question['message']))


@database_common.connection_handler
def write_answer_data(cursor: RealDictCursor, new_answer):
    sql = """
        INSERT INTO answer
        VALUES (%s, %s, %s, %s, %s);
    """
    cursor.execute(sql, (new_answer['id'], new_answer['submission'],
                         new_answer['vote'], new_answer['question_id'], new_answer['message']))


@database_common.connection_handler
def get_answers(cursor: RealDictCursor, id) -> list:
    query = """
        SELECT *
        FROM answer
        WHERE question_id=%(id)s"""
    cursor.execute(query, {'id': id})
    answer = cursor.fetchall()
    return answer


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
    sql = """
        DELETE FROM answer
        WHERE id = %(answer_id)s;
    """
    cursor.execute(sql, {'answer_id': answer_id})


@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id: int):
    query = """
        DELETE FROM answer
        WHERE question_id = %(question_id)s;
        DELETE FROM question
        WHERE id = %(question_id)s;"""

    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def search(cursor: RealDictCursor, input):
    query = """
        SELECT A.*
        FROM question A
        WHERE title ILIKE %(input)s OR message ILIKE %(input)s
        OR A.id IN (SELECT B.question_id from answer B WHERE message ILIKE %(input)s)
    """
    cursor.execute(query, {'input': '%' + input + '%'})
    vote_num_data = cursor.fetchall()
    return vote_num_data


@database_common.connection_handler
def update_question(cursor: RealDictCursor, title: str, message: str, question_id: int):
    query = """
        UPDATE question
        SET title = %(title)s, message = %(message)s
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'title': title, 'message': message, 'question_id': question_id})


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
def new_comment_for_question(cursor: RealDictCursor, question_id: int, message: str, submission_time: str):
    query = """
        INSERT INTO comment (question_id, message, submission_time)
        VALUES (%(question_id)s, %(message)s, %(submission_time)s);"""
    cursor.execute(query, {'question_id': question_id, 'message': message, 'submission_time': submission_time})


@database_common.connection_handler
def new_comment_for_answer(cursor: RealDictCursor, answer_id: int, message: str, submission_time: str):
    query = """
        INSERT INTO comment (answer_id, message, submission_time)
        VALUES (%(answer_id)s, %(message)s, %(submission_time)s);"""
    cursor.execute(query, {'answer_id': answer_id, 'message': message, 'submission_time': submission_time})


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
def delete_question_comments(cursor: RealDictCursor):
    pass
