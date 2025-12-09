import os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv 

#Cargar las variables de entorno
load_dotenv()

#crear instancia
app =  Flask(__name__)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo Categoría
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

# Modelo Post
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    category = db.relationship('Category', backref=db.backref('posts', lazy=True))

# Lista de categorías que quieres insertar
default_categories = ['Deportes', 'Tecnología', 'Política', 'Economía', 'Cultura']

# Crear las tablas si no existen (ya lo tienes)
with app.app_context():
    db.create_all()

    # Iterar sobre las categorías predefinidas
    for cat_name in default_categories:
        # 1. Intentar encontrar la categoría por nombre
        existing_category = Category.query.filter_by(name=cat_name).first()

        # 2. Si la categoría NO existe, la creamos e insertamos
        if existing_category is None:
            new_category = Category(name=cat_name)
            db.session.add(new_category)
            print(f"✅ Categoría '{cat_name}' insertada.")
        else:
            # 3. Si ya existe, la ignoramos y mostramos un mensaje (opcional)
            print(f"⚠️ Categoría '{cat_name}' ya existe, se omite.")

    # 4. Confirmar los cambios en la base de datos (solo si hubo inserciones)
    db.session.commit()
    print("✨ Proceso de inserción de categorías completado.")

# Ruta para ver todos los posts
@app.route('/')
def index():
    posts = Post.query.all()
    categories = Category.query.all()
    return render_template('index.html', posts=posts, categories=categories)

#Ruta /post crear un nuevo post
@app.route('/post/new', methods=['GET','POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category_id = request.form.get('category_id')
        new_post = Post(title=title, content=content, category_id=category_id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('index'))
    
    #Aqui sigue si es GET
    categories = Category.query.all()
    return render_template('create_post.html', categories=categories)

if __name__ == '__main__':
    app.run(debug=True)