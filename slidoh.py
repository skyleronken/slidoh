import argparse
import logging
import sys

import requests

logger = logging.getLogger(__name__)


def get_event_ids(event_code):
    url = f'https://app2.sli.do/api/v0.5/events?code={event_code}'
    re = requests.get(url)
    d = re.json()[0]
    return d['uuid'], d['event_id']


def authenticate(event_uuid):
    url = f'https://app2.sli.do/api/v0.5/events/{event_uuid}/auth'
    re = requests.post(url, json={})
    #logger.info(f'{re.status_code}, {re.text}')
    token = re.json()['access_token']
    return f'Bearer {token}'

def get_questions(event_id, event_uuid):
    url = f'https://app2.sli.do/api/v0.5/events/{event_uuid}/questions/'
    auth = authenticate(event_uuid)
    re = requests.get(url, headers={
        'Authorization': auth,
    })
    question_results = []
    parsed_questions = re.json()
    for question in parsed_questions:
        q = {}
        if len(question['author']) > 0:
            q['author'] = question['author']['name']
            q['author_id'] = question['author']['event_user_id']
            q['author_device'] = question['author']['attrs']['attrs']['initialAppViewer']
        else:
            q['author'] = "Anonymous"
            q['author_id'] = 0
            q['author_device'] = "Unknown"
        q['text'] = question['text']
        q['score'] = question['score']
        q['id'] = question['event_question_id']
        question_results.append(q)

    return question_results

def vote(event_id, question_id, event_uuid):
    url = f'https://app2.sli.do/api/v0.5/events/{event_id}/questions/{question_id}/like'
    auth = authenticate(event_uuid)
    re = requests.post(url, json={
        'score': 1
    }, headers={
        'Authorization': auth,
    })
    #logger.info(f'{re.status_code}, {re.text}')
    return re.json()['event_question_score']


def main():
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('event_code', type=str)
    args = parser.parse_args()
    event_uuid, event_id = get_event_ids(args.event_code)
    questions = get_questions(event_id, event_uuid)
    for i in range(len(questions)):
        cur_q = questions[i]
        print("[{}] ({}) {} ({} {}) - {}".format(i, cur_q['score'], cur_q['author'], cur_q['author_id'], cur_q['author_device'], cur_q['text']))

    q_i = int(input("Input question number:"))

    question_id = questions[q_i]['id']

    n_v = int(input("Input number of votes to add:"))

    print(n_v)
        
    for i in range(n_v):
        print(f'vote #{i}')
        vote(event_id, question_id, event_uuid)


if __name__ == '__main__':
    main()