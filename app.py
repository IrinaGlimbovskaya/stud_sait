from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_admin.contrib import fileadmin
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm.exc import NoResultFound
from flask import Blueprint
import re
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPBasicAuth
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime

app = Flask(__name__)
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/D/учеба/Flask/stud_sait/instance/sait.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Указываем страницу входа

# Директория для загрузки фотографий
UPLOAD_FOLDER = 'C:\D\учеба\Flask\stud_sait\static\images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
class Students(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    game_name = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    role = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Students %r>' % self.id_student

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def is_authenticated(self):
        if current_user.is_authenticated:
            print("Пользователь аутентифицирован")
        else:
            print("Пользователь не аутентифицирован")
        return True  # Возвращайте True для аутентифицированных пользователей

    @property
    def user_role(self):
        return self.role




class studweb(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    studies = db.Column(db.Text, nullable=False)
    programm = db.Column(db.Text, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)


class MyAdminView(ModelView):
    column_list = ('id', 'name', 'role','img' ,'studies' ,'programm' ,'course' ,'faculty', 'photo' )  # Список полей, которые вы хотите отображать

    def get_query(self):
            if current_user.is_authenticated:
                print("я в 81 строке")# Проверяем, аутентифицирован ли пользователь
                if current_user.role == 3:  # Если роль пользователя 3
                    student_id = current_user.id
                    return self.session.query(self.model).filter_by(id=student_id)
            print("я в 86 строке")
            return self.session.query(self.model)  # Возвращаем все записи, если пользователь не аутентифицирован или его роль не 3



class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    groups_img = db.Column(db.String(100), nullable=False)
    curator = db.Column(db.String(100), nullable=False)
    curators_description = db.Column(db.String(100), nullable=False)
    curator_img = db.Column(db.String(100), nullable=False)


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(100), nullable=False)
    course = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)


class BullCowUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_name = db.Column(db.String(50), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(50), nullable=False)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(60))
    role = db.Column(db.Integer, nullable=False)


class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)


admin = Admin(app, name='MyAdmin', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Students, db.session))
#admin.add_view(ModelView(studweb, db.session))
admin.add_view(ModelView(Courses, db.session))
admin.add_view(ModelView(Games, db.session))
admin.add_view(MyAdminView(studweb, db.session, name='studweb'))

# Добавление модели источника данных для загрузки файлов
admin.add_view(fileadmin.FileAdmin(UPLOAD_FOLDER, name='Uploads'))
admin_bp = Blueprint('MyAdmin', __name__, url_prefix='/admin')
admin.init_app(admin_bp)

@app.route('/hash_password/<int:student_id>', methods=['GET', 'POST'])
def hash_password(student_id):
    student = Students.query.get(student_id)

    if student:
        if request.method == 'POST':
            new_password = request.form['new_password']
            student.set_password(new_password)
            db.session.commit()
            flash(f"Пароль студента {student_id} успешно хеширован.", 'success')
            return redirect(url_for('index'))  # Замените 'some_route' на ваш роут

        return render_template('change_password.html', student=student)
    else:
        return f"Студент с ID {student_id} не найден."

@auth.verify_password
def verify_password(username, password):
    student = Students.query.filter_by(name=username).first()
    if student and bcrypt.check_password_hash(student.password, password):
        return (True, student.role)
    return False


admin.add_link(MenuLink(name='Logout', category='', url="/logout"))
#admin.add_link(MenuLink(name='Login', category='', url="/login"))

class MyAdminView(BaseView):
    @expose('/')
    def index_view(self):
        student_id = request.args.get('student_id')


# Функция загрузки пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Students.query.get(int(user_id))


