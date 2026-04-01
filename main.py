from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "secreto123"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# =====================
# MODELOS
# =====================

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500))
    response = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# =====================
# LOGIN
# =====================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# =====================
# RUTAS
# =====================

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/chatbot")
@login_required
def chatbot():
    mensajes = Message.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", mensajes=mensajes)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if not user:
            return "❌ Usuario no existe"

        if not check_password_hash(user.password, password):
            return "❌ Contraseña incorrecta"

        login_user(user)
        return redirect(url_for("chatbot"))

    return render_template("login.html")

    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        hashed_password = generate_password_hash(request.form["password"])

        user = User(
            username=request.form["username"],
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/clear")
@login_required
def clear():
    Message.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return redirect(url_for("home"))

# =====================
# CHAT
# =====================

@app.route("/chat", methods=["POST"])
@login_required
def chat():
    texto = request.json.get("mensaje", "").lower()

    if "html" in texto:
        respuesta = "HTML crea la estructura de una página web."
    elif "css" in texto:
        respuesta = "CSS da estilo."
    elif "javascript" in texto:
        respuesta = "JavaScript hace la web interactiva."
    elif "primer codigo" in texto:
        respuesta = "Tu primer còdigo puede ser:" \
        "print('Hello world')"
    elif "error" in texto:
        respuesta = "Los errores son respuestas que te da la consola cuando algo esta mal o no cuadra en el codigo"
    elif "Unity" in texto:
        respuesta = "Unity si bien no es un lenguaje de programaciòn, es una plataforma en donde puedes crear juegos son c#"
    elif "sistema operativo para programaciòn" in texto:
        respuesta = "El sistema operativo va a depender mucho de tu gusto, si tu quieres un sistema libre, usa linux, si quieres uno facil de manejar y para principiantes, usa windows" 
    elif "I.A" in texto:
        respuesta = "Una I.A es un bot que te puede decir cualquier duda que tengas o en este caso, una ayuda en la programaciòn"   
    
    elif "hola" in texto:
        respuesta = f"Hola {current_user.username} 👋"
    else:
        respuesta = "No entiendo todavía 🤖"

    msg = Message(text=texto, response=respuesta, user_id=current_user.id)
    db.session.add(msg)
    db.session.commit()

    return jsonify({"respuesta": respuesta})

# =====================
# INICIAR
# =====================

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
