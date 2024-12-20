import json
import requests

class Database:
    data: dict[str, dict[str, dict[str, float]]]
    crypto_values: dict[str, float]

    def __init__(self):
        self.data = self.load_data()
        self.crypto_values = self.load_values()
    
    def load_data(self):
        try:
            with open("crypto_portfolios.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("Portfolio file not found, starting fresh.")
            return {}
        except json.JSONDecodeError:
            print("Error decoding portfolio file, starting fresh.")
            return {}

    def save_portfolios(self):
        try:
            with open("crypto_portfolios.json", "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving stats: {e}")
    
    def load_values(self):
        # Get the list of unique cryptocurrency symbols from all portfolios
        crypto_ids = set("bitcoin")
        for user_portfolio in self.data.values():
            crypto_ids.update(user_portfolio.keys())

        ids = ','.join(crypto_ids)

        if not ids:
            return {}

        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": ids,
            "vs_currencies": "usd",
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            j = response.json()
            res = {}
            for currency, values in j.items():
                res[currency] = values['usd']
            return res
        except requests.exceptions.RequestException as e:
            print(f"Error fetching cryptocurrency prices: {e}")
            return {}
    
    def register(self, author_id: int) -> None:
        self.data[str(author_id)] = {}
    
    def delete(self, author_id: int) -> None:
        self.data.pop(str(author_id))

    def is_registered(self, author_id: int) -> bool:
        return str(author_id) in self.data.keys()

    def get_portfolio(self, author_id: int) -> dict[str, dict[str, float]]:
        return self.data.get(str(author_id), {})

    def add_cryptocurrency(self, author_id: int, currency: str, amount: float) -> bool:
        c_low = currency.lower()
        if c_low in self.crypto_values.keys():
            self.data[str(author_id)][c_low] = {
                "amount": amount
            }
            return True

        # Fetch the price of the cryptocurrency in real-time from the CoinGecko API
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={c_low}&vs_currencies=usd"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # Check if the currency exists in the API response
            if c_low not in data:
                return False

            self.crypto_values[c_low] = data[c_low]["usd"]

            self.data[str(author_id)][c_low] = {
                "amount": amount,
            }
            return True
        except requests.exceptions.RequestException as e:
            return False
    
    def remove_cryptocurrency(self, author_id: int, currency: str) -> None:
        self.data[str(author_id)].pop(currency, None)
    
    def update_coins(self, author_id: int, currency: str, coins: float) -> None:
        self.data[str(author_id)][currency] = coins

    def get_portfolio_summary(self, author_id: int) -> tuple[str, float]:
        portfolio = self.get_portfolio(author_id)
        if not portfolio:
            return ("Your portfolio is empty.", 0.0)
        
        total_value: float = 0.0
        self.load_values()
        
        summary = ""
        for currency, stats in portfolio.items():
            curr_val = self.crypto_values.get(currency, 0)
            current_value = stats['amount'] * curr_val
            total_value += current_value
            summary += (
                f"**{currency.upper()}**:\n"
                f"1 Amount: {stats['amount']:.4f}\n"
                f"2 Current Coin Value: ${curr_val:.4f}\n"
                f"3 Current Value: ${current_value:.2f}\n\n"
            )
        return (summary, total_value)