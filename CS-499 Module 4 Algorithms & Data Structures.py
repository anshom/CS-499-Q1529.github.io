#Import libraries needed

import json
from bson import json_util
from pymongo import MongoClient
import os
import pprint
import sys
from datetime import datetime
import bottle
from bottle import route, run, request, abort,delete, get, post, put, template

#Create a link to localhost and database
connection = MongoClient('localhost', 27017)
db = connection['market']
collection = db['stocks']

#Create a document
@post('/createStock/<ticker>')
def post_createStock(ticker=None):
    '''
    HTTP POST method to create and Insert a new document into the MongoDB collection.
    This will require a <ticker> symbol in the URI and valid JSON format data.
    return results in JSON format.
    '''

    if ticker:
        query = {"Ticker" : ticker}

        if request.json:            
            query.update(request.json) #This combines ticker and JSON data together

            #Insert the document and read the result
            result = collection.insert_one(query)

            string = template("{ \"result\" : \"{{result}}\" }", result=result.acknowledged)
        else:
            abort(404, "Invalid arguments passed.Expected a JSON format data.")
    else:
        abort(404, "Invalid arguments passed. Expected a ticker symbol.")

    return json.loads(json.dumps(string, indent=4, default=json_util.default))

#Retrieves document from the collection using @get function 
@get('/getStock/<ticker>')
def getStock(ticker=None):
    '''
    HTTP GET method to retrieve document from collection using Ticker symbol.
    Requires <ticker> symbol in the URI.
    return results in JSON format.
    '''

    if ticker:
        query = collection.find_one({"Ticker" : ticker})

        if not query:
            abort(404, "No stock found with ticker symbol:".format(ticker))
    else:
        abort(404, "Invalid arguments passed. Expected a ticker symbol:")

    return json.dumps(query, indent=4, default=json_util.default)

#Update existing document in the collection using @update function
@put('/updateStock/<ticker>')
def updateStock(ticker):
    '''
    HTTP PUT method to update a document in collection using ticker symbol passed.
    Requires <ticker> symbol in the URI and a valid JSON format data.
    return results in JSON format.
    '''

    if ticker:
        entity = {"Ticker" : ticker}

        if request.json:
            update = {"$set" : request.json}

            result = collection.update_one(entity, update)
        else:
            abort(404, "Invalid arguments passed. Expected data in JSON format.")    
    else:
        abort(404, "Invalid arguments passed. Expected ticker symbol.")

    return result.raw_result

#Delete a document from the collection
@delete('/deleteStock/<ticker>')
def deleteStock(ticker):
    '''
    HTTP DELETE method to delete a document in MongoDB based on Ticker field.
    Requires <ticker> string value in URI.
    Returns result in JSON format.
    '''
    if ticker:  
        doc = {"Ticker" : ticker}

        result = collection.delete_one(doc)    
    else:
        abort(404, "Invalid arguments. Expected ticker name. No ticker argument provided.")

    return result.raw_result


#Retrieves the StockReport using get function
@get('/stockReport/<stocks>')
def get_stockReport(stocks=None):
    '''
    HTTP GET method to read a customized summary report for list of stocks in the collection.
    This requires <stocks> symbols in the URI.
    <stocks> symbols must be in square bracket and comma seperated:
    For example  [AAIT,AAMC,AA,AADR]
    Returns result in JSON format.    
    '''
    if stocks: 
        if "[" in stocks and "]" in stocks:
            stocks = stocks.replace("[", "").replace("]","")
            stocks = stocks.split(",")
        else:
            abort(404, "Invalid stock list format.Provide a comma seperated list in square brackets.")    
     
        pipeline = [
            {"$match" : {"Ticker" : {"$in" : ['AAIT','AAMC','AA','AADR']}}},
            {"$project" :{"_id":0,"Ticker":1,"Price":1,"Change":1,"Volume":1,"Market Cap":1, 
                "Change %":{"$multiply":[ {"$divide":["$Change",{"$subtract":["$Price","$Change"]}]},100]}
                }
            }
        ]

        entity = collection.aggregate(pipeline)

        if not entity:
            abort(404, "No documents returned for Ticker list: {}".format(stocks))
    else:
        abort(404, "Invalid stocks list format.Provide comma seperated list in square brackets.")

    return json.dumps(entity, indent=4, default=json_util.default)

#Get Industry Report of Stocks
@get('/industryReport/<industry>')
def industryReport(industry=None):
    '''
    HTTP GET method to retrieve a customized industry report for Industry name.
    This performs a full-text index search for the Industry name provided.
    requires <industry> name in the URI.<industry> can take any valid name, with spaces:
    For example; Test Industry Name,Exchange Traded Fund,Meat Products,Asset Management
    Returns results in JSON format.    
    '''
    if industry:
        pipeline = [
             {"$match" : {"$text" : {"$search" : "Asset Management"}}},
             {"$project" : {"_id" : 0, "Ticker" : 1, "Price" : 1}}, 
             {"$sort" : {"Price" : -1}}, 
             {"$limit" : 5}
        ]

        # Retrieve data from MongoDB collection for provided pipeline
        entity= collection.aggregate(pipeline)

        if not entity:
            abort(404, "No industry name found: {}".format(industry))

    else:
        abort(404, "Invalid arguments. Provide industry name.")

    return json.dumps(entity, indent=4, default=json_util.default)

#Return Industry Report of (top 5) stocks for chosen Industry
    return industry_report(industry)
      
def main():
    # Run the bottle application
  run(host='0.0.0.0', port=8080)

if __name__ == "__main__":    
    if len(sys.argv) >= 2:
        if sys.argv[1].lower() in ("--testmode", "-t"):
                test_mongo()                
        else:
            show_help()
        sys.exit()   

    main()

    
    
    










