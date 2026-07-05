from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash, abort
import json
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'gracebed-dev-secret-2025')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_JSON = os.path.join(BASE_DIR, 'products.json')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'products')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'gracebed2025')

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.office365.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'gracebeds01@outlook.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = 'gracebeds01@outlook.com'
mail = Mail(app)

SEED_PRODUCTS = {
    "royal-heritage": {
        "id": "royal-heritage",
        "name": "Royal Heritage Bed",
        "tagline": "Where centuries of craft meet modern luxury",
        "price": "Rs. 185,000",
        "price_range": "Rs. 185,000 - Rs. 320,000",
        "category": "Frame Bed",
        "sizes": ["Single", "Double", "Queen", "King"],
        "material": "Solid Sheesham Wood",
        "finish": "Dark Walnut Polish",
        "headboard": "Ornate carved headboard with gold inlay",
        "warranty": "10 Years",
        "description": "The Royal Heritage is our crown jewel - a masterpiece of Sheesham wood, hand-carved by artisans with decades of experience. Every joint, every curve, every detail speaks of uncompromising quality. This is not just a bed; it is an heirloom.",
        "features": [
            "Hand-carved solid Sheesham wood",
            "24-carat gold leaf detailing",
            "Mortise & tenon joinery - no screws",
            "Storage drawers with soft-close mechanism",
            "Orthopedic slat system included",
            "Custom size available on order"
        ],
        "color": "#8B4513",
        "image": ""
    },
    "obsidian-sultan": {
        "id": "obsidian-sultan",
        "name": "Obsidian Sultan Bed",
        "tagline": "Dark majesty. Silent power.",
        "price": "Rs. 210,000",
        "price_range": "Rs. 210,000 - Rs. 380,000",
        "category": "Ottoman Bed",
        "sizes": ["Double", "Queen", "King", "Super King"],
        "material": "Ebony-stained Mango Wood",
        "finish": "Jet Black Lacquer",
        "headboard": "Tufted velvet headboard - deep charcoal",
        "warranty": "12 Years",
        "description": "Inspired by the grand courts of the Mughals, the Obsidian Sultan commands every room it enters. Its midnight-black lacquer finish and towering tufted headboard create a silhouette of pure authority. The Ottoman lift-up base provides massive hidden storage.",
        "features": [
            "Gas-lift Ottoman storage base",
            "Tufted velvet headboard (3 colour options)",
            "Ebony-stained solid mango wood frame",
            "Anti-scratch lacquer finish",
            "Silent hydraulic lift mechanism",
            "Fits standard and custom mattresses"
        ],
        "color": "#1a1a2e",
        "image": ""
    },
    "ivory-empress": {
        "id": "ivory-empress",
        "name": "Ivory Empress Bed",
        "tagline": "Elegance carved in light and wood",
        "price": "Rs. 155,000",
        "price_range": "Rs. 155,000 - Rs. 260,000",
        "category": "Divan Bed Set",
        "sizes": ["Single", "Double", "Queen", "King"],
        "material": "White Oak & Rubberwood",
        "finish": "Ivory Matte with Brass Hardware",
        "headboard": "Fluted panel headboard with brass rail",
        "warranty": "8 Years",
        "description": "The Ivory Empress is femininity distilled into furniture. Pale oak tones, delicate fluted panels, and gleaming brass accents combine in a design that is both old-world and effortlessly modern. A complete divan set - mattress, base, and headboard - all in one.",
        "features": [
            "Complete divan set (base + headboard)",
            "Fluted oak panel design",
            "Solid brass hardware fittings",
            "4 drawer under-bed storage",
            "Hypoallergenic fabric lining",
            "Modular - splits for easy moving"
        ],
        "color": "#c8a96e",
        "image": ""
    },
    "cedar-throne": {
        "id": "cedar-throne",
        "name": "Cedar Throne Bed",
        "tagline": "Built for those who refuse to settle",
        "price": "Rs. 240,000",
        "price_range": "Rs. 240,000 - Rs. 420,000",
        "category": "Luxury Frame Bed",
        "sizes": ["Queen", "King", "Super King"],
        "material": "Himalayan Cedar Wood",
        "finish": "Natural Cedar with Teak Oil",
        "headboard": "Cathedral arch headboard - full height",
        "warranty": "15 Years",
        "description": "The Cedar Throne is our most prestigious creation. Crafted from rare Himalayan cedar - a wood prized for its natural fragrance, insect resistance, and incredible grain - this bed is built to outlast generations. The cathedral arch headboard stands nearly two metres tall.",
        "features": [
            "Rare Himalayan cedar - naturally fragrant",
            "Cathedral arch headboard (190cm tall)",
            "Lifetime structural guarantee on frame",
            "Hand-rubbed teak oil finish",
            "Integrated USB & wireless charging",
            "Bespoke engraving available"
        ],
        "color": "#6B3A2A",
        "image": ""
    }
}

