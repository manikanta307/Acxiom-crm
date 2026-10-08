from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models.customer import Customer
from services.audit import record_audit
from schemas.customer_schema import CustomerSchema

customers_bp = Blueprint('customers', __name__, url_prefix='/customers')
_schema = CustomerSchema()


@customers_bp.route('/')
@login_required
def list_customers():
    q = request.args.get('q')
    query = Customer.query
    if q:
        query = query.filter(Customer.name.ilike(f"%{q}%"))
    customers = query.limit(100).all()
    return render_template('customers/list.html', customers=customers)


@customers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    if request.method == 'POST':
        data = request.form.to_dict()
        errors = _schema.validate(data)
        if errors:
            flash('Validation error: ' + str(errors), 'danger')
            return render_template('customers/create.html', data=data)

        # uniqueness checks
        if data.get('email') and Customer.query.filter_by(email=data.get('email')).first():
            flash('Email already exists', 'danger')
            return render_template('customers/create.html', data=data)
        if data.get('phone') and Customer.query.filter_by(phone=data.get('phone')).first():
            flash('Phone already exists', 'danger')
            return render_template('customers/create.html', data=data)

        customer = Customer(
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            owner_id=current_user.get_id()
        )
        db.session.add(customer)
        db.session.commit()
        record_audit(user_id=current_user.get_id(), action='Create', entity_name='Customer', record_id=str(customer.id), new_value=str(customer.to_dict()), ip_address=request.remote_addr)
        flash('Customer created', 'success')
        return redirect(url_for('customers.list_customers'))

    return render_template('customers/create.html')


@customers_bp.route('/<int:cid>')
@login_required
def customer_detail(cid):
    c = Customer.query.get_or_404(cid)
    return render_template('customers/detail.html', customer=c)


@customers_bp.route('/api', methods=['GET', 'POST'])
@login_required
def api_customers():
    if request.method == 'GET':
        customers = Customer.query.limit(200).all()
        return jsonify([c.to_dict() for c in customers])

    # POST
    payload = request.get_json() or {}
    errors = _schema.validate(payload)
    if errors:
        return jsonify({'errors': errors}), 400

    if payload.get('email') and Customer.query.filter_by(email=payload.get('email')).first():
        return jsonify({'error': 'Email exists'}), 400

    customer = Customer(
        name=payload.get('name'),
        email=payload.get('email'),
        phone=payload.get('phone'),
        address=payload.get('address'),
        owner_id=current_user.get_id()
    )
    db.session.add(customer)
    db.session.commit()
    record_audit(user_id=current_user.get_id(), action='Create', entity_name='Customer', record_id=str(customer.id), new_value=str(customer.to_dict()), ip_address=request.remote_addr)
    return jsonify(customer.to_dict()), 201
