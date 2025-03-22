import json
import datetime
from peewee import Model, CharField, TextField, SqliteDatabase

db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Market(BaseModel):
    name = CharField(unique=True)
    priceRanges = TextField(null=True)
    changesRange = TextField(null=True)
 
    def get_price_ranges(self):
        return json.loads(self.priceRanges) if self.priceRanges else []

    def set_price_ranges(self, value):
        self.priceRanges = json.dumps(value)

    def get_changes_range(self):
        return json.loads(self.changesRange) if self.changesRange else []

    def set_changes_range(self, value):
        self.changesRange = json.dumps(value)

def initialize_database ():
    db.connect()
    # Create a Bitcoin market explicitly
    db.create_tables([Market], safe=True)
    # Market.create(name ='bitcoin')
    # market = Market.get(Market.name == 'bitcoin')
    # market.get_price_ranges = []
    # market.get_changes_range = []
    # check = market.save()
    # print(check)



def clear_database():
    """ Clears database every 24 hours """
    print("🗑 Clearing database...")
    Market.delete().execute()

def close_database():
    db.close()

TRADE_HISTORY_FILE = "trade_history.json"

def load_trade_history():
    try:
        with open(TRADE_HISTORY_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_trade_history(trade_data):
    with open(TRADE_HISTORY_FILE, "w") as file:
        json.dump(trade_data, file, indent=4)

def record_trade(coin, action, price, reason):
    trade_data = load_trade_history()
    trade_data.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "coin": coin,
        "action": action,
        "price": price,
        "reason": reason
    })
    save_trade_history(trade_data)