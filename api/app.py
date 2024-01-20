import requests
from bs4 import BeautifulSoup

from flask import Flask, redirect, render_template, request, jsonify
import requests
from datetime import datetime

api_url = 'https://app.ylytic.com/ylytic/test'

response = requests.get(api_url, verify=False)

if response.status_code == 200:
    api_data = response.json()
    comments = api_data['comments']
else:
    print(f"Error: {response.status_code}")

app = Flask(__name__)


def returnNonNoneFilters(filters):
    new_dict = {}
    keys = list(filters.keys())
    values = list(filters.values())

    for i in range(len(values)):
        if values[i]['value'] is not None and values[i]['value'] != '':
            new_dict[keys[i]] = values[i]
    return new_dict


def filter_comments(comment, filters):
    all_conditions_met = True

    for key, value in filters.items():
        if key == 'search_text' and 'value' in value:
            if value['value'].lower() not in comment['text'].lower():
                all_conditions_met = False
                break
        elif key == 'search_author' and 'value' in value:
            if comment['author'].lower() != value['value'].lower():
                all_conditions_met = False
                break
        elif key == 'like_from' and 'value' in value:
            if comment['like'] < int(value['value']):
                all_conditions_met = False
                break
        elif key == 'like_to' and 'value' in value:
            if comment['like'] > int(value['value']):
                all_conditions_met = False
                break
        elif key == 'reply_from' and 'value' in value:
            if comment['reply'] < int(value['value']):
                all_conditions_met = False
                break
        elif key == 'reply_to' and 'value' in value:
            if comment['reply'] > int(value['value']):
                all_conditions_met = False
                break
        elif key == 'at_from' and 'value' in value:
            if datetime.strptime(comment['at'], '%a, %d %b %Y %H:%M:%S %Z') < datetime.strptime(value['value'], '%Y-%m-%d'):
                all_conditions_met = False
                break
        elif key == 'at_to' and 'value' in value:
            if datetime.strptime(comment['at'], '%a, %d %b %Y %H:%M:%S %Z') > datetime.strptime(value['value'], '%Y-%m-%d'):
                all_conditions_met = False
                break

    return all_conditions_met


@app.route('/', methods=['GET'])
def index():
    url = request.args.get('url')
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            hidden_cost_keywords = ['subscription', 'fee', 'charge', 'cost', 'billing']

            for keyword in hidden_cost_keywords:
                if soup.find(text=lambda text: text and keyword.lower() in text.lower()):
                    return f"Potential hidden cost found: '{keyword}'"

        except requests.RequestException as e:
            return f"Error fetching the website: {e}"



if __name__ == "__main__":
    app.run(debug=True)