def load_products():
    if not os.path.exists(PRODUCTS_JSON):
        save_products(SEED_PRODUCTS)
        return dict(SEED_PRODUCTS)
    with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_products(data):
    with open(PRODUCTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def slugify(name):
    return name.lower().strip().replace(' ', '-').replace('_', '-')[:50]

@app.route('/')
def home():
    products = load_products()
    return render_template('index.html', products=products)

@app.route('/collection')
def collection():
    products = load_products()
    return render_template('collection.html', products=products)

@app.route('/product/<product_id>')
def product(product_id):
    products = load_products()
    p = products.get(product_id)
    if not p:
        return render_template('404.html'), 404
    return render_template('product.html', product=p)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    products = load_products()
    if request.method == 'POST':
        name = request.form.get('fname', '') + ' ' + request.form.get('lname', '')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        bed = request.form.get('bed', '')
        size = request.form.get('size', '')
        message = request.form.get('message', '')

        # Save enquiry to file
        enquiry = {
            'date': str(datetime.now()),
            'name': name,
            'email': email,
            'phone': phone,
            'bed': bed,
            'size': size,
            'message': message
        }

        enquiries_file = os.path.join(BASE_DIR, 'enquiries.json')
        enquiries = []
        if os.path.exists(enquiries_file):
            with open(enquiries_file, 'r', encoding='utf-8') as f:
                enquiries = json.load(f)
        enquiries.append(enquiry)
        with open(enquiries_file, 'w', encoding='utf-8') as f:
            json.dump(enquiries, f, indent=2, ensure_ascii=False)

        flash('Thank you! Your enquiry has been received. We will contact you soon.', 'success')
        return redirect(url_for('contact'))

    return render_template('contact.html', products=products)

@app.route('/api/products')
def api_products():
    products = load_products()
    return jsonify(list(products.values()))

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    error = None
    if request.method == 'POST':
        pw = request.form.get('password', '')
        if pw == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        error = 'Invalid password. Please try again.'
    return render_template('admin/login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    products = load_products()
    return render_template('admin/dashboard.html', products=products)

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_add_product():
    if request.method == 'POST':
        products = load_products()
        name = request.form.get('name', '').strip()
        if not name:
            flash('Product name is required.', 'error')
            return redirect(url_for('admin_add_product'))

        product_id = slugify(name)
        base_id = product_id
        counter = 1
        while product_id in products:
            product_id = f"{base_id}-{counter}"
            counter += 1

        image_filename = ''
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                image_filename = f"{product_id}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        sizes_raw = request.form.get('sizes', '')
        sizes = [s.strip() for s in sizes_raw.split(',') if s.strip()]

        features_raw = request.form.get('features', '')
        features = [f.strip() for f in features_raw.split(chr(10)) if f.strip()]

        products[product_id] = {
            "id": product_id,
            "name": name,
            "tagline": request.form.get('tagline', '').strip(),
            "price": request.form.get('price', '').strip(),
            "price_range": request.form.get('price_range', '').strip(),
            "category": request.form.get('category', '').strip(),
            "sizes": sizes,
            "material": request.form.get('material', '').strip(),
            "finish": request.form.get('finish', '').strip(),
            "headboard": request.form.get('headboard', '').strip(),
            "warranty": request.form.get('warranty', '').strip(),
            "description": request.form.get('description', '').strip(),
            "features": features,
            "color": request.form.get('color', '#8B4513').strip(),
            "image": image_filename
        }
        save_products(products)
        flash(f'Product "{name}" added successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/product_form.html', product=None, mode='add')

@app.route('/admin/product/edit/<product_id>', methods=['GET', 'POST'])
@admin_required
def admin_edit_product(product_id):
    products = load_products()
    p = products.get(product_id)
    if not p:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Product name is required.', 'error')
            return redirect(url_for('admin_edit_product', product_id=product_id))

        image_filename = p.get('image', '')
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                if image_filename:
                    old_path = os.path.join(UPLOAD_FOLDER, image_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                ext = file.filename.rsplit('.', 1)[1].lower()
                image_filename = f"{product_id}.{ext}"
                file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        sizes_raw = request.form.get('sizes', '')
        sizes = [s.strip() for s in sizes_raw.split(',') if s.strip()]

        features_raw = request.form.get('features', '')
        features = [f.strip() for f in features_raw.split(chr(10)) if f.strip()]

        products[product_id] = {
            "id": product_id,
            "name": name,
            "tagline": request.form.get('tagline', '').strip(),
            "price": request.form.get('price', '').strip(),
            "price_range": request.form.get('price_range', '').strip(),
            "category": request.form.get('category', '').strip(),
            "sizes": sizes,
            "material": request.form.get('material', '').strip(),
            "finish": request.form.get('finish', '').strip(),
            "headboard": request.form.get('headboard', '').strip(),
            "warranty": request.form.get('warranty', '').strip(),
            "description": request.form.get('description', '').strip(),
            "features": features,
            "color": request.form.get('color', '#8B4513').strip(),
            "image": image_filename
        }
        save_products(products)
        flash(f'Product "{name}" updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/product_form.html', product=p, mode='edit')

@app.route('/admin/product/delete/<product_id>', methods=['POST'])
@admin_required
def admin_delete_product(product_id):
    products = load_products()
    p = products.pop(product_id, None)
    if p:
        img = p.get('image', '')
        if img:
            img_path = os.path.join(UPLOAD_FOLDER, img)
            if os.path.exists(img_path):
                os.remove(img_path)
        save_products(products)
        flash('Product deleted successfully.', 'success')
    else:
        flash('Product not found.', 'error')
    return redirect(url_for('admin_dashboard'))


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/newsletter', methods=['POST'])
def newsletter():
    email = request.form.get('email', '').strip()
    if email:
        # Save newsletter signup
        newsletter_file = os.path.join(BASE_DIR, 'newsletter.json')
        subscribers = []
        if os.path.exists(newsletter_file):
            with open(newsletter_file, 'r', encoding='utf-8') as f:
                subscribers = json.load(f)
        subscribers.append({'email': email, 'date': str(datetime.now())})
        with open(newsletter_file, 'w', encoding='utf-8') as f:
            json.dump(subscribers, f, indent=2, ensure_ascii=False)
        flash('Thank you for subscribing! You will receive our latest updates.', 'success')
    else:
        flash('Please enter a valid email address.', 'error')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
