from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ncr_trans_multilang_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ncr_trans_multilang.db'
db = SQLAlchemy(app)

ADMIN_EMAIL = "Islombekmurodjonv64@gmail.com"

# --- DATABASE MODELS ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(50), nullable=False) # Xalqaro bo'lmagan oddiy raqam
    role = db.Column(db.String(30), nullable=False) # 'admin', 'dispatcher', 'owner', 'driver'
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

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email=ADMIN_EMAIL).first():
        hashed_pw = generate_password_hash("admin123")
        admin_user = User(name="Islombekmurodjon", email=ADMIN_EMAIL, password=hashed_pw, phone="901234567", role='admin', is_verified=True)
        db.session.add(admin_user)
        db.session.commit()

# --- ROUTES ---
@app.route('/')
def index():
    lang = request.args.get('lang', 'uz')
    session['lang'] = lang
    
    from_c = request.args.get('from_city', '')
    to_c = request.args.get('to_city', '')
    
    cargos_query = Cargo.query.filter_by(status='Faol')
    if from_c:
        cargos_query = cargos_query.filter(Cargo.from_city.ilike(f"%{from_c}%"))
    if to_c:
        cargos_query = cargos_query.filter(Cargo.to_city.ilike(f"%{to_c}%"))
        
    cargos = cargos_query.all()
    return render_template('index.html', cargos=cargos, lang=lang)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']
        
        if email == ADMIN_EMAIL and role != 'admin':
            flash("Bu email faqat admin uchun!", "danger")
            return redirect(url_for('register'))

        user = User(name=name, email=email, phone=phone, password=password, role=role, is_verified=(role=='admin'))
        db.session.add(user)
        db.session.commit()
        flash("Ro'yxatdan o'tdingiz! Admin tasdiqlashini kuting.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if not user.is_verified and user.role != 'admin':
                flash("Hisobingiz hali admin tomonidan tasdiqlanmagan!", "warning")
                return redirect(url_for('login'))
            
            session['user_id'] = user.id
            session['role'] = user.role
            session['name'] = user.name
            session['email'] = user.email
            
            if user.email == ADMIN_EMAIL:
                return redirect(url_for('admin_panel'))
            return redirect(url_for('index'))
        flash("Email yoki parol xato!", "danger")
    return render_template('login.html')

@app.route('/add_cargo', methods=['GET', 'POST'])
def add_cargo():
    if 'user_id' not in session or session['role'] not in ['owner', 'dispatcher']:
        flash("Ruxsat yo'q!", "danger")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        new_cargo = Cargo(
            title=request.form['title'],
            from_city=request.form['from_city'],
            to_city=request.form['to_city'],
            weight=float(request.form['weight']),
            price=request.form['price'],
            cargo_type=request.form['cargo_type'],
            owner_id=session['user_id']
        )
        db.session.add(new_cargo)
        db.session.commit()
        flash("Yuk muvaffaqiyatli qo'shildi!", "success")
        return redirect(url_for('index'))
    return render_template('add_cargo.html')

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or session.get('email') != ADMIN_EMAIL:
        flash("Sizda admin huquqi yo'q!", "danger")
        return redirect(url_for('index'))
    
    pending_users = User.query.filter_by(is_verified=False).all()
    all_cargos = Cargo.query.all()
    all_users = User.query.all()
    return render_template('admin.html', pending_users=pending_users, all_cargos=all_cargos, all_users=all_users)

@app.route('/verify_user/<int:user_id>')
def verify_user(user_id):
    if session.get('email') == ADMIN_EMAIL:
        user = User.query.get(user_id)
        user.is_verified = True
        db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('email') == ADMIN_EMAIL:
        user = User.query.get(user_id)
        if user.email != ADMIN_EMAIL:
            db.session.delete(user)
            db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)