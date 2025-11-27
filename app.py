# app.py (CÓDIGO FINAL E COMPLETO)

from flask import Flask, render_template, request, redirect, url_for
from datetime import date
import random
from sistema import db, Pessoa, Leitor, Funcionario, Livro, LivroReferencia, Locacao, parse_date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def setup_database():
    """Cria todas as tabelas dentro do contexto do app."""
    # Garante que o contexto da aplicação Flask seja carregado para acessar o DB
    with app.app_context(): 
        db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

# CADASTRO
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        tipo = request.form.get("tipo")
        try:
            if tipo == "leitor":
                nome = request.form.get("nome") or "Sem Nome"
                cpf = request.form.get("cpf") or ""
                leitor = Leitor(nome, cpf)
                db.session.add(leitor)
            elif tipo == "funcionario":
                nome = request.form.get("nome") or "Sem Nome"
                cpf = request.form.get("cpf") or ""
                cargo = request.form.get("cargo") or ""
                func = Funcionario(nome, cpf, cargo)
                db.session.add(func)
            elif tipo in ["livro", "referencia"]:
                titulo = request.form.get("titulo") or "Sem Título"
                autor = request.form.get("autor") or ""
                isbn = request.form.get("isbn") or f"ISBN-{random.randint(1000,9999)}"
                if tipo == "referencia":
                    livro = LivroReferencia(titulo, autor, isbn)
                else:
                    livro = Livro(titulo, autor, isbn)
                db.session.add(livro)
            
            db.session.commit()
            return redirect(url_for("home"))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao cadastrar: {e}")
            return redirect(url_for("status"))

    return render_template("cadastrar.html")

# LOCAÇÃO
@app.route("/locar", methods=["GET", "POST"])
def locar():
    if request.method == "POST":
        mat = request.form.get("matricula")
        isbn = request.form.get("isbn")
        
        leitor = Leitor.query.filter_by(matricula=mat).first()
        livro = Livro.query.filter_by(isbn=isbn).first()
        # Encontra o primeiro funcionário para registrar a locação
        func = Funcionario.query.first() 
        
        if not (leitor and livro and func and livro.disponivel):
            return redirect(url_for("status"))
            
        try:
            loc, err = func.registrar_locacao(leitor, livro)
            
            if loc:
                db.session.add(loc)
                db.session.commit()
            return redirect(url_for("status"))
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao locar: {e}")
            return redirect(url_for("status"))
        
    return render_template("locar.html")

# DEVOLUÇÃO
@app.route("/devolver", methods=["GET", "POST"])
def devolver():
    if request.method == "POST":
        mat = request.form.get("matricula")
        isbn = request.form.get("isbn")
        data_real_str = request.form.get("data_real")
        data_real = parse_date(data_real_str) if data_real_str else date.today()
        
        leitor = Leitor.query.filter_by(matricula=mat).first()
        
        registro_encontrado = Locacao.query.join(Livro).filter(
            Locacao.leitor_id == leitor.id if leitor else None, 
            Locacao.livro_isbn == isbn,
            Livro.disponivel == False 
        ).first()

        if registro_encontrado and leitor:
            try:
                leitor.devolver_livro(registro_encontrado, data_real)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Erro ao devolver: {e}")
        
        return redirect(url_for("status"))
        
    return render_template("devolver.html")

# STATUS
@app.route("/status")
def status():
    # As consultas agora devem funcionar
    leitores = Leitor.query.all()
    livros = Livro.query.all()
    locs_ativas = Locacao.query.join(Livro).filter(Livro.disponivel == False).all() 

    # Passa objetos para o template usar com Jinja
    # Algumas expressões no template usam Locacao e Livro; disponibilizamos as classes
    return render_template("status.html", leitores=leitores, livros=livros, locs_ativas=locs_ativas, Locacao=Locacao, Livro=Livro)

if __name__ == "__main__":
    setup_database() # Cria as tabelas na inicialização do script
    app.run(debug=True)