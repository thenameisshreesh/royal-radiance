import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from PIL import Image
from config import Config

from supabase_db import (
    get_all_products, add_product, delete_product,
    get_all_blogs, add_blog, delete_blog,
    get_site_content, update_site_content, add_site_content,
    upload_to_supabase_storage  # ✅ new
)


from flask_mail import Mail, Message
from datetime import timedelta
from functools import wraps

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def admin_required(fn):
    @wraps(fn)
    def wrapper(*a, **kw):
        if session.get('admin_logged'):
            return fn(*a, **kw)
        flash('You must log in as admin to access that page.', 'warning')
        return redirect(url_for('admin_login'))
    return wrapper

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    # ensure upload folder exists locally
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    except Exception as e:
        # if creation fails on readonly FS, keep going (we handle save errors later)
        print("⚠️ Could not create upload folder:", e)

    UPLOAD_STATIC = os.path.join(app.static_folder, 'uploads')
    os.makedirs(UPLOAD_STATIC, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_STATIC
    app.config['UPLOAD_STATIC'] = UPLOAD_STATIC

    
    mail = Mail(app)
    app.permanent_session_lifetime = timedelta(seconds=app.config['PERMANENT_SESSION_LIFETIME'])

    # Ensure default site content exists (previously done by SQLAlchemy)
    try:
        if get_site_content('about') is None:
            add_site_content('about', 'Royal Radiance — handcrafted candles to light your moments. Edit this in admin.')
        if get_site_content('special_offer') is None:
            add_site_content('special_offer', 'Limited-time: Golden Autumn collection — 20% off!')
    except Exception as e:
        print("⚠️ Could not ensure default site content:", e)

    # route to serve uploaded files (templates use url_for('uploads', filename=...))
    @app.route('/uploads/<path:filename>')
    def uploads(filename):
        # Serve files from UPLOAD_FOLDER if exists, else 404
        folder = app.config.get('UPLOAD_STATIC')
        if folder and os.path.exists(os.path.join(folder, filename)):
            return send_from_directory(folder, filename)
        # Not found (on Vercel might be ephemeral), return 404
        return "", 404

    # ------------------------- Public routes -------------------------
    @app.route('/')
    def home():
        products = get_all_products() or []
        # Defensive: ensure list
        if not isinstance(products, list):
            products = []
        special = get_site_content('special_offer')
        return render_template('home.html', products=products[:6], special=special or '')

    @app.route('/about')
    def about():
        about_text = get_site_content('about') or ''
        return render_template('about.html', about_text=about_text)

    @app.route('/catalog')
    def catalog():
        products = get_all_products() or []
        if not isinstance(products, list):
            products = []
        return render_template('catalog.html', products=products)

    @app.route('/product/<int:pid>')
    def product_api(pid):
        all_prods = get_all_products() or []
        p = next((x for x in all_prods if int(x.get('id', 0)) == pid), None)
        if not p:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify(p)

    @app.route('/blog')
    def blog():
        posts = get_all_blogs() or []
        return render_template('blog.html', posts=posts)

    @app.route('/blog/<int:bid>')
    def blog_post(bid):
        posts = get_all_blogs() or []
        post = next((x for x in posts if int(x.get('id', 0)) == bid), None)
        if not post:
            return "Blog not found", 404
        return render_template('blog_post.html', post=post)

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            msg = request.form.get('message')
            try:
                message = Message(
                    subject=f"🕯️ New Inquiry from {name}",
                    sender=app.config.get('MAIL_DEFAULT_SENDER'),
                    recipients=[app.config.get('MAIL_DEFAULT_SENDER')],
                    reply_to=email
                )
                bg_url = url_for('static', filename='images/cg.gif', _external=True)
                message.html = f"<p><b>{name}</b> ({email}) wrote:</p><p>{msg}</p>"
                message.body = f"From: {name} <{email}>\n\n{msg}"
                mail.send(message)
                flash('Your message was sent successfully!', 'success')
            except Exception as ex:
                print('Mail error:', ex)
                flash('Could not send message.', 'warning')
            return redirect(url_for('contact'))
        return render_template('contact.html')

    # ------------------------- Admin routes -------------------------
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            pwd = request.form.get('password', '')
            stored_hash = app.config.get('ADMIN_PASSWORD_HASH')
            if check_password_hash(stored_hash, pwd):
                session['admin_logged'] = True
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Wrong password', 'danger')
        return render_template('admin_login.html')

    @app.route('/admin/logout')
    def admin_logout():
        session.clear()
        flash('Logged out.', 'info')
        return redirect(url_for('home'))

    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        products = get_all_products() or []
        blogs = get_all_blogs() or []
        return render_template('admin_dashboard.html', products=len(products), blogs=len(blogs))

    @app.route('/admin/products', methods=['GET', 'POST'])
    @admin_required
    def admin_products():
        if request.method == 'POST':
            name = request.form.get('name')
            desc = request.form.get('short_desc')

            try:
                price = float(request.form.get('price') or 0)
            except:
                price = 0.0

            img = request.files.get('image')
            image_url = None

            if img and allowed_file(img.filename):
                fname = secure_filename(img.filename)
                filename = f"prod_{fname}"
                file_bytes = img.read()
            # ✅ Upload to Supabase Storage
                image_url = upload_to_supabase_storage(filename, file_bytes, img.content_type)

            ok = add_product(name, desc, price, image_url)
            if not ok:
                flash('⚠️ Could not add product to database — check logs.', 'warning')
            else:
                flash('✅ Product added successfully!', 'success')
            return redirect(url_for('admin_products'))

    # Fetch all products
        products = get_all_products() or []
        for p in products:
            if not p.get('image'):
                p['image'] = url_for('static', filename='images/no_image.png')
        return render_template('admin_products.html', products=products)


    @app.route('/admin/blogs', methods=['GET', 'POST'])
    @admin_required
    def admin_blogs():
        if request.method == 'POST':
            title = request.form.get('title')
            excerpt = request.form.get('excerpt')
            content = request.form.get('content')

            img = request.files.get('image')
            image_url = None

            if img and allowed_file(img.filename):
                fname = secure_filename(img.filename)
                filename = f"blog_{fname}"
                file_bytes = img.read()
            # ✅ Upload to Supabase Storage
                image_url = upload_to_supabase_storage(filename, file_bytes, img.content_type)

            ok = add_blog(title, excerpt, content, image_url)
            if not ok:
                flash('⚠️ Could not add blog — check logs.', 'warning')
            else:
                flash('✅ Blog added successfully!', 'success')
            return redirect(url_for('admin_blogs'))

    # Fetch all blog posts
        posts = get_all_blogs() or []
        return render_template('admin_blogs.html', posts=posts)








    @app.route('/admin/products/delete/<int:pid>', methods=['POST'])
    @admin_required
    def admin_products_delete(pid):
        ok = delete_product(pid)
        if not ok:
            flash('Could not delete product — check logs.', 'warning')
        else:
            flash('Product deleted.', 'info')
        return redirect(url_for('admin_products'))

    
    @app.route('/admin/blogs/delete/<int:bid>', methods=['POST'])
    @admin_required
    def admin_blogs_delete(bid):
        ok = delete_blog(bid)
        if not ok:
            flash('Could not delete blog — check logs.', 'warning')
        else:
            flash('Blog deleted.', 'info')
        return redirect(url_for('admin_blogs'))

    @app.route('/admin/edit/<key>', methods=['GET', 'POST'])
    @admin_required
    def admin_edit(key):
        if request.method == 'POST':
            val = request.form.get('value')
            ok = update_site_content(key, val)
            if not ok:
                flash('Could not update content — check logs.', 'warning')
            else:
                flash('Updated successfully.', 'success')
            return redirect(url_for('admin_dashboard'))
        val = get_site_content(key) or ''
        return render_template('admin_edit.html', item={'key': key, 'value': val})

    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    return app

# create app instance for WSGI
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