# Маршрут логина
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Добавьте проверку, если пользователь уже вошел
    if current_user.is_authenticated:
        flash("Вы уже вошли в систему.", 'info')
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        student = Students.query.filter_by(name=username).first()

        if student and bcrypt.check_password_hash(student.password, password):
            # Проверяем, есть ли у пользователя экземпляр User
            user_instance = Students.query.filter_by(name=username).first()

            if not user_instance:
                # Если экземпляр Students не существует, создаем его
                user_instance = Students(name=username, password=generate_password_hash(password), role=student.role)
                db.session.add(user_instance)
                db.session.commit()

            login_user(user_instance)
            flash("Вход выполнен успешно", 'success')

            if student.role == 1:
                return redirect(url_for('admin.index'))
            elif student.role == 2:
                return redirect(url_for('students.index_view'))
            elif student.role == 3:
                student_id = student.id
                return redirect(url_for('studweb.index_view', student_id=student_id))
                # Получаем запрос на получение количества записей из базы данных
                #query = super(student).get_count_query()
                # Фильтруем записи по текущему пользователю (студенту)

                #return redirect(url_for('MyAdmin.students.index_view', username=username))

        else:
            flash("Неправильное имя пользователя или пароль", 'error')
            return render_template('login.html')

    return render_template('login.html')



@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы.")
    return redirect(url_for('login'))


# Маршрут админки
@app.route('/admin')
@login_required
def admin():
    if current_user.role != 1:  # Если у пользователя нет админских прав
        flash("У вас нет доступа к этой странице.", 'error')
        return redirect(url_for('login'))

    return redirect(url_for('admin'))


def generate_secret_number():
    # Генерируем случайное число из четырех цифр
    first_digit = random.randint(1, 9)  # Генерируем первую цифру от 1 до 9
    rest_of_digits = ''.join([str(random.randint(0, 9)) for _ in range(3)])  # Генерируем остальные три цифры
    secret_number = str(first_digit) + rest_of_digits
    return secret_number


@app.route('/')
@app.route('/home')
def index():
    students = Students.query.order_by(Students.id.asc()).all()
    # Извлекаем все группы из базы данных
    groups = Courses.query.order_by(Courses.id.asc()).all()

    # Передаем группы в шаблон
    return render_template("index.html", groups=groups)


@app.route('/ListOfGroups')
def ListOfGroups():
    # Извлекаем все группы из базы данных
    groups = Courses.query.order_by(Courses.id.asc()).all()

    return render_template("ListOfGroups.html", groups=groups)

@app.route('/Contacts')
def Contacts():
    return render_template("Contacts.html",)
@app.route('/base')
def base():
    return render_template("base.html",)

@app.route('/course<int:id>', methods=['POST', 'GET'] )
def course(id):
    courses = Courses.query.order_by(Courses.id.asc()).all()  # по id вывести группу
    #print(courses)
    course = Courses.query.filter_by(id=id).first()

    #print(course.id)
    #for el in courses:
        #print(el.course)
    groups = Courses.query.with_entities(Courses.id, Courses.name).all()
    #print(groups)
    students = Students.query.order_by(Students.id.asc()).all()
    #for el in students:
        #print(el.course)
    games = Courses.query.with_entities(Games.img, Games.name, Games.path).all()
    #print(games)
    # Извлекаем значения поля Name из объектов Courses
    names = [course.name for course in courses]

    return render_template("course_page.html", students=students, course=course, groups=groups, games=games, courses=courses )

@app.route('/List')
def List():
    return render_template("List.html")


@app.route('/diplom')
def Diplom():
    return render_template("Diplom.html")


@app.route('/kursovaya')
def Kursovaya():
    return render_template("Kursovaya.html")


# @app.route('/list_group')
# def index():
#    courses = Courses.query.order_by(Courses.id.asc()).all()  # по id вывести группу
#     print(courses)
#     course = Courses.query.filter_by(id=id).first()
#     print(course.id)
#     # Извлекаем значения поля Name из объектов Courses
#     names = [course.name for course in courses]
#
#     # Передаем группы в шаблон
#     return render_template("index.html", names=names)

# @app.route('/kurs<int:id_student>')
# def kurs3():
# return render_template("3kurs.html")


# @app.route('/kurs<int:id>', methods=['POST', 'GET'])
# def kurs_page(id):
#     courses = Courses.query.order_by(Courses.id.asc()).all()  # по id вывести группу
#     print(courses)
#     course = Courses.query.filter_by(id=id).first()
#     print(course.id)
#     for el in courses:
#         print(el.course)
#     groups = Courses.query.with_entities(Courses.id, Courses.name).all()
#     print(groups)
#     students = Students.query.order_by(Students.id.asc()).all()
#     for el in students:
#         print(el.course)
#     games = Courses.query.with_entities(Games.img, Games.name, Games.path).all()
#     print(games)
#     # Извлекаем значения поля Name из объектов Courses
#     names = [course.name for course in courses]
#
#     return render_template("kurs_page.html", students=students, course=course, groups=groups, games=games, courses=courses )


