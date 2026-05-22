from flask import Flask, redirect, render_template, request, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from flask_bcrypt import Bcrypt

from models import CalculationResult, User
from forms import RegisterForm, LoginForm

from tasks import random_number, compute_heavy_data, store_result_to_db
from celery.result import AsyncResult
from celery import chain
from celery_app import celery
from utils import paginate

def register_routes(app: Flask, db: SQLAlchemy, bcrypt: Bcrypt):
     
    @app.route('/', methods=['GET'])
    def home():
        return render_template('home.html')
    
    @app.get('/register')
    def register_get():
        form = RegisterForm()
        return render_template('register.html', form=form)
    
    @app.post('/register')
    def register_post():

        form = RegisterForm()

        if not form.validate_on_submit():
            return render_template('register.html', form=form)

        hashed_password = bcrypt.generate_password_hash(form.password.data)

        new_user = User(username=form.username.data, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('user_login_get'))

    
    @app.get('/login')
    def user_login_get(form: LoginForm = None):
        form = form or LoginForm()
        return render_template('login.html', form=form)
        
    @app.post('/login')
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
            return redirect(url_for('user_dashboard'))
        
        form.username.errors.append('Invalid username or password')
        
        return user_login_get(form=form)

        #return render_template('login.html', form=form)


    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/dashboard', methods=['GET'])
    @login_required
    def user_dashboard():
        return render_template('dashboard.html')

        
    @app.route("/dashboard/calculation-results")
    @app.route("/dashboard/calculation-results/<int:page>")
    @login_required
    def user_calculation_results(page=1):
        query = (
            db.select(CalculationResult)
            #.where(CalculationResult.user_id == current_user.id)
            .order_by(CalculationResult.id.desc())
        )
        query = paginate(query, page=page, per_page=20)
    
        results = db.session.scalars(query).all()
    
        return render_template("calculation_results.html", results=results)


    @app.route("/task/estimate-pi/<int:samples>")
    @login_required
    def user_estimate_pi(samples):
        workflow = chain(
                compute_heavy_data.s(samples), 
                store_result_to_db.s(user_id=current_user.id)
            )
        # (result of each function will be passed to thefirst argument of the next one)
 
        workflow.apply_async()
        return jsonify({"message": "Pipeline started"})


    @app.get("/task/generate-random/<int:maximum>")
    def start_task(maximum):
        result = random_number.delay(maximum)

        return jsonify({
            "task_id": result.id,
            "state": result.state
        })


    @app.get("/task/result/<task_id>")
    def get_task(task_id):
        result = AsyncResult(task_id, app=celery)

        if result.ready():
            return jsonify({
                "state": result.state,
                "result": result.get()
            })

        return jsonify({
            "state": result.state
        })