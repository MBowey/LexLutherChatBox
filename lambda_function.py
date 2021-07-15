import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from newsapi import NewsApiClient
from datetime import datetime
from dateutil.relativedelta import relativedelta
from botocore.vendored import requests

import nltk as nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.data.path.append("/tmp")

nltk.download("vader_lexicon", download_dir = "/tmp")

analyzer = SentimentIntensityAnalyzer()

### Insert NewsAPI Key ###
api_key = " "
newsapi = NewsApiClient(api_key=api_key)

### Functionality Helper Functions ###
def parse_float(n):
    """
    Securely converts a non-numeric value to float.
    """
    try:
        return float(n)
    except ValueError:
        return float("nan")



### Data Validation ###
def build_validation_result(is_valid, violated_slot, message_content):
    """
    Defines an internal validation message structured as a python dictionary.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


def validate_data(intent_request):
    """
    Validates the data provided by the user.
    """

    # A True results is returned if age or amount are valid
    return build_validation_result(True, None, None)


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response



### Investment Update Request ###
def get_updates(intent_request):

    """
    Performs dialog management and fulfillment for investment update.
    """

    # Gets slots' values
    investment = get_slots(intent_request)["investment"]
    updates = get_slots(intent_request)["updates"]

    # Gets the invocation source, for Lex dialogs "DialogCodeHook" is expected.
    source = intent_request["invocationSource"]  #

    if source == "DialogCodeHook":
        # This code performs basic validation on the supplied input slots.

        # Gets all the slots
        slots = get_slots(intent_request)

        # Validates user's input using the validate_data function
            
        validation_result = validate_data(intent_request)

        # If the data provided by the user is not valid,
        # the elicitSlot dialog action is used to re-prompt for the first violation detected.
        
        if not validation_result["isValid"]:
            slots[validation_result["violatedSlot"]] = None  # Cleans invalid slot

            # Returns an elicitSlot dialog to request new data for the invalid slot
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )

        # Fetch current session attributes
        output_session_attributes = intent_request["sessionAttributes"]

        # Once all slots are valid, a delegate dialog is returned to Lex to choose the next course of action.
        return delegate(output_session_attributes, get_slots(intent_request))

    
    # Get the investment articles and sentiment analysis
    
    top_articles = newsapi.get_everything(q=investment, language="en", page_size=50, sort_by="relevancy")
    
    sentiments = []
    
    for article in top_articles['articles']:
        try:
            title = article["title"]
            text = article["content"]
            date = article["publishedAt"][:5]
            sentiment = analyzer.polarity_scores(text)
            compound = sentiment["compound"]
            pos = sentiment["pos"]
            neu = sentiment["neu"]
            neg = sentiment["neg"]

            sentiments.append({
                "title": title,
                "text": text,
                "date": date,
                "compound": compound,
                "positive": pos,
                "negative": neg,
                "neutral": neu

            })
        except AttributeError:
            pass
    
    sentiment_df = pd.DataFrame(sentiments)
    columns = ["date", "title", "text", "compound", "positive", "negative", "neutral"]
    sentiment_df = sentiment_df[columns]
    sentiment_df = sentiment_df.set_index(sentiment_df['date']).drop('date',1)
    sentiment_df = sentiment_df.sort_values(by="date", ascending=False)
    
    
    # Returns a message with the top 5 headlines for investment selected
    if updates == "headlines":
        
        headline_1 = sentiment_df['title'][0]
        headline_2 = sentiment_df['title'][1]
        headline_3 = sentiment_df['title'][2]
        headline_4 = sentiment_df['title'][3]
        headline_5 = sentiment_df['title'][4]
    
        update_message = """Here are the top headlines;
            for {}: ;
            1) {} ;
            2) {} ;
            3) {} ;
            4) {} ;
            5) {} 
            
            """.format(
                investment,
                headline_1,
                headline_2,
                headline_3,
                headline_4,
                headline_5
            )
    

    # Fetches the current price of crypto assets and returns a message
    elif updates == "data":
        
        
        url = ""
        id = ""
        if investment == "Bitcoin":
            url = "https://api.alternative.me/v2/ticker/Bitcoin/?convert=USD"
            id = "1"
        
            response = requests.get(url)
            response_json = response.json()
            price_usd = parse_float(response_json["data"][id]["quotes"]["USD"]["price"])
            
            
            update_message = """The current price of {} is ${:,.2f}
            
            """.format(
                investment, 
                price_usd
                
            )
        
        elif investment == "Ethereum":
            url = "https://api.alternative.me/v2/ticker/Ethereum/?convert=USD"
            id = "1027"
        
            response = requests.get(url)
            response_json = response.json()
            price_usd = parse_float(response_json["data"][id]["quotes"]["USD"]["price"])
            
            update_message = """The current price of {} is ${:,.2f}
            
            """.format(
                investment, 
                price_usd
                
            )
        
        elif investment == "Ripple":
        
            url = "https://api.alternative.me/v2/ticker/Ripple/?convert=USD"
            id = "52"

            response = requests.get(url)
            response_json = response.json()
            price_usd = parse_float(response_json["data"][id]["quotes"]["USD"]["price"])
            
            update_message = """The current price of {} is ${:,.2f}
            
            """.format(
                investment, 
                price_usd
                
            )
        
        else:
            
            update_message = """Sorry, {} data is currently not available. 
                            Data is currently only available for crypto.
            
            """.format(
                investment 
                
                
            )
        
        
        
    # Evaluates the sentiment of last 5 articles and returns a message
    elif updates == "sentiment":
        
        avg_sentiment = sentiment_df['compound'][0:5].mean()

        if avg_sentiment < -0.05:
            latest_sentiment = "NEGATIVE"
    
        elif avg_sentiment > 0.05:
            latest_sentiment = "POSITIVE"
    
        else:
            latest_sentiment = "NEUTRAL"
      
       
        update_message = """{} currently has a {} sentiment and an average vader 
            compound score of {:,.2f} based on the last 5 articles.
            
            """.format(
                investment,
                latest_sentiment,
                avg_sentiment
            )
    
    
    # Future placeholder for Machine Learning that returns a message with price/data trend
    else:
        
        investment_trend = "UPWARDS"
        Accuracy = "95%"
        
        
        update_message = """The current market trend for {} is "{}"
            
            """.format(
                investment, 
                investment_trend
                
            )
    
    
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": update_message
            
        },
    )
    
  



### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    # Get the name of the current intent
    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "PortfolioHeadlines":
        return get_updates(intent_request)
        
    

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)