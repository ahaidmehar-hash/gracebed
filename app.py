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
PRODUCTS_JSON  = os.path.join(BASE_DIR, 'products.json')
CONTENT_JSON   = os.path.join(BASE_DIR, 'content.json')
GALLERY_JSON   = os.path.join(BASE_DIR, 'gallery.json')
SETTINGS_JSON  = os.path.join(BASE_DIR, 'settings.json')

UPLOAD_FOLDER  = os.path.join(BASE_DIR, 'static', 'images', 'products')
GALLERY_FOLDER = os.path.join(BASE_DIR, 'static', 'images', 'gallery')
BG_FOLDER      = os.path.join(BASE_DIR, 'static', 'images', 'bg')

os.makedirs(UPLOAD_FOLDER,  exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)
os.makedirs(BG_FOLDER,      exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_IMAGES_PER_PRODUCT = 6
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'gracebed2025')

# Email configuration
app.config['MAIL_SERVER']         = 'smtp.office365.com'
app.config['MAIL_PORT']           = 587
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = 'gracebeds01@outlook.com'
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = 'gracebeds01@outlook.com'
mail = Mail(app)

# ── Maintenance Mode Configuration ─────────────────────────────────────────────
MAINTENANCE_MODE = os.environ.get('MAINTENANCE_MODE', 'False').lower() == 'true'

@app.before_request
def check_maintenance_mode():
    """
    Check if maintenance mode is enabled.
    If yes, show maintenance page for all routes except /admin/*
    """
    if MAINTENANCE_MODE:
        # Allow admin routes to bypass maintenance mode
        if request.path.startswith('/admin'):
            return None
        
        # Load content for contact information
        with open(CONTENT_JSON, 'r') as f:
            content = json.load(f)
        
        return render_template(
            'maintenance.html',
            whatsapp_number=content['contact']['whatsapp_number'],
            phone_link=content['contact']['phone_link']
        ), 503

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
        "image": "",
        "images": []
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
        "image": "",
        "images": []
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
        "image": "",
        "images": []
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
        "image": "",
        "images": []
    }
}

SEED_CONTENT = {
    "hero": {
        "eyebrow": "Luxury Wooden Beds · Glasgow · Est. 2015",
        "title_line1": "Where Wood",
        "title_emphasis": "Becomes Legacy",
        "tagline": "Heirloom-quality beds, handcrafted from the finest woods.<br>Designed to outlast generations."
    },
    "contact": {
        "phone_display": "+44 0735 916 4886",
        "phone_link": "4407359164886",
        "email": "gracebeds01@outlook.com",
        "address": "Unit 2, 3 Siding Ln, Glasgow G5 0DZ, UK",
        "hours": "Mon–Sat: 10am – 8pm · Sun: 12pm – 6pm",
        "whatsapp_number": "447359164886"
    },
    "footer": {
        "brand_desc": "Where the silence of ancient forests becomes the furniture of your dreams. Every Grace Bed is built by hand, built to last, built to be inherited.",
        "copyright": "© 2025 Grace Bed. All rights reserved.",
        "tagline": "Crafted with precision. Built to last.",
        "instagram": "https://instagram.com/gracebed",
        "facebook": "https://facebook.com/gracebed"
    },
    "about": {
        "eyebrow": "Est. 2015 · Glasgow, United Kingdom",
        "tagline": "A decade of sawdust, polish, and the quiet pride of craftsmanship.",
        "story_heading_line1": "Born in a Workshop,",
        "story_heading_line2": "Built for Palaces",
        "story_para1": "Grace Bed began in 2015 in a small workshop on the outskirts of Glasgow. Our founder, a third-generation carpenter, believed that Scotland's craftsmen had the skill to produce beds worthy of the world's most discerning homes — they just needed someone willing to set the standard.",
        "story_para2": "Ten years later, every Grace Bed is still built by hand. We have grown our team, expanded our wood selection, and added new techniques — but the fundamental truth of our business has never changed: we will not use a single piece of material we would be ashamed of.",
        "story_para3": "Every joint is mortised. Every surface is hand-finished. Every bed is inspected for four hours before it leaves our doors. This is not a production line. It is a craft tradition.",
        "stat1_number": "10+",
        "stat1_label": "Years of Craft",
        "stat2_number": "1,200+",
        "stat2_label": "Beds Delivered",
        "stat3_number": "4",
        "stat3_label": "Master Craftsmen",
        "stat4_number": "100%",
        "stat4_label": "Solid Wood",
        "quote_text": "My grandfather built furniture that is still in use today. That is the only standard I know.",
        "quote_author": "Founder, Grace Bed · Glasgow"
    }
}

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_products():
    if not os.path.exists(PRODUCTS_JSON):
        save_products(SEED_PRODUCTS)
        return dict(SEED_PRODUCTS)
    with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Migrate legacy single-"image" products to the new "images" list format,
    # without breaking any template that still reads product.image directly.
    changed = False
    for p in data.values():
        if 'images' not in p:
            p['images'] = [p['image']] if p.get('image') else []
            changed = True
        if not p.get('image') and p.get('images'):
            p['image'] = p['images'][0]
            changed = True
    if changed:
        save_products(data)
    return data

