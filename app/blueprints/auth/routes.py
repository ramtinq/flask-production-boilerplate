from flask import redirect, render_template, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from sqlalchemy import select

from .tasks import compute_heavy_data, store_result_to_db
from celery import chain

from . import auth_bp
from .forms import RegisterForm, LoginForm
from .models import User
from app.extensions import db, bcrypt
from app.blueprints.calculations.models import CalculationResult

from app.utils import paginate

@auth_bp.get('/register')
def register_get():
    form = RegisterForm()
    return render_template('auth/register.html', form=form)

@auth_bp.post('/register')
def register_post():

    form = RegisterForm()

    if not form.validate_on_submit():
        return render_template('auth/register.html', form=form)

    hashed_password = bcrypt.generate_password_hash(form.password.data)

    new_user = User(username=form.username.data, password = hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.user_login_get'))


@auth_bp.get('/login')
def user_login_get(form: LoginForm = None):
    form = form or LoginForm()
    return render_template('auth/login.html', form=form)
    
@auth_bp.post('/login')
def user_login_post():
    form = LoginForm()
    if not form.validate_on_submit():
        return user_login_get(form=form)
    
    #find:
    user = db.session.scalar(select(User).where(User.username == form.username.data))
    #user = User.query.filter_by(username = username).first()
    if user and bcrypt.check_password_hash(user.password, form.password.data):
        login_user(user)
        flash('Login successful!', 'success')
        return redirect(url_for('auth.user_dashboard'))
    
    form.username.errors.append('Invalid username or password')
    
    return user_login_get(form=form)

    #return render_template('login.html', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.home'))

@auth_bp.route('/dashboard', methods=['GET'])
@login_required
def user_dashboard():
    return render_template('auth/dashboard.html')

    
@auth_bp.route("/dashboard/calculation-results")
@auth_bp.route("/dashboard/calculation-results/<int:page>")
@login_required
def user_calculation_results(page=1):
    query = (
        db.select(CalculationResult)
        #.where(CalculationResult.user_id == current_user.id)
        .order_by(CalculationResult.id.desc())
    )
    query = paginate(query, page=page, per_page=20)

    results = db.session.scalars(query).all()

    return render_template("auth/calculation_results.html", results=results)


@auth_bp.route("/task/estimate-pi/<int:samples>")
@login_required
def user_estimate_pi(samples):
    workflow = chain(
            compute_heavy_data.s(samples), 
            store_result_to_db.s(user_id=current_user.id)
        )
    # (result of each function will be passed to thefirst argument of the next one)

    workflow.apply_async()
    return jsonify({"message": "Pipeline started"})