@app.route('/students_web/<int:id>')
def students_web(id):
    try:
        student = db.session.query(studweb).filter_by(id=id).one()
        programm_sentences = re.findall(r'([А-ЯA-Z].*?[.!?])', student.programm)
        studies_sentences = re.findall(r'([А-ЯA-Z].*?[.!?])', student.studies)
        groups = Courses.query.with_entities(Courses.id, Courses.name).all()

        print("Programm Sentences:", programm_sentences)
        print("Studies Sentences:", studies_sentences)

        return render_template("students_web.html", student=student, programm_sentences=programm_sentences,
                               studies_sentences=studies_sentences, groups=groups)
    except NoResultFound:
        # Handle the case where the student with the given id is not found.
        # You can return an error page or a 404 Not Found response.
        return render_template("student_not_found.html")


@app.route('/bull_cow_log', methods=['GET', 'POST'])
def bull_cow_log():
    if request.method == 'POST':
        player_name = request.form.get('playerName')
        number = request.form.get('guessNumber')
        secret_number = generate_secret_number()
        session['secret_number'] = secret_number

        return redirect(url_for('bull_cow', player_name=player_name, number=number))
    return render_template('index_bull_cow.htm')


@app.route('/guess_num', methods=['GET', 'POST'])
def guess_num():
    if request.method == 'POST':
        player_name = request.form.get('playerName')
        number = request.form.get('guessNumber')
        secret_number = generate_secret_number()
        session['secret_number'] = secret_number
        new_record = BullCowUser(player_name=player_name, number=number)
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('bull_cow', player_name=player_name, number=number))
    return render_template('index_end.htm')


@app.route('/bull_cow/<player_name>/<number>', methods=['GET'])
def bull_cow(player_name, number):
    #global attempts_count  # Объявляем, что мы будем использовать глобальный счетчик
    if 'attempts_count' not in session:
        session['attempts_count'] = 1
    else:
        session['attempts_count'] += 1

    attempts_count = session['attempts_count']
    if attempts_count > 2:
        session.pop('attempts_count')
        result = 'Вы проиграли!'
        return render_template('bull_cow_restart.html', player_name=player_name)

        # Дополнительные действия при достижении лимита попыток, если нужны
    secret_number = session.get('secret_number')
    print(secret_number)
    bulls, cows = check_guess(number, secret_number)
    result = 'Вы победили!'
    if bulls == 4:  # Все цифры на своих местах
        new_record = BullCowUser(player_name=player_name, number=number, result=result)
        db.session.add(new_record)
        db.session.commit()
        return render_template('bull_cow_congratulations.html', player_name=player_name)
    else:
        return render_template('bull_cow_try_again.html', player_name=player_name, number=number, bulls=bulls,
                               cows=cows, attempts_count=attempts_count)


def check_guess(guess, secret):
    bulls, cows = 0, 0
    for i in range(4):
        if guess[i] == secret[i]:
            bulls += 1
        elif guess[i] in secret:
            cows += 1
    return bulls, cows


@app.route('/about')
def about():
    groups = Courses.query.with_entities(Courses.id, Courses.name).all()
    return render_template("about.html", groups=groups)


if __name__ == "__main__":
    app.run(debug=True,port=5000)

# Проверка аутентификации и роли пользователя перед каждым запросом
@app.before_request
def restrict_access():
    if request.endpoint and "/admin" in request.endpoint:  # Проверяем, что запрос направлен к админке
        if not current_user.is_authenticated:  # Если пользователь не аутентифицирован
            return redirect(url_for('login'))  # Перенаправляем его на страницу входа
        elif current_user.user_role != 1:  # Если у пользователя нет админских прав
            flash("У вас нет доступа к этой странице.", 'error')  # Показываем сообщение об ошибке
            return redirect(url_for('login'))  # Перенаправляем его на страницу входа
