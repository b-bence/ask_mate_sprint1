import csv
from datetime import datetime
from operator import itemgetter
csv_question_headers = ['id','submission_time','view_number','vote_number','title','message', 'image']
csv_answer_headers = ['id','submission_time','vote_number', 'question_id','message','image']

question_table_headers = ['ID', 'Submission time', 'View number', 'Vote number', 'Title', 'Message', 'Image']


def current_time():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_questions():
    with open('questions.csv', 'r') as csv_file:
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


def update_view_number(lst):
    with open('questions.csv', 'w') as new_file:
        fieldnames = csv_question_headers
        csv_writer = csv.DictWriter(new_file, fieldnames=fieldnames)
        csv_writer.writeheader()
        for row in lst:
            csv_writer.writerow(row)


def sort_by(questions, header, direction):
    reverse = False
    if direction == 'desc':
        reverse = True
    return sorted(questions, key=itemgetter(header), reverse=reverse)
