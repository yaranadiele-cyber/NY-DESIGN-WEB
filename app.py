import os
import sqlite3
from flask import Flask, render_template, request, redirect, session
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# ===== Variáveis de Ambiente =====
load_dotenv()

cloudinary.config(
    cloud_name=os.environ.get("CLOUD_NAME"),
    api_key=os.environ.get("API_KEY"),
    api_secret=os.environ.get("API_SECRET")
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ny_design_ultra_secure")

DATABASE = "database.db"

# ================= BANCO =================
def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

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

    c.execute("""
    CREATE TABLE IF NOT EXISTS servicos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        valor TEXT,
        imagem TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS portfolio(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imagem TEXT,
        link TEXT
    )
    """)

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
    conn = get_connection()

    config = conn.execute("SELECT * FROM config WHERE id=1").fetchone()
    servicos = conn.execute("SELECT * FROM servicos").fetchall()
    portfolio = conn.execute("SELECT * FROM portfolio").fetchall()
    depoimentos = conn.execute("SELECT * FROM depoimentos").fetchall()

    conn.close()

    return render_template("index.html",
                           config=config,
                           servicos=servicos,
                           portfolio=portfolio,
                           depoimentos=depoimentos)

# ================= DEPOIMENTO =================
@app.route("/enviar-depoimento", methods=["POST"])
def enviar_depoimento():
    conn = get_connection()
    conn.execute("""
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

# ================= ADMIN =================
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if "admin" not in session:
        return redirect("/login")

    conn = get_connection()

    if request.method == "POST":

        # ===== ADICIONAR SERVIÇO =====
        if "add_servico" in request.form:
            imagem = request.files.get("imagem")
            url_img = ""
            if imagem and imagem.filename:
                try:
                    upload = cloudinary.uploader.upload(imagem)
                    url_img = upload.get("secure_url")
                except:
                    url_img = ""

            conn.execute("""
                INSERT INTO servicos(nome,descricao,valor,imagem)
                VALUES(?,?,?,?)
            """, (
                request.form.get("nome"),
                request.form.get("descricao"),
                request.form.get("valor"),
                url_img
            ))
            conn.commit()

        # ===== ATUALIZAR SERVIÇO =====
        elif "update_servico" in request.form:
            id = request.form.get("id")
            imagem = request.files.get("imagem")

            if imagem and imagem.filename:
                upload = cloudinary.uploader.upload(imagem)
                url_img = upload.get("secure_url")
                conn.execute("""
                    UPDATE servicos
                    SET nome=?, descricao=?, valor=?, imagem=?
                    WHERE id=?
                """, (
                    request.form.get("nome"),
                    request.form.get("descricao"),
                    request.form.get("valor"),
                    url_img,
                    id
                ))
            else:
                conn.execute("""
                    UPDATE servicos
                    SET nome=?, descricao=?, valor=?
                    WHERE id=?
                """, (
                    request.form.get("nome"),
                    request.form.get("descricao"),
                    request.form.get("valor"),
                    id
                ))
            conn.commit()

        # ===== EXCLUIR SERVIÇO =====
        elif "delete_servico" in request.form:
            conn.execute("DELETE FROM servicos WHERE id=?",
                         (request.form.get("id"),))
            conn.commit()

        # ===== ADICIONAR PORTFOLIO =====
        elif "add_portfolio" in request.form:
            imagem = request.files.get("imagem")
            url_img = ""
            if imagem and imagem.filename:
                upload = cloudinary.uploader.upload(imagem)
                url_img = upload.get("secure_url")

            conn.execute("""
                INSERT INTO portfolio(imagem,link)
                VALUES(?,?)
            """, (url_img, request.form.get("link")))
            conn.commit()

        # ===== ATUALIZAR PORTFOLIO =====
        elif "update_portfolio" in request.form:
            id = request.form.get("id")
            imagem = request.files.get("imagem")

            if imagem and imagem.filename:
                upload = cloudinary.uploader.upload(imagem)
                url_img = upload.get("secure_url")
                conn.execute("""
                    UPDATE portfolio SET imagem=?, link=? WHERE id=?
                """, (url_img, request.form.get("link"), id))
            else:
                conn.execute("""
                    UPDATE portfolio SET link=? WHERE id=?
                """, (request.form.get("link"), id))
            conn.commit()

        # ===== EXCLUIR PORTFOLIO =====
        elif "delete_portfolio" in request.form:
            conn.execute("DELETE FROM portfolio WHERE id=?",
                         (request.form.get("id"),))
            conn.commit()

        # ===== ATUALIZAR DEPOIMENTO =====
        elif "update_depoimento" in request.form:
            conn.execute("""
                UPDATE depoimentos
                SET nome=?, texto=?, estrelas=?
                WHERE id=?
            """, (
                request.form.get("nome"),
                request.form.get("texto"),
                request.form.get("estrelas"),
                request.form.get("id")
            ))
            conn.commit()

        # ===== EXCLUIR DEPOIMENTO =====
        elif "delete_depoimento" in request.form:
            conn.execute("DELETE FROM depoimentos WHERE id=?",
                         (request.form.get("id"),))
            conn.commit()

        # ===== CONFIGURAÇÕES =====
        elif "update_config" in request.form:
            logo = request.files.get("logo")

            if logo and logo.filename:
                upload = cloudinary.uploader.upload(logo)
                conn.execute("UPDATE config SET logo=? WHERE id=1",
                             (upload.get("secure_url"),))

            conn.execute("""
                UPDATE config SET
                titulo=?,
                whatsapp=?,
                instagram=?,
                facebook=?,
                cor=?,
                logo_texto=?
                WHERE id=1
            """, (
                request.form.get("titulo"),
                request.form.get("whatsapp"),
                request.form.get("instagram"),
                request.form.get("facebook"),
                request.form.get("primary_color"),
                request.form.get("logo_texto")
            ))
            conn.commit()

        elif "delete_logo" in request.form:
            conn.execute("UPDATE config SET logo='' WHERE id=1")
            conn.commit()

        elif "reset_config" in request.form:
            conn.execute("""
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

    config = conn.execute("SELECT * FROM config WHERE id=1").fetchone()
    servicos = conn.execute("SELECT * FROM servicos").fetchall()
    portfolio = conn.execute("SELECT * FROM portfolio").fetchall()
    depoimentos = conn.execute("SELECT * FROM depoimentos").fetchall()
    conn.close()

    return render_template("admin.html",
                           config=config,
                           servicos=servicos,
                           portfolio=portfolio,
                           depoimentos=depoimentos)


if __name__ == "__main__":
    app.run(debug=True)