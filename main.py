from coinbase_websocket_client import CoinbaseWebsocketClient

if __name__ == "__main__":
    websocket_client = CoinbaseWebsocketClient()
    websocket_client.connect()
    websocket_client.close()
