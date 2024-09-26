from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ItemPrice(db.Model):
    __tablename__ = 'item_prices'
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sale_price = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<ItemPrice {self.item_name} {self.date} {self.sale_price}>"
