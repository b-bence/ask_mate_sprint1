import csv
from datetime import datetime
from operator import itemgetter
csv_question_headers = ['id','submission_time','view_number','vote_number','title','message', 'image']
csv_answer_headers = ['id','submission_time','vote_number', 'question_id','message','image']

question_table_headers = ['ID', 'Submission time', 'View number', 'Vote number', 'Title', 'Message', 'Image']


def current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_questions_data(sort=False):
    with open('questions.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        lst = [x for x in csv_reader]
        if sort is True:
            for dict in lst:
                for key, value in dict.items():
                    if dict[key].isdigit() or key == 'vote_number':
                        dict[key] = int(dict[key])
    return lst


def get_answers_data():
    with open('answers.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        lst = [x for x in csv_reader]
    return lst


def generate_new_id(filename):
    max_id = 0
    with open(filename, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for i in csv_reader:
            if int(i['id']) >= max_id:
                max_id = int(i['id']) + 1
    return max_id


def write_new_data(lst, filename):
    with open(filename, 'a') as file:
        wr = csv.writer(file)
        wr.writerow(lst)


def get_answers(id):
    with open('answers.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        answers = [answer for answer in csv_reader if answer['question_id']==str(id)]
    return answers


def update_question_view_number(lst):
    with open('questions.csv', 'w') as new_file:
        fieldnames = csv_question_headers
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in lst:
            csv_writer.writerow(row)


def update_answer_view_number(lst):
    with open('answers.csv', 'w') as new_file:
        fieldnames = csv_answer_headers
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in lst:
            csv_writer.writerow(row)


def change_question_vote_count(id, num):
    dataset = get_questions_data()
    row_num = get_row(id, dataset)
    question_data = dataset[row_num]
    dataset[row_num]['vote_number'] = int(question_data['vote_number']) + num
    update_question_view_number(dataset)
    return dataset


def change_answer_vote_count(id, num):
    dataset = get_answers_data()
    row_num = get_row(id, dataset)
    answer_data = dataset[row_num]
    dataset[row_num]['vote_number'] = int(answer_data['vote_number']) + num
    update_answer_view_number(dataset)
    return dataset


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


def delete(item_id, is_question):
    answers = get_answers_data()
    id_type = 'id'
    if is_question is True:
        id_type = 'question_id'
        questions = get_questions_data()
        new_question_list = [row for row in questions if row['id'] != item_id]
        update_question_view_number(new_question_list)
    new_answer_list = [row for row in answers if row[id_type] != item_id]
    update_answer_view_number(new_answer_list)


