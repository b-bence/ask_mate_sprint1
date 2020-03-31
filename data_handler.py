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

#
# def update_answer_view_number(lst):
#     with open('answers.csv', 'w') as new_file:
#         fieldnames = csv_answer_headers
#         csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
#         csv_writer.writeheader()
#         for row in lst:
#             csv_writer.writerow(row)


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


def get_row(id, lst):
    row_num = 0
    for index, row in enumerate(lst):
        if row['id'] == id:
            row_num = index
    return row_num


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


# def delete(item_id, is_question):
#     answers = get_answers_data()
#     id_type = 'id'
#     if is_question is True:
#         id_type = 'question_id'
#         questions = get_questions_data()
#         new_question_list = [row for row in questions if row['id'] != item_id]
#         update_question_view_number(new_question_list)
#     new_answer_list = [row for row in answers if row[id_type] != item_id]
#     update_answer_view_number(new_answer_list)

@database_common.connection_handler
def delete_question(cursor: RealDictCursor, question_id: int):
    query = """
        DELETE FROM answer
        WHERE question_id = %(question_id)s;
        DELETE FROM question
        WHERE id = %(question_id)s;"""

    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def update_question(cursor: RealDictCursor, title: str, message: str, question_id: int):
    query = """
        UPDATE question
        SET title = %(title)s, message = %(message)s
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'title': title, 'message': message, 'question_id': question_id})
