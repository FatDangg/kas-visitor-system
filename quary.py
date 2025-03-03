from app import app, db, Visitor

with app.app_context():
    visitors = Visitor.query.all()
    for visitor in visitors:
        print(visitor.name, visitor.id_number, visitor.reason, visitor.visit_date)
