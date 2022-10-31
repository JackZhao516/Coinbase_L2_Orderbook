###running the following commands to set up and run the project
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 main.py
```
###### coinbase_websocket_client.py contains the  CoinbaseWebsocketClient class
###### orderbook.py contains the OrderBook class
###### main.py contains the main function
###### orderbook_unittest.py contains the unit tests for the OrderBook class and CoinbaseWebsocketClient class
###### *.json files are the test data inputs for the unit tests

Once running, the project will generate a log file called order_book.log in the same directory as the project. 
The log file will record the error messages.