import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from PIL import Image
from config import Config
from models import db, Product, BlogPost, SiteContent
from flask_mail import Mail, Message
from datetime import timedelta
from functools import wraps

# -------------------------
# Allowed extensions
# -------------------------
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


# -------------------------
# Admin security decorator (moved outside create_app)
# -------------------------
def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if session.get('admin_logged'):
            return fn(*a, **kw)
        flash('You must log in as admin to access that page.', 'warning')
        return redirect(url_for('admin_login'))
    return wrapper


# -------------------------
# Flask app factory
# -------------------------
def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    mail = Mail(app)

    # Session lifetime
    app.permanent_session_lifetime = timedelta(seconds=app.config['PERMANENT_SESSION_LIFETIME'])

    # Initialize database and default content
    with app.app_context():
        db.create_all()
        if not SiteContent.query.filter_by(key='about').first():
            c = SiteContent(
                key='about',
                value='Royal Radiance — handcrafted candles to light your moments. Edit this in admin.'
            )
            db.session.add(c)
            db.session.commit()

        if not SiteContent.query.filter_by(key='special_offer').first():
            db.session.add(
                SiteContent(key='special_offer', value='Limited-time: Golden Autumn collection — 20% off!')
            )
            db.session.commit()

    # -------------------------
    # Public routes
    # -------------------------
    @app.route('/')
    def home():
        products = Product.query.order_by(Product.created_at.desc()).limit(6).all()
        special = SiteContent.query.filter_by(key='special_offer').first()
        return render_template('home.html', products=products, special=special.value if special else '')

    @app.route('/about')
    def about():
        about = SiteContent.query.filter_by(key='about').first()
        return render_template('about.html', about_text=about.value if about else '')

    @app.route('/catalog')
    def catalog():
        products = Product.query.order_by(Product.created_at.desc()).all()
        return render_template('catalog.html', products=products)

    @app.route('/product/<int:pid>')
    def product_api(pid):
        p = Product.query.get_or_404(pid)
        return jsonify({'id': p.id, 'name': p.name, 'desc': p.short_desc, 'price': p.price, 'image': p.image})

    @app.route('/blog')
    def blog():
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        return render_template('blog.html', posts=posts)

    @app.route('/blog/<int:bid>')
    def blog_post(bid):
        post = BlogPost.query.get_or_404(bid)
        return render_template('blog_post.html', post=post)

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            msg = request.form.get('message')
            try:
                message = Message(
                    f'Royal Radiance contact from {name}',
                    recipients=[app.config.get('MAIL_DEFAULT_SENDER')]
                )
                message.body = f'From: {name} \nEmail: <{email}>\n\n{msg}'
                mail.send(message)
                flash('Message sent — we will contact you soon', 'success')
            except Exception as ex:
                print('Mail error:', ex)
                flash('Could not send message - please try again or contact via social links', 'warning')
            return redirect(url_for('contact'))
        return render_template('contact.html')

    @app.route('/uploads/<path:filename>')
    def uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    # -------------------------
    # Admin routes
    # -------------------------
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            pwd = request.form.get('password', '')
            stored_hash = app.config.get('ADMIN_PASSWORD_HASH')

        # Debug prints — to see if everything loads correctly
            print("Loaded hash from config:", stored_hash)
            print("Entered password:", pwd)

            try:
                is_valid = check_password_hash(stored_hash, pwd)
            except Exception as e:
                print("Hash check error:", e)
                is_valid = False

            print("Password match result:", is_valid)

            if is_valid:
                session['admin_logged'] = True
                session.permanent = True
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Wrong password', 'danger')

        return render_template('admin_login.html')


    @app.route('/admin/logout')
    def admin_logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('home'))

    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        products = Product.query.count()
        blogs = BlogPost.query.count()
        return render_template('admin_dashboard.html', products=products, blogs=blogs)

    @app.route('/admin/products', methods=['GET', 'POST'])
    @admin_required
    def admin_products():
        if request.method == 'POST':
            name = request.form.get('name')
            desc = request.form.get('short_desc')
            price = float(request.form.get('price') or 0)
            img = request.files.get('image')
            filename = None
            if img and allowed_file(img.filename):
                fname = secure_filename(img.filename)
                filename = f"prod_{int(os.times().system * 1000)}_{fname}"
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                img.save(path)
                try:
                    im = Image.open(path)
                    im.thumbnail((1200, 1200))
                    im.save(path, optimize=True, quality=85)
                except Exception as ex:
                    print('resize fail', ex)
            p = Product(name=name, short_desc=desc, price=price, image=filename)
            db.session.add(p)
            db.session.commit()
            flash('Product added', 'success')
            return redirect(url_for('admin_products'))

        prods = Product.query.order_by(Product.created_at.desc()).all()
        return render_template('admin_products.html', products=prods)

    @app.route('/admin/products/delete/<int:pid>', methods=['POST'])
    @admin_required
    def admin_products_delete(pid):
        p = Product.query.get_or_404(pid)
        if p.image:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], p.image))
            except:
                pass
        db.session.delete(p)
        db.session.commit()
        flash('Product deleted', 'info')
        return redirect(url_for('admin_products'))

    @app.route('/admin/blogs', methods=['GET', 'POST'])
    @admin_required
    def admin_blogs():
        if request.method == 'POST':
            title = request.form.get('title')
            excerpt = request.form.get('excerpt')
            content = request.form.get('content')
            img = request.files.get('image')
            filename = None
            if img and allowed_file(img.filename):
                fname = secure_filename(img.filename)
                filename = f"blog_{int(os.times().system * 1000)}_{fname}"
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                img.save(path)
                try:
                    im = Image.open(path)
                    im.thumbnail((1400, 900))
                    im.save(path, optimize=True, quality=80)
                except:
                    pass
            b = BlogPost(title=title, excerpt=excerpt, content=content, image=filename)
            db.session.add(b)
            db.session.commit()
            flash('Blog added', 'success')
            return redirect(url_for('admin_blogs'))

        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        return render_template('admin_blogs.html', posts=posts)

    @app.route('/admin/blogs/delete/<int:bid>', methods=['POST'])
    @admin_required
    def admin_blogs_delete(bid):
        b = BlogPost.query.get_or_404(bid)
        if b.image:
            try:
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], b.image))
            except:
                pass
        db.session.delete(b)
        db.session.commit()
        flash('Blog deleted', 'info')
        return redirect(url_for('admin_blogs'))

    @app.route('/admin/edit/<key>', methods=['GET', 'POST'])
    @admin_required
    def admin_edit(key):
        item = SiteContent.query.filter_by(key=key).first_or_404()
        if request.method == 'POST':
            item.value = request.form.get('value')
            db.session.commit()
            flash('Saved', 'success')
            return redirect(url_for('admin_dashboard'))
        return render_template('admin_edit.html', item=item)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app


# -------------------------
# Run app
# -------------------------
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
