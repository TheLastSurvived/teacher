from flask import Flask, render_template, request, flash, redirect, session, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from hashlib import md5
from  sqlalchemy.sql.expression import func
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqlamodel import ModelView
from flask_admin import Admin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
app.config['UPLOAD_FOLDER'] = 'static/img/upload'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
db = SQLAlchemy(app)
ckeditor = CKEditor(app)


class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100))
    surname = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), unique=True)
    root = db.Column(db.Integer, default=0)
   
    def __repr__(self):
        return 'User %r' % self.id 


class Articles(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100))
    date = db.Column(db.DateTime, default=datetime.now)
    text = db.Column(db.Text)
    image_name = db.Column(db.String(100))
    category = db.Column(db.String(100))

    def __repr__(self):
        return 'Articles %r' % self.id 


class Teachers(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    desciption = db.Column(db.Text)
    price = db.Column(db.Integer)
    subject = db.Column(db.String(100))
    image_name = db.Column(db.String(100))
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Integer, default=0)
   
    def __repr__(self):
        return 'Teachers %r' % self.id 


class Orders(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('users.id'))
    id_teacher = db.Column(db.Integer, db.ForeignKey('teachers.id'))

    def __repr__(self):
        return 'Orders %r' % self.id 


class AdminIndex(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if 'name' in session:
            user = Users.query.filter_by(email=session['name']).first()
            if user.root!=1:
                abort(403)
            else:
                return self.render('admin/dashboard_index.html')
        else:
            abort(401)


admin = Admin(app, name='Teacher', template_mode='bootstrap3',index_view=AdminIndex())

class OrdersView(ModelView):
    column_display_pk = True 
    column_hide_backrefs = False
    column_list = ['id','id_user','id_teacher']
    
    
class TeachersView(ModelView):
    column_display_pk = True 
    column_hide_backrefs = False
    column_list = ['id','desciption','price','subject','image_name','id_user']
    

admin.add_view(ModelView(Users, db.session))
admin.add_view(ModelView(Articles, db.session))
admin.add_view(TeachersView(Teachers, db.session))
admin.add_view(OrdersView(Orders, db.session))


@app.route('/', methods=['GET', 'POST'])
def index():
    teachers = Teachers.query.all()
    
    users_ids = []
    for teacher in teachers:
        users_ids.append(teacher.id_user)
        
    users_list = []
    for id in users_ids:
        users_list.append(Users.query.get(id))
        
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        subject = request.form.get('category')
        price = request.form.get('price')
        desciption = request.form.get('ckeditor')
        image = request.files['image']
        filename = secure_filename(image.filename)
        pic_name = str(uuid.uuid4()) + "_" + filename
        image.save("static/img/upload/" + pic_name)
        teacher = Teachers(name=name,surname=surname,price=price, subject=subject,desciption=desciption,image_name=pic_name)
        db.session.add(teacher)
        db.session.commit()
        flash("Запись добавлена!", category="ok")
        return redirect(url_for("index"))

    if request.method == 'GET':
        subject = request.args.get('subject')
        if subject:
            subject= subject.capitalize()
            subject = "%{}%".format(subject)
            teachers = Teachers.query.filter(Teachers.subject.like(subject)).all()
            return render_template("index.html",zip=zip,teachers=teachers,users_list=users_list)
        else:
             return render_template("index.html",zip=zip,teachers=teachers,users_list=users_list)

    return render_template("index.html",zip=zip,teachers=teachers,users_list=users_list)


@app.route('/add_teacher/<int:id_user>', methods=['GET', 'POST'])
def add_teacher(id_user):
    if not 'name' in session:
        abort(401)
    total_user = Users.query.filter_by(id=id_user).first()
    total_user.root = 2
    if request.method == 'POST':
        subject = request.form.get('category')
        price = request.form.get('price')
        desciption = request.form.get('ckeditor')
        image = request.files['image']
        filename = secure_filename(image.filename)
        pic_name = str(uuid.uuid4()) + "_" + filename
        image.save("static/img/upload/" + pic_name)
        teacher = Teachers(price=price, subject=subject,desciption=desciption,image_name=pic_name,id_user=total_user.id)
        db.session.add(teacher)
        db.session.commit()
        flash("Запись добавлена!", category="ok")
    return redirect(url_for("profile"))


@app.route('/about', methods=['GET', 'POST'])
def about():
    return render_template("about.html")


@app.route('/article/<int:id>', methods=['GET', 'POST'])
def article(id):
    
    article = Articles.query.get(id)
    articles_random = Articles.query.filter(Articles.id!=article.id).order_by(func.random()).limit(3).all()

    if request.method == 'POST':
        article.title = request.form.get('title')
        article.category = request.form.get('category')
        article.text = request.form.get('ckeditor')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save("static/img/upload/" + pic_name)
            article.image_name = pic_name
        db.session.commit()
        flash("Запись обновлена!", category="ok")
        return redirect(url_for("article", id=article.id))

    return render_template("article.html",article=article,articles_random=articles_random)


@app.route('/blog', methods=['GET', 'POST'])
def blog():
    articles = Articles.query.order_by(Articles.date.desc()).all()
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        text = request.form.get('ckeditor')
        image = request.files['image']
        
        filename = secure_filename(image.filename)
        pic_name = str(uuid.uuid4()) + "_" + filename
        image.save("static/img/upload/" + pic_name)

        article = Articles(title=title, category=category,text=text,image_name=pic_name)
        db.session.add(article)
        db.session.commit()
        flash("Запись добавлена!", category="ok")
        return redirect(url_for("blog"))

    if request.method == 'GET':
        category = request.args.get('category')
        if category:
            category= category.capitalize()
            category = "%{}%".format(category)
            articles = Articles.query.filter(Articles.category.like(category)).all()
            return render_template("blog.html",articles=articles)
        else:
             return render_template("blog.html",articles=articles)

    return render_template("blog.html",articles=articles)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not 'name' in session:
        abort(401)
   
    total_user = Users.query.filter_by(email=session['name']).first()
    
    id_list = []
    teacher_list = []
    teacher = object
    orders_teacher = []
    
    
    
    total_user = Users.query.filter_by(email=session['name']).first()
    orders = Orders.query.filter_by(id_user=total_user.id).all()
    
    
    teacher = Teachers.query.filter_by(id_user=total_user.id).first()
    if teacher:
        orders_teacher = Orders.query.filter_by(id_teacher=teacher.id).all()
    
    student_list = []
    
    for el in orders_teacher:
        student_list.append(Users.query.get(el.id_user))
    
    for order in orders:
        id_list.append(order.id_teacher)

    for el in id_list:
        teacher_list.append(Teachers.query.filter_by(id=el).first())
        
    user_list = []
    
    for el in teacher_list:
        user_list.append(Users.query.filter_by(id=el.id_user).first())
        
   

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = md5(request.form.get('password').encode()).hexdigest()
        total_user.name = name
        total_user.email = email
        total_user.password =password
        db.session.commit()
        flash("Профиль обновлен!", category="ok")
        return redirect(url_for("profile"))
    return render_template("profile.html",teacher_list=teacher_list,teacher=teacher,user_list=user_list,student_list=student_list,zip=zip)


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('name', None)
    if request.method == 'POST':
        email = request.form.get('email')
        password = md5(request.form.get('password').encode()).hexdigest()
        user = Users.query.filter_by(email=email,password=password).first()
        if user:
            session['name'] = Users.query.filter_by(email=email).first().email
            return redirect(url_for("index"))
        else:
            flash("Неправильная почта или пароль!", category="bad")
            return redirect(url_for("login"))
    return render_template("login.html")


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            surname = request.form.get('surname')
            email = request.form.get('email')
            password = request.form.get('password')
            user = Users(name=name,surname=surname,email=email,password=md5(password.encode()).hexdigest())
            db.session.add(user)
            db.session.commit()
            flash("Регистрация прошла успешно!", category="ok")
            return redirect(url_for("reg"))
        except:
            flash("Произошла ошибка! Проверьте введенные данные!", category="bad")
            db.session.rollback()
            return redirect(url_for("reg"))
    return render_template("reg.html")


@app.route('/teacher/<int:id>', methods=['GET', 'POST'])
def teacher(id):
    total_user = object
    orders = object
    id_list = []
    if 'name' in session:
        total_user = Users.query.filter_by(email=session['name']).first()
        orders = Orders.query.filter_by(id_user=total_user.id).all()
        for order in orders:
            id_list.append(order.id_teacher)
    teacher = Teachers.query.get(id)
    user = Users.query.filter_by(id = teacher.id_user).first()
    if request.method == 'POST':
        teacher.subject = request.form.get('category')
        teacher.price = request.form.get('price')
        teacher.desciption = request.form.get('ckeditor')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save("static/img/upload/" + pic_name)
            teacher.image_name = pic_name
        db.session.commit()
        flash("Запись обновлена!", category="ok")
        return redirect(url_for("teacher", id=teacher.id))
    return render_template("teacher.html",teacher=teacher,id_list=id_list,user=user)


@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
     teacher = Teachers.query.get(id)
     if request.method == 'POST':
        teacher.subject = request.form.get('category')
        teacher.price = request.form.get('price')
        teacher.desciption = request.form.get('ckeditor')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            pic_name = str(uuid.uuid4()) + "_" + filename
            image.save("static/img/upload/" + pic_name)
            teacher.image_name = pic_name
        db.session.commit()
        flash("Запись обновлена!", category="ok")
        return redirect(url_for("profile"))


@app.route('/delete-teacher/<int:id>')
def delete_teacher(id):
    obj = Teachers.query.filter_by(id=id).first()
    user = Users.query.filter_by(id=obj.id_user).first()
    orders = Orders.query.filter_by(id_teacher=obj.id).all()
    for el in orders:
        db.session.delete(el)
    user.root = 0
    db.session.delete(obj)
    
    db.session.commit()
    flash("Запись удалена!", category="bad")
    return redirect('/profile')


@app.route('/delete-article/<int:id>')
def delete_article(id):
    obj = Articles.query.filter_by(id=id).first()
    db.session.delete(obj)
    db.session.commit()
    flash("Запись удалена!", category="bad")
    return redirect('/blog')


@app.route('/order/<int:id_teacher>')
def order(id_teacher):
    total_user = Users.query.filter_by(email=session['name']).first()
    order = Orders(id_user=total_user.id, id_teacher=id_teacher)
    db.session.add(order)
    db.session.commit()
    flash("Репетитор заказан!", category="ok")
    return redirect(url_for("teacher", id=id_teacher))


@app.route('/order-delete/<int:id_teacher>')
def order_delete(id_teacher):
    total_user = Users.query.filter_by(email=session['name']).first()
    obj = Orders.query.filter_by(id_user=total_user.id,id_teacher=id_teacher).first()
    db.session.delete(obj)
    db.session.commit()
    flash("Репетитор отменен!", category="bad")
    return redirect(url_for("teacher", id=id_teacher))


@app.route('/logout')
def logout():
    session.pop('name', None)
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidded(e):
    return render_template('403.html'), 403


@app.errorhandler(401)
def forbidded(e):
    return render_template('401.html'), 401


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.context_processor
def inject_user():
    return dict(
    subjects=db.session.query(Teachers.subject).distinct().all(),
    articles_category=db.session.query(Articles.category).distinct().all(),
    )


@app.context_processor
def inject_user():
    def get_user_name():
        if 'name' in session:
            return Users.query.filter_by(email=session['name']).first()
    return dict(active_user=get_user_name())


if __name__ == '__main__':
    app.run(debug=True)