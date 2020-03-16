import csv
question_headers = ['id','submission_time','view_number','vote_number','title','message', 'image']
answer_headers = ['id','submission_time','vote_number', 'question_id','message','image']

question_table_headers = ['ID', 'Submission time', 'View number', 'Vote number', 'Title', 'Message', 'Image']


def get_questions():
    with open('questions.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        lst = [x for x in csv_reader]
    return lst

