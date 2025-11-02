# remove.py
from app import create_app
from models import db, Product

# Create app context so SQLAlchemy works
app = create_app()
with app.app_context():
    # Example: delete all products with missing images
    bad_products = Product.query.filter_by(image=None).all()

    if not bad_products:
        print("✅ No products found with missing images.")
    else:
        for p in bad_products:
            print(f"🗑️ Deleting: {p.name} (ID: {p.id})")
            db.session.delete(p)
        db.session.commit()
        print(f"✅ Deleted {len(bad_products)} product(s).")
