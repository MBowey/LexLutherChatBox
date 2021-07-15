# Project 2 - Lex Luther Chat Box

# Team 4
##### 
---

## Intro 
The main focus of this project was to create an automated chat box that returned the top headlines, price data & sentiment analysis for various asset classes. We wanted to create a tool that would provide a quick and efficient update for its user. 



## Data Preperation & Amazon Lex
We used various different API's to pull in all this our data. We mainly used Alpaca & Quandl APIs for our equities, and other metrics. We pulled our Econnomic data from FRED using QUANDL's python API.
 * We gave the user a selection of investment and economic data to choose from:
    1. Equities
    2. Fixed Income
    3. Cryptocurrencies
    4. Commodities
    5. Foreign Exchange
    6. Economic Data

![InvestmentPrompt](Images/InvestmentPrompt.png)

## Natural Language Processing: VADER Sentiment
In a data-driven world, sentinment analysis is extremly useful as it allows a wider public opinion about certain topics. Sentiment analysis is the process of computing and categorizing textx into their respective polarity: postitive, negative or neutral.
A VADER sentiment analysis was a great way for our team to analyize the content of our data, it is:
* Speed-performance advantage
* Less resource-consuming model
* No need for training data
* Only a few lines of code
* F1-Score of 0.96* 

![SentimentAnalysis](Images/SentimentAnalysis.png)

_*https://blog.quantinsti.com/vader-sentiment/_ 


## AWS Lambda: Intent Handler & NLP Model
* Build
* Define
* Import
* Evaluate
* Return

![Slots](Images/Slots.png)


## Final Conclusions & Challenges

* Additional library dependencies required
    * AWS Lambda Layers 
    * Cloud 9
* AWS Lambda Layers has a capacity limit of  250 MB
* Testing functions in AWS is inefficient

![LambdaLayer](Images/LambdaLayer.png)


## Next Steps
* Import more libraries with AWS S3 
* Connect chat box to Slack, Twilio, Facebook, URL Website
* Add machine learning price/trend prediction