def save_products(data):
    with open(PRODUCTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_content():
    if not os.path.exists(CONTENT_JSON):
        save_content(SEED_CONTENT)
        return dict(SEED_CONTENT)
    with open(CONTENT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for section, defaults in SEED_CONTENT.items():
        if section not in data:
            data[section] = defaults
        else:
            for key, val in defaults.items():
                if key not in data[section]:
                    data[section][key] = val
    return data

def save_content(data):
    with open(CONTENT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_gallery():
    if not os.path.exists(GALLERY_JSON):
        return []
    with open(GALLERY_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_gallery(data):
    with open(GALLERY_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_settings():
    if not os.path.exists(SETTINGS_JSON):
        return {'bg_image': ''}
    with open(SETTINGS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.context_processor
def inject_content():
    return {'content': load_content()}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def slugify(name):
    return name.lower().strip().replace(' ', '-').replace('_', '-')[:50]

def save_product_images(files, product_id):
    """
    Save a list of uploaded FileStorage objects for a product.
    Returns a list of saved filenames (in upload order).
    Each filename is unique (product_id + timestamp + index) so re-uploads
    never collide with previously saved images.
    """
    saved = []
    stamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    for i, file in enumerate(files):
        if not file or not file.filename:
            continue
        if not allowed_file(file.filename):
            continue
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{product_id}-{stamp}-{i}.{ext}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        saved.append(filename)
    return saved

def delete_product_image(filename):
    if not filename:
        return
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)

# ── Public routes ─────────────────────────────────────────────────────────────
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

@app.route('/workshop')
def workshop():
    gallery  = load_gallery()
    settings = load_settings()
    return render_template('workshop.html', gallery=gallery, settings=settings)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    products = load_products()
    if request.method == 'POST':
        name    = request.form.get('fname', '') + ' ' + request.form.get('lname', '')
        email   = request.form.get('email', '')
        phone   = request.form.get('phone', '')
        bed     = request.form.get('bed', '')
        size    = request.form.get('size', '')
        message = request.form.get('message', '')

        enquiry = {
            'date': str(datetime.now()),
            'name': name, 'email': email, 'phone': phone,
            'bed': bed, 'size': size, 'message': message
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

# ── Admin auth ────────────────────────────────────────────────────────────────
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

# ── Admin — Products ──────────────────────────────────────────────────────────
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

        # Multiple images support
        files = request.files.getlist('images') if 'images' in request.files else []
        images = save_product_images(files, product_id)[:MAX_IMAGES_PER_PRODUCT]

        sizes_raw    = request.form.get('sizes', '')
        sizes        = [s.strip() for s in sizes_raw.split(',') if s.strip()]
        features_raw = request.form.get('features', '')
        features     = [f.strip() for f in features_raw.split(chr(10)) if f.strip()]

        products[product_id] = {
            "id": product_id,
            "name": name,
            "tagline":     request.form.get('tagline', '').strip(),
            "price":       request.form.get('price', '').strip(),
            "price_range": request.form.get('price_range', '').strip(),
            "category":    request.form.get('category', '').strip(),
            "sizes":       sizes,
            "material":    request.form.get('material', '').strip(),
            "finish":      request.form.get('finish', '').strip(),
            "headboard":   request.form.get('headboard', '').strip(),
            "warranty":    request.form.get('warranty', '').strip(),
            "description": request.form.get('description', '').strip(),
            "features":    features,
            "color":       request.form.get('color', '#8B4513').strip(),
            "image":       images[0] if images else '',
            "images":      images
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

        existing_images = list(p.get('images', []))

        # Remove any images the admin checked for deletion
        remove_list = request.form.getlist('remove_images')
        for filename in remove_list:
            if filename in existing_images:
                delete_product_image(filename)
                existing_images.remove(filename)

        # Add newly uploaded images
        files = request.files.getlist('images') if 'images' in request.files else []
        new_images = save_product_images(files, product_id)
        all_images = (existing_images + new_images)[:MAX_IMAGES_PER_PRODUCT]

        sizes_raw    = request.form.get('sizes', '')
        sizes        = [s.strip() for s in sizes_raw.split(',') if s.strip()]
        features_raw = request.form.get('features', '')
        features     = [f.strip() for f in features_raw.split(chr(10)) if f.strip()]

        products[product_id] = {
            "id": product_id,
            "name": name,
            "tagline":     request.form.get('tagline', '').strip(),
            "price":       request.form.get('price', '').strip(),
            "price_range": request.form.get('price_range', '').strip(),
            "category":    request.form.get('category', '').strip(),
            "sizes":       sizes,
            "material":    request.form.get('material', '').strip(),
            "finish":      request.form.get('finish', '').strip(),
            "headboard":   request.form.get('headboard', '').strip(),
            "warranty":    request.form.get('warranty', '').strip(),
            "description": request.form.get('description', '').strip(),
            "features":    features,
            "color":       request.form.get('color', '#8B4513').strip(),
            "image":       all_images[0] if all_images else '',
            "images":      all_images
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
        for img in p.get('images', []):
            delete_product_image(img)
        save_products(products)
        flash('Product deleted successfully.', 'success')
    else:
        flash('Product not found.', 'error')
    return redirect(url_for('admin_dashboard'))

# ── Admin — Content ───────────────────────────────────────────────────────────
@app.route('/admin/content', methods=['GET', 'POST'])
@admin_required
def admin_content():
    content = load_content()
    if request.method == 'POST':
        content['hero']['eyebrow']        = request.form.get('hero_eyebrow', '').strip()
        content['hero']['title_line1']    = request.form.get('hero_title_line1', '').strip()
        content['hero']['title_emphasis'] = request.form.get('hero_title_emphasis', '').strip()
        content['hero']['tagline']        = request.form.get('hero_tagline', '').strip()

        content['contact']['phone_display']    = request.form.get('phone_display', '').strip()
        content['contact']['phone_link']       = request.form.get('phone_link', '').strip()
        content['contact']['email']            = request.form.get('email', '').strip()
        content['contact']['address']          = request.form.get('address', '').strip()
        content['contact']['hours']            = request.form.get('hours', '').strip()
        content['contact']['whatsapp_number']  = request.form.get('whatsapp_number', '').strip()

        content['footer']['brand_desc']  = request.form.get('brand_desc', '').strip()
        content['footer']['copyright']   = request.form.get('copyright', '').strip()
        content['footer']['tagline']     = request.form.get('footer_tagline', '').strip()
        content['footer']['instagram']   = request.form.get('instagram', '').strip()
        content['footer']['facebook']    = request.form.get('facebook', '').strip()

        content['about']['eyebrow']             = request.form.get('about_eyebrow', '').strip()
        content['about']['tagline']             = request.form.get('about_tagline', '').strip()
        content['about']['story_heading_line1'] = request.form.get('story_heading_line1', '').strip()
        content['about']['story_heading_line2'] = request.form.get('story_heading_line2', '').strip()
        content['about']['story_para1']         = request.form.get('story_para1', '').strip()
        content['about']['story_para2']         = request.form.get('story_para2', '').strip()
        content['about']['story_para3']         = request.form.get('story_para3', '').strip()
        content['about']['stat1_number']        = request.form.get('stat1_number', '').strip()
        content['about']['stat1_label']         = request.form.get('stat1_label', '').strip()
        content['about']['stat2_number']        = request.form.get('stat2_number', '').strip()
        content['about']['stat2_label']         = request.form.get('stat2_label', '').strip()
        content['about']['stat3_number']        = request.form.get('stat3_number', '').strip()
        content['about']['stat3_label']         = request.form.get('stat3_label', '').strip()
        content['about']['stat4_number']        = request.form.get('stat4_number', '').strip()
        content['about']['stat4_label']         = request.form.get('stat4_label', '').strip()
        content['about']['quote_text']          = request.form.get('quote_text', '').strip()
        content['about']['quote_author']        = request.form.get('quote_author', '').strip()

        save_content(content)
        flash('Site content updated successfully.', 'success')
        return redirect(url_for('admin_content'))

    return render_template('admin/content.html', content=content)

# ── Admin — Gallery ───────────────────────────────────────────────────────────
@app.route('/admin/gallery')
@admin_required
def admin_gallery():
    gallery = load_gallery()
    return render_template('admin/gallery.html', gallery=gallery)

@app.route('/admin/gallery/add', methods=['POST'])
@admin_required
def admin_gallery_add():
    gallery = load_gallery()
    caption = request.form.get('caption', '').strip()

    if 'photo' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('admin_gallery'))

    file = request.files['photo']
    if not file or not file.filename or not allowed_file(file.filename):
        flash('Invalid file type. Use jpg, png, webp.', 'error')
        return redirect(url_for('admin_gallery'))

    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"gallery_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.{ext}"
    file.save(os.path.join(GALLERY_FOLDER, filename))

    gallery.append({
        'id':       filename,
        'filename': filename,
        'caption':  caption,
        'uploaded': str(datetime.now())
    })
    save_gallery(gallery)
    flash('Photo added to workshop gallery.', 'success')
    return redirect(url_for('admin_gallery'))

@app.route('/admin/gallery/delete/<filename>', methods=['POST'])
@admin_required
def admin_gallery_delete(filename):
    gallery = load_gallery()
    gallery = [g for g in gallery if g['filename'] != filename]
    save_gallery(gallery)
    path = os.path.join(GALLERY_FOLDER, filename)
    if os.path.exists(path):
        os.remove(path)
    flash('Photo removed from gallery.', 'success')
    return redirect(url_for('admin_gallery'))

# ── Admin — Settings (background image) ──────────────────────────────────────
@app.route('/admin/settings', methods=['GET', 'POST'])
@admin_required
def admin_settings():
    settings = load_settings()

    if request.method == 'POST':
        if 'bg_image' in request.files:
            file = request.files['bg_image']
            if file and file.filename and allowed_file(file.filename):
                old = settings.get('bg_image', '')
                if old:
                    old_path = os.path.join(BG_FOLDER, old)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                ext      = file.filename.rsplit('.', 1)[1].lower()
                filename = f"bg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
                file.save(os.path.join(BG_FOLDER, filename))
                settings['bg_image'] = filename
                save_settings(settings)
                flash('Background image updated successfully.', 'success')
            else:
                flash('Invalid file. Use jpg, png, webp.', 'error')
        return redirect(url_for('admin_settings'))

    return render_template('admin/settings.html', settings=settings)

# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)