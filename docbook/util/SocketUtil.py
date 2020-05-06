import requests


def notify_all(dbdoc_id):
    requests.post('http://localhost:9000' + "/", {}, {'id': dbdoc_id})


def notify(dbdoc_id, session_key, error):
    requests.post('http://localhost:9000' + "/", {}, {'id': dbdoc_id, 'session_key': session_key, 'error': error})
