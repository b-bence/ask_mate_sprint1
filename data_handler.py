import csv
csv_question_headers = ['id','submission_time','view_number','vote_number','title','message', 'image']
csv_answer_headers = ['id','submission_time','vote_number', 'question_id','message','image']

question_table_headers = ['ID', 'Submission time', 'View number', 'Vote number', 'Title', 'Message', 'Image']


def get_questions():
    with open('questions.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        lst = [x for x in csv_reader]
    return lst


def generate_question_id():
    max_id = 0
    with open('questions.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for i in csv_reader:
            if int(i['id']) >= max_id:
                max_id = int(i['id']) + 1
    return max_id


def write_question_data(lst):
    with open('questions.csv', 'a') as file:
        wr = csv.writer(file)
        wr.writerow(lst)


def get_answers():
    with open('answers.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        lst = [x for x in csv_reader]
    return lst


