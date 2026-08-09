from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import io
import qrcode
from base64 import b64encode

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ncr_trans_premium_max_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ncr_trans_multilang.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)

ADMIN_EMAIL = "Islombekmurodjonv64@gmail.com"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

class Cargo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    from_city = db.Column(db.String(100), nullable=False)
    to_city = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    price = db.Column(db.String(50), nullable=False)
    cargo_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(30), default='Faol')
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref='cargos')

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email=ADMIN_EMAIL).first():
        hashed_pw = generate_password_hash("admin123")
        admin_user = User(name="Islombekmurodjon", email=ADMIN_EMAIL, password=hashed_pw, phone="+90 0850 284 52 45", role='admin', is_verified=True)
        db.session.add(admin_user)
        db.session.commit()

LAYOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>NCR TRANS - VIP Logistika Tizimi</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary-gold: #ffb703; --dark-navy: #023047; --light-bg: #f8f9fa; }
        body { background-color: #f0f2f5; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .hero-section { background: linear-gradient(135deg, #023047 0%, #219ebc 100%); color: white; padding: 40px 15px; border-radius: 0 0 25px 25px; }
        .premium-card { border: none; border-radius: 15px; box-shadow: 0 10px 20px rgba(0,0,0,0.08); transition: all 0.3s ease; background: white; margin-bottom: 20px; }
        .premium-card:hover { transform: translateY(-5px); box-shadow: 0 15px 30px rgba(0,0,0,0.15); }
        .btn-gold { background: var(--primary-gold); color: #000; font-weight: bold; border: none; border-radius: 10px; padding: 10px 20px; }
        .btn-gold:hover { background: #fb8500; color: white; }
        .badge-status { font-size: 0.85rem; padding: 6px 12px; border-radius: 20px; }
        .ai-box { background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); color: white; border-radius: 15px; padding: 20px; }
        @media (max-width: 576px) {
            .hero-section { padding: 25px 10px; text-align: center; }
            .btn-gold { width: 100%; margin-top: 10px; }
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark sticky-top shadow-sm">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center" href="/">
                <div class="bg-warning text-dark fw-bold px-3 py-1 rounded me-2">NCR</div>
                <span class="fw-bold text-white">TRANS LOGISTICS</span>
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto align-items-center">
                    <li class="nav-item"><a class="nav-link text-white" href="/"><i class="fa-solid fa-truck"></i> Bosh sahifa</a></li>
                    {% if session.get('user_id') %}
                        {% if session.get('role') in ['owner', 'dispatcher', 'admin'] %}
                            <li class="nav-item"><a class="nav-link text-warning" href="/add_cargo"><i class="fa-solid fa-plus-circle"></i> Yuk Qo'shish</a></li>
                        {% endif %}
                        {% if session.get('email') == 'Islombekmurodjonv64@gmail.com' %}
                            <li class="nav-item"><a class="nav-link text-danger fw-bold" href="/admin"><i class="fa-solid fa-user-shield"></i> Admin Panel</a></li>
                        {% endif %}
                        <li class="nav-item"><a class="btn btn-outline-light btn-sm ms-2" href="/logout">Chiqish ({{ session.get('name') }})</a></li>
                    {% else %}
                        <li class="nav-item"><a class="nav-link text-white" href="/login">Kirish</a></li>
                        <li class="nav-item"><a class="btn btn-warning btn-sm ms-2 fw-bold" href="/register">Ro'yxatdan o'tish</a></li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-3">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    {% block content %}{% endblock %}

    <footer class="bg-dark text-white text-center py-4 mt-5">
        <div class="container">
            <p class="mb-1 fw-bold">© 2026 OOO "NCR TRANS". Barcha huquqlar himoyalangan.</p>
            <small class="text-muted">Xalqaro va Ichki Avto Tashuvlar Tizimi | AI-Powered Platform</small>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    from_c = request.args.get('from_city', '')
    to_c = request.args.get('to_city', '')
    
    cargos_query = Cargo.query.filter_by(status='Faol')
    if from_c:
        cargos_query = cargos_query.filter(Cargo.from_city.ilike(f"%{from_c}%"))
    if to_c:
        cargos_query = cargos_query.filter(Cargo.to_city.ilike(f"%{to_c}%"))
        
    cargos = cargos_query.all()

    content = """
    {% extends "layout" %}
    {% block content %}
    <div class="hero-section text-center mb-4">
        <div class="container">
            <h1 class="fw-bold">NCR TRANS — Aqlli Logistika Platformasi</h1>
            <p class="lead">Xalqaro va shaharlararo yuklarni tez va qulay toping</p>
            
            <form method="GET" action="/" class="row g-2 justify-content-center mt-3">
                <div class="col-md-4 col-6">
                    <input type="text" name="from_city" class="form-control form-control-lg" placeholder="Qayerdan (Shahar)...">
                </div>
                <div class="col-md-4 col-6">
                    <input type="text" name="to_city" class="form-control form-control-lg" placeholder="Qayerga (Shahar)...">
                </div>
                <div class="col-md-2 col-12">
                    <button type="submit" class="btn btn-gold btn-lg w-100"><i class="fa-solid fa-search"></i> Qidirish</button>
                </div>
            </form>
        </div>
    </div>

    <div class="container">
        <div class="ai-box shadow-sm mb-4">
            <div class="d-flex align-items-center mb-2">
                <i class="fa-solid fa-robot fa-2x me-3"></i>
                <h4 class="mb-0 fw-bold">NCR AI Smart Assistent</h4>
            </div>
            <p class="mb-0">AIning analitik algoritmi orqali yuklar narxi va masofa xavfi avtomatik monitoring qilinadi.</p>
        </div>

        <h3 class="fw-bold mb-3 text-dark"><i class="fa-solid fa-boxes-packing text-warning"></i> Faol Yuklar E'lonlari</h3>
        <div class="row">
            {% for cargo in cargos %}
            <div class="col-md-6 col-lg-4">
                <div class="premium-card p-3">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="badge bg-success badge-status"><i class="fa-solid fa-circle-check"></i> {{ cargo.status }}</span>
                        <span class="fw-bold text-primary">{{ cargo.price }}</span>
                    </div>
                    <h5 class="fw-bold text-dark mb-2">{{ cargo.title }}</h5>
                    <p class="text-muted mb-1"><i class="fa-solid fa-location-dot text-danger"></i> <strong>Yo'nalish:</strong> {{ cargo.from_city }} ➔ {{ cargo.to_city }}</p>
                    <p class="text-muted mb-1"><i class="fa-solid fa-weight-hanging text-secondary"></i> <strong>O'g'irligi:</strong> {{ cargo.weight }} Tonna | {{ cargo.cargo_type }}</p>
                    
                    <hr>
                    <div class="d-flex justify-content-between align-items-center">
                        <button class="btn btn-outline-dark btn-sm" data-bs-toggle="modal" data-bs-target="#contactModal{{ cargo.id }}">
                            <i class="fa-solid fa-phone text-success"></i> Aloqaga Chiqish
                        </button>
                        <a href="/generate_pdf/{{ cargo.id }}" class="btn btn-outline-danger btn-sm" target="_blank">
                            <i class="fa-solid fa-file-pdf"></i> QR PDF
                        </a>
                    </div>
                </div>
            </div>

            <div class="modal fade" id="contactModal{{ cargo.id }}" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header bg-dark text-white">
                            <h5 class="modal-header-title mb-0"><i class="fa-solid fa-user"></i> Yuk Egasining Ma'lumotlari</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body text-center py-4">
                            <i class="fa-solid fa-id-card-clip fa-3x text-warning mb-3"></i>
                            <h4 class="fw-bold text-dark">{{ cargo.owner.name }}</h4>
                            <p class="text-muted mb-3">Kompaniya / Mas'ul shaxs</p>
                            <div class="p-3 bg-light rounded border mb-3">
                                <h3 class="fw-bold text-success mb-0">{{ cargo.owner.phone if cargo.owner.phone and cargo.owner.phone != '+' else '+90 0850 284 52 45' }}</h3>
                            </div>
                            <a href="tel:{{ cargo.owner.phone if cargo.owner.phone and cargo.owner.phone != '+' else '+90 0850 284 52 45' }}" class="btn btn-success btn-lg w-100 fw-bold">
                                <i class="fa-solid fa-phone-flip me-2"></i> Qo'ng'iroq Qilish
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% else %}
            <div class="col-12 text-center py-5">
                <i class="fa-solid fa-box-open fa-4x text-muted mb-3"></i>
                <h4 class="text-muted">Hozircha hech qanday faol yuk e'loni mavjud emas.</h4>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(LAYOUT_TEMPLATE.replace('{% block content %}{% endblock %}', content), cargos=cargos)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        raw_password = request.form.get('password')
        role = request.form.get('role', 'driver')
        
        if not phone or phone.strip() == '+':
            phone = "+90 0850 284 52 45"

        user = User(name=name, email=email, phone=phone, password=generate_password_hash(raw_password), role=role, is_verified=(email == ADMIN_EMAIL or role == 'admin'))
        db.session.add(user)
        db.session.commit()
        flash("Muvaffaqiyatli ro'yxatdan o'tdingiz! Tizimga kiring.", "success")
        return redirect(url_for('login'))

    content = """
    {% extends "layout" %}
    {% block content %}
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="premium-card p-4">
                    <h3 class="fw-bold text-center mb-3">Ro'yxatdan O'tish</h3>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Ism / Kompaniya</label>
                            <input type="text" name="name" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Telefon Raqam</label>
                            <input type="text" name="phone" class="form-control" value="+90 0850 284 52 45" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Parol</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Rolingiz</label>
                            <select name="role" class="form-select">
                                <option value="driver">Haydovchi (Yuk Qidiruvchi)</option>
                                <option value="owner">Yuk Egasi</option>
                                <option value="dispatcher">Logist / Dispetcher</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-gold w-100">Ro'yxatdan o'tish</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(LAYOUT_TEMPLATE.replace('{% block content %}{% endblock %}', content))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            session['email'] = user.email
            return redirect(url_for('index'))
        flash("Email yoki parol xato!", "danger")

    content = """
    {% extends "layout" %}
    {% block content %}
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-md-5">
                <div class="premium-card p-4">
                    <h3 class="fw-bold text-center mb-3">Tizimga Kirish</h3>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Email</label>
                            <input type="email" name="email" class="form-control" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Parol</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-gold w-100">Kirish</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(LAYOUT_TEMPLATE.replace('{% block content %}{% endblock %}', content))

@app.route('/add_cargo', methods=['GET', 'POST'])
def add_cargo():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        cargo = Cargo(
            title=request.form.get('title'),
            from_city=request.form.get('from_city'),
            to_city=request.form.get('to_city'),
            weight=float(request.form.get('weight', 0)),
            price=request.form.get('price'),
            cargo_type=request.form.get('cargo_type'),
            owner_id=session['user_id']
        )
        db.session.add(cargo)
        db.session.commit()
        flash("Yangi yuk e'loni joylandi!", "success")
        return redirect(url_for('index'))

    content = """
    {% extends "layout" %}
    {% block content %}
    <div class="container py-4">
        <div class="row justify-content-center">
            <div class="col-md-6">
                <div class="premium-card p-4">
                    <h3 class="fw-bold mb-3"><i class="fa-solid fa-box text-warning"></i> Yangi Yuk Joylash</h3>
                    <form method="POST">
                        <div class="mb-3">
                            <label class="form-label">Yuk Nomi</label>
                            <input type="text" name="title" class="form-control" placeholder="Masalan: Maishiy texnika" required>
                        </div>
                        <div class="row">
                            <div class="col-6 mb-3">
                                <label class="form-label">Qayerdan</label>
                                <input type="text" name="from_city" class="form-control" placeholder="Toshkent" required>
                            </div>
                            <div class="col-6 mb-3">
                                <label class="form-label">Qayerga</label>
                                <input type="text" name="to_city" class="form-control" placeholder="Istanbul" required>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-6 mb-3">
                                <label class="form-label">Massa (Tonna)</label>
                                <input type="number" step="0.1" name="weight" class="form-control" required>
                            </div>
                            <div class="col-6 mb-3">
                                <label class="form-label">Transport Turi</label>
                                <input type="text" name="cargo_type" class="form-control" placeholder="Tenta / Fura" required>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Taklif Qilingan Narx ($ / UZS)</label>
                            <input type="text" name="price" class="form-control" placeholder="2500 $" required>
                        </div>
                        <button type="submit" class="btn btn-gold w-100 fw-bold"><i class="fa-solid fa-paper-plane"></i> E'lonni Chop Etish</button>
                    </form>
                </div>
            </div>
        </div>
    </div>
    {% endblock %}
    """
    return render_template_string(LAYOUT_TEMPLATE.replace('{% block content %}{% endblock %}', content))

@app.route('/generate_pdf/<int:cargo_id>')
def generate_pdf(cargo_id):
    cargo = Cargo.query.get_or_404(cargo_id)
    owner_phone = cargo.owner.phone if cargo.owner.phone and cargo.owner.phone != '+' else '+90 0850 284 52 45'
    
    qr_data = f"NCR TRANS VERIFIED CARGO\\nID: {cargo.id}\\nNomi: {cargo.title}\\nYo'nalish: {cargo.from_city} -> {cargo.to_city}\\nOwner Phone: {owner_phone}"
    qr = qrcode.make(qr_data)
    buf = io.BytesIO()
    qr.save(buf, format='PNG')
    qr_b64 = b64encode(buf.getvalue()).decode('utf-8')

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NCR TRANS - Yuk Hujjati #{cargo.id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 30px; border: 10px solid #023047; }}
            .header {{ text-align: center; border-bottom: 2px solid #ffb703; padding-bottom: 15px; }}
            .qr-code {{ text-align: right; margin-top: -60px; }}
            .details {{ margin-top: 30px; font-size: 16px; line-height: 1.8; }}
            .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #777; }}
        </style>
    </head>
    <body onload="window.print()">
        <div class="header">
            <h1 style="color: #023047; margin:0;">OOO "NCR TRANS"</h1>
            <p style="margin:5px;">RASMIY YUK HAMROHLIK HUJJATI (WAYBILL)</p>
        </div>
        <div class="qr-code">
            <img src="data:image/png;base64,{qr_b64}" width="100">
        </div>
        <div class="details">
            <p><strong>Hujjat Raqami:</strong> #NCR-{cargo.id}2026</p>
            <p><strong>Yuk Nomi:</strong> {cargo.title}</p>
            <p><strong>Yo'nalish:</strong> {cargo.from_city} ➔ {cargo.to_city}</p>
            <p><strong>Og'irligi va Turi:</strong> {cargo.weight} Tonna ({cargo.cargo_type})</p>
            <p><strong>Kelishilgan Qiymati:</strong> {cargo.price}</p>
            <p><strong>Egasining Telefon Raqami:</strong> {owner_phone}</p>
            <p><strong>Status:</strong> Tasdiqlangan / Faol</p>
        </div>
        <div class="footer">
            <p>Ushbu hujjat NCR TRANS xalqaro avto-tashuvlar raqamli platformasi orqali avtomatik shakllantirildi.</p>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)