# -*- coding:utf8 -*-
# !/usr/bin/env python
# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

import random

from flask import Flask, request, make_response, jsonify
from GoogleSheet.read import get_show_rate, get_best_rate
from show_rate_responses import (
    NO_INPUT,
    NO_BANK,
    NO_LOAN_AMOUNT,
    NO_LOAN_PERIOD,
    ONLY_BANK,
    BEST_RATE_RESPONSE_ONLY_BANK,
    BEST_RATE_RESPONSE_ONLY_REPAYMENT,
    BEST_RATE_RESPONSE_ONLY_FIXEDYEAR,
    BEST_RATE_RESPONSE_NO_INPUT,
    BEST_RATE_RESPONSE_ALL_INPUT,
    BEST_RATE_RESPONSE_BANK_MORTGAGE,
    BEST_RATE_RESPONSE_BANK_FIXEDYEAR,
    BEST_RATE_RESPONSE_MORTGAGE_FIXEDYEAR
)

from util import random_response_best_bank

# Flask app should start in global layout
app = Flask(__name__)
log = app.logger


@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    try:
        intent = req.get('queryResult').get('intent').get('displayName')
    except AttributeError:
        return 'json error'

    print('Intent: ' + intent)
    if intent == 'showRate':
        res = show_rate(req)
    elif intent == 'description':
        res = description(req)
    elif intent == 'compareRate':
        res = compare_rate(req)
    elif intent == 'bestRate':
        res = best_rate(req)
    elif intent == 'rate-followup':
        res = rate_followup(req)
    else:
        # TODO: Fix the else statement for res with fallback intent?
        res = show_rate(req)

    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return make_response(jsonify({'fulfillmentText': res}))


def description(req):
    parameters = req['queryResult']['parameters']

    mortgage_type = parameters["Mortgage_types"]
    if mortgage_type == "IO":
        response = mortgage_type + " or Interest Only loan is a loan in which " \
                                   "the borrower pays only the interest for some or all of the " \
                                   "term, with the principal balance unchanged during the interest-only period."
    elif mortgage_type == "P&I":
        response = mortgage_type + " or Principal and Interest loan is a loan in which " \
                                   "the borrower pays the portioon of principal with " \
                                   "the interest in a certain period of time."
    elif mortgage_type == "LVR":
        response = mortgage_type + " or Loan to Value Ratio is calculated by dividing the loan amount " \
                                   "by the actual purchase price or valuation of the property, then" \
                                   " multiplying it by 100."
    else:
        response = "Sorry, I do not understand what you mean."
    return response


def get_parameters(req):
    return req['queryResult']['parameters']


def show_rate(req):
    # Parsing the POST request body into a dictionary for easy access.
    intent_name = req['queryResult']['intent']['displayName']
    parameters = get_parameters(req)
    print('Dialogflow Parameters:')
    print(json.dumps(parameters, indent=4))
    print("intent name:", intent_name)

    # if the name of the bank is not given, then tell
    # them that they need to include the name of the bank.

    # TODO: CHECK LOAN AMOUNT AND LOAN YEAR SHOULD BE NEARING THE END TO CHECK IF THE AMOUNT AND PERIOD IS VALID. #####

    # Accessing the fields on the POST request body of API.ai invocation of the webhook
    # loan_amount = parameters["loan_value"]
    # loan_year_period = parameters["loan_year_period"]
    bank_name = parameters['Australian_Banks']
    repayment_type = parameters['repayment_type']

    if bank_name == "" and repayment_type == "":
        response = random.choice(NO_INPUT)
    elif bank_name == "":
        response = random.choice(NO_BANK)
    elif repayment_type == "":
        output_string = random.choice(ONLY_BANK)
        response = output_string.format(
            bank_name=bank_name
        )
    else:
        response = get_show_rate(bank_name, repayment_type)
    return response


def compare_rate(req):
    # TODO: Get the request and show right response.
    response = "The comparison ..."
    return response


def best_rate(req):
    bank_name = None
    mortgage_type = None
    year_fixed = None

    parameters = get_parameters(req)

    bank_param = parameters['Australian_Banks']
    mortgage_param = parameters['Mortgage_types']
    fixed_year_param = parameters['fixed_year']

    if bank_param == "" and mortgage_param == "" and fixed_year_param == "":
        best_rate = get_best_rate(bank_name, mortgage_type, year_fixed)
        response = random_response_best_bank(BEST_RATE_RESPONSE_NO_INPUT, best_rate)
    elif bank_param != "" and mortgage_param != "" and fixed_year_param != "":
        best_rate = get_best_rate(bank_param, mortgage_param, fixed_year_param)
        response = random_response_best_bank(BEST_RATE_RESPONSE_ALL_INPUT, best_rate)
    elif bank_param != "" and mortgage_param != "":
        best_rate = get_best_rate(bank_param, mortgage_param, year_fixed)
        response = random_response_best_bank(BEST_RATE_RESPONSE_BANK_MORTGAGE, best_rate)
    elif bank_param != "" and fixed_year_param != "":
        best_rate = get_best_rate(bank_param, mortgage_type, fixed_year_param)
        response = random_response_best_bank(BEST_RATE_RESPONSE_BANK_FIXEDYEAR, best_rate)
    elif mortgage_param != "" and fixed_year_param != "":
        best_rate = get_best_rate(bank_name, mortgage_param, fixed_year_param)
        response = random_response_best_bank(BEST_RATE_RESPONSE_MORTGAGE_FIXEDYEAR, best_rate)
    elif bank_param != "":
        best_rate = get_best_rate(bank_param, mortgage_type, year_fixed)
        response = random_response_best_bank(BEST_RATE_RESPONSE_ONLY_BANK, best_rate)
    elif mortgage_param != "":
        best_rate = get_best_rate(bank_name, mortgage_param, year_fixed)
        response = random_response_best_bank(BEST_RATE_RESPONSE_ONLY_REPAYMENT, best_rate)
    elif fixed_year_param != "":
        best_rate = get_best_rate(bank_name, mortgage_type, fixed_year_param)
        response = random_response_best_bank(BEST_RATE_RESPONSE_ONLY_FIXEDYEAR, best_rate)
    else:
        best_rate = get_best_rate(bank_param, mortgage_param, fixed_year_param)
        response = random_response_best_bank(BEST_RATE_RESPONSE_ALL_INPUT, best_rate)

    return response


def rate_followup(req):
    parameters = get_parameters(req)
    bank_name = ""
    repayment_type = ""
    if parameters["Australian_Banks"] != "":
        bank_name = parameters["Australian_Banks"]

    if parameters["repayment_type"] != "":
        repayment_type = parameters["repayment_type"]

    response = get_show_rate(bank_name, repayment_type)
    return response


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0', threaded=True)
