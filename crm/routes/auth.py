from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from services.auth_helpers import validate_password_policy

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        role = request.form.get('role', 'Sales Executive')

        # Basic validation
        if not username or not email or not password:
            flash('Please fill all required fields', 'danger')
            return render_template('register.html')

        valid, msg = validate_password_policy(password)
        if not valid:
            flash(msg, 'danger')
            return render_template('register.html')

        # uniqueness
        from extensions import db
        from models.user import User
        from services.audit import record_audit

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists', 'danger')
            return render_template('register.html')

        pw_hash = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=pw_hash, role=role)
        db.session.add(user)
        db.session.commit()

        record_audit(user_id=user.id, action='Create', entity_name='User', record_id=str(user.id), new_value=f'Created user {user.username}')

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '')

        # Find by username or email
        from extensions import db
        from models.user import User
        from services.audit import record_audit

        user = User.query.filter((User.username == identifier) | (User.email == identifier.lower())).first()

        # Generic message
        msg = 'Invalid credentials'

        if user is None:
            # record a failed attempt without revealing user existence
            record_audit(action='Failed Login', entity_name='User', record_id=None, ip_address=request.remote_addr)
            flash(msg, 'danger')
            return render_template('login.html')

        # Check lockout
        if user.is_locked():
            flash('Account temporarily locked. Try again later or contact admin.', 'danger')
            record_audit(user_id=user.id, action='Failed Login - Locked', entity_name='User', record_id=str(user.id), ip_address=request.remote_addr)
            return render_template('login.html')

        if not check_password_hash(user.password_hash, password):
            user.failed_login_attempts = user.failed_login_attempts + 1
            # lock if threshold reached
            threshold = current_app.config.get('MAX_FAILED_LOGIN_ATTEMPTS', 5)
            if user.failed_login_attempts >= threshold:
                lock_minutes = current_app.config.get('ACCOUNT_LOCK_MINUTES', 15)
                user.locked_until = datetime.utcnow() + timedelta(minutes=lock_minutes)
                record_audit(user_id=user.id, action='Account Locked', entity_name='User', record_id=str(user.id), ip_address=request.remote_addr)
                flash('Account locked due to repeated failed login attempts.', 'danger')
            else:
                flash(msg, 'danger')
                record_audit(user_id=user.id, action='Failed Login', entity_name='User', record_id=str(user.id), ip_address=request.remote_addr)

            db.session.commit()
            return render_template('login.html')

        # successful login
        if not user.is_active:
            flash('Account is deactivated. Contact admin.', 'danger')
            return render_template('login.html')

        user.failed_login_attempts = 0
        user.locked_until = None
        db.session.commit()

        login_user(user)
        record_audit(user_id=user.id, action='Login', entity_name='User', record_id=str(user.id), ip_address=request.remote_addr)
        flash('Login successful', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    record_audit(user_id=current_user.id, action='Logout', entity_name='User', record_id=str(current_user.id))
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('auth.login'))
