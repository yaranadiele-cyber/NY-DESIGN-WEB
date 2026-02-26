from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "ny_design_ultra_secure"

if not os.path.exists("static/uploads"):
    os.makedirs("static/uploads")

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================= BANCO =================
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # CONFIG
    c.execute("""
    CREATE TABLE IF NOT EXISTS config(
        id INTEGER PRIMARY KEY,
        titulo TEXT,
        whatsapp TEXT,
        instagram TEXT,
        facebook TEXT,
        cor TEXT,
        logo TEXT,
        logo_texto TEXT
    )
    """)

    c.execute("""
    INSERT OR IGNORE INTO config
    (id,titulo,whatsapp,instagram,facebook,cor,logo,logo_texto)
    VALUES
    (1,'N Design Web Premium','5599999999999','','','#c9a063','','NY DESIGN')
    """)

    # SERVIÇOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS servicos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        valor TEXT,
        imagem TEXT
    )
    """)

    # PORTFÓLIO
    c.execute("""
    CREATE TABLE IF NOT EXISTS portfolio(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imagem TEXT,
        link TEXT
    )
    """)

    # DEPOIMENTOS
    c.execute("""
    CREATE TABLE IF NOT EXISTS depoimentos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        texto TEXT,
        estrelas INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= SITE =================
@app.route("/")
def index():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    config = c.execute("SELECT * FROM config WHERE id=1").fetchone()
    servicos = c.execute("SELECT * FROM servicos").fetchall()
    portfolio = c.execute("SELECT * FROM portfolio").fetchall()
    depoimentos = c.execute("SELECT * FROM depoimentos").fetchall()

    conn.close()

    return render_template("index.html",
                           config=config,
                           servicos=servicos,
                           portfolio=portfolio,
                           depoimentos=depoimentos)

# ================= ENVIAR DEPOIMENTO =================
@app.route("/enviar-depoimento", methods=["POST"])
def enviar_depoimento():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO depoimentos(nome,texto,estrelas)
    VALUES(?,?,?)
    """, (
        request.form["nome"],
        request.form["texto"],
        request.form["estrelas"]
    ))

    conn.commit()
    conn.close()

    return redirect("/")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["pass"] == "1234":
            session["admin"] = True
            return redirect("/admin")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" not in session:
        return redirect("/login")

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    config = c.execute("SELECT * FROM config WHERE id=1").fetchone()

    if request.method == "POST":

        # ================= ADICIONAR SERVIÇO =================
        if "add_servico" in request.form:

            imagem = request.files["imagem"]
            nome_img = ""

            if imagem and imagem.filename != "":
                nome_img = secure_filename(imagem.filename)
                imagem.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_img))

            c.execute("""
                INSERT INTO servicos(nome,descricao,valor,imagem)
                VALUES(?,?,?,?)
            """, (
                request.form["nome"],
                request.form["descricao"],
                request.form["valor"],
                nome_img
            ))
            conn.commit()

        # ================= ADICIONAR PORTFÓLIO =================
        elif "add_portfolio" in request.form:

            imagem = request.files["imagem"]
            nome_img = ""

            if imagem and imagem.filename != "":
                nome_img = secure_filename(imagem.filename)
                imagem.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_img))

            c.execute("""
                INSERT INTO portfolio(imagem,link)
                VALUES(?,?)
            """, (
                nome_img,
                request.form["link"]
            ))
            conn.commit()

        # ================= EXCLUIR LOGO =================
        elif "delete_logo" in request.form:

            if config["logo"]:
                caminho = os.path.join(app.config["UPLOAD_FOLDER"], config["logo"])
                if os.path.exists(caminho):
                    os.remove(caminho)

            c.execute("UPDATE config SET logo='' WHERE id=1")
            conn.commit()

        # ================= RESET CONFIG =================
        elif "reset_config" in request.form:

            c.execute("""
                UPDATE config SET
                titulo='N Design Web Premium',
                whatsapp='',
                instagram='',
                facebook='',
                cor='#c9a063',
                logo='',
                logo_texto='NY DESIGN'
                WHERE id=1
            """)
            conn.commit()

        # ================= ATUALIZAR CONFIG =================
        elif "update_config" in request.form:

            logo = request.files["logo"]

            if logo and logo.filename != "":
                nome_logo = secure_filename(logo.filename)
                logo.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_logo))
                c.execute("UPDATE config SET logo=? WHERE id=1", (nome_logo,))

            c.execute("""
                UPDATE config SET
                titulo=?,
                whatsapp=?,
                instagram=?,
                facebook=?,
                cor=?,
                logo_texto=?
                WHERE id=1
            """, (
                request.form["titulo"],
                request.form["whatsapp"],
                request.form["instagram"],
                request.form["facebook"],
                request.form["primary_color"],
                request.form["logo_texto"]
            ))
            conn.commit()

    # Recarrega dados
    config = c.execute("SELECT * FROM config WHERE id=1").fetchone()
    servicos = c.execute("SELECT * FROM servicos").fetchall()
    portfolio = c.execute("SELECT * FROM portfolio").fetchall()
    depoimentos = c.execute("SELECT * FROM depoimentos").fetchall()

    conn.close()

    return render_template("admin.html",
                           config=config,
                           servicos=servicos,
                           portfolio=portfolio,
                           depoimentos=depoimentos)

        # ================= EXCLUIR LOGO =================
        if "delete_logo" in request.form:
            if config["logo"]:
                caminho = os.path.join(app.config["UPLOAD_FOLDER"], config["logo"])
                if os.path.exists(caminho):
                    os.remove(caminho)

            c.execute("UPDATE config SET logo='' WHERE id=1")
            conn.commit()

        # ================= RESET CONFIG =================
        elif "reset_config" in request.form:
            c.execute("""
            UPDATE config SET
            titulo='N Design Web Premium',
            whatsapp='',
            instagram='',
            facebook='',
            cor='#c9a063',
            logo='',
            logo_texto='NY DESIGN'
            WHERE id=1
            """)
            conn.commit()

        # ================= ATUALIZAR CONFIG =================
        elif "update_config" in request.form:

            logo = request.files["logo"]

            if logo and logo.filename != "":
                nome_logo = secure_filename(logo.filename)
                logo.save(os.path.join(app.config["UPLOAD_FOLDER"], nome_logo))
                c.execute("UPDATE config SET logo=? WHERE id=1", (nome_logo,))

            c.execute("""
            UPDATE config SET
            titulo=?,
            whatsapp=?,
            instagram=?,
            facebook=?,
            cor=?,
            logo_texto=?
            WHERE id=1
            """, (
                request.form["titulo"],
                request.form["whatsapp"],
                request.form["instagram"],
                request.form["facebook"],
                request.form["primary_color"],
                request.form["logo_texto"]
            ))

            conn.commit()

    # Recarrega dados após alterações
    config = c.execute("SELECT * FROM config WHERE id=1").fetchone()
    servicos = c.execute("SELECT * FROM servicos").fetchall()
    portfolio = c.execute("SELECT * FROM portfolio").fetchall()
    depoimentos = c.execute("SELECT * FROM depoimentos").fetchall()

    conn.close()

    return render_template("admin.html",
                           config=config,
                           servicos=servicos,
                           portfolio=portfolio,
                           depoimentos=depoimentos)

if __name__ == "__main__":
    app.run()