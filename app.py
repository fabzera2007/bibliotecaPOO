# app.py (CÓDIGO FINAL E COMPLETO)

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
import random
from sistema import db, Pessoa, Leitor, Funcionario, Livro, LivroReferencia, Locacao, parse_date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'biblioteca-secret-key-123'
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
                matricula = request.form.get("matricula") or None
                # permite informar matricula opcionalmente
                if matricula:
                    leitor = Leitor(nome, cpf, matricula=matricula)
                else:
                    leitor = Leitor(nome, cpf)
                db.session.add(leitor)
            elif tipo == "funcionario":
                nome = request.form.get("nome") or "Sem Nome"
                cpf = request.form.get("cpf") or ""
                cargo = request.form.get("cargo") or ""
                matricula = request.form.get("matricula") or None
                if matricula:
                    func = Funcionario(nome, cpf, cargo, matricula=matricula)
                else:
                    func = Funcionario(nome, cpf, cargo)
                db.session.add(func)
            elif tipo in ["livro", "referencia"]:
                titulo = request.form.get("titulo") or "Sem Título"
                autor = request.form.get("autor") or ""
                isbn = request.form.get("isbn") or f"ISBN-{random.randint(1000,9999)}"
                if tipo == "referencia":
                    livro = LivroReferencia(titulo=titulo, autor=autor, isbn=isbn)
                else:
                    livro = Livro(titulo=titulo, autor=autor, isbn=isbn)
                db.session.add(livro)
            
            db.session.commit()
            flash("✅ Cadastro realizado com sucesso!", "success")
            return redirect(url_for("home"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Erro ao cadastrar: {str(e)}", "error")
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
        func = Funcionario.query.first() 
        
        if not leitor:
            flash(f"❌ Leitor com matrícula '{mat}' não encontrado.", "error")
        elif not livro:
            flash(f"❌ Livro com ISBN '{isbn}' não encontrado.", "error")
        elif not func:
            flash("❌ Nenhum funcionário cadastrado. Cadastre um funcionário antes de fazer locações.", "error")
        elif not livro.disponivel:
            flash(f"❌ Livro '{livro.titulo}' não está disponível (já foi locado).", "error")
        else:
            try:
                loc, err = func.registrar_locacao(leitor, livro)
                if loc:
                    db.session.add(loc)
                    db.session.commit()
                    flash(f"✅ Locação registrada com sucesso! Livro '{livro.titulo}' para '{leitor.nome}'.", "success")
                else:
                    flash(f"❌ Não foi possível locar: {err}", "error")
            except Exception as e:
                db.session.rollback()
                flash(f"❌ Erro ao locar: {str(e)}", "error")
                print(f"Erro ao locar: {e}")
        
        return redirect(url_for("status"))

    return render_template("locar.html")

# DEVOLUÇÃO
@app.route("/devolver", methods=["GET", "POST"])
def devolver():
    if request.method == "POST":
        # devolve uma locação específica pelo id da locação
        loc_id = request.form.get('locacao_id')
        if loc_id:
            registro = Locacao.query.get(int(loc_id))
            if registro:
                try:
                    if registro.livro.devolver():
                        registro.registrar_devolucao(date.today())
                        db.session.commit()
                        flash(f"✅ Livro '{registro.livro.titulo}' devolvido com sucesso!", "success")
                    else:
                        flash("❌ Erro ao devolver o livro.", "error")
                except Exception as e:
                    db.session.rollback()
                    flash(f"❌ Erro ao devolver: {str(e)}", "error")
                    print(f"Erro ao devolver: {e}")
            else:
                flash("❌ Locação não encontrada.", "error")
        else:
            flash("❌ ID da locação não informado.", "error")
        return redirect(url_for('status'))

    # GET: permite buscar locações por matrícula
    mat = request.args.get('matricula')
    leitor = None
    leitor_locs = []
    if mat:
        leitor = Leitor.query.filter_by(matricula=mat).first()
        if leitor:
            locs = Locacao.query.filter_by(leitor_id=leitor.id).join(Livro).filter(Livro.disponivel == False).all()
            for l in locs:
                days_remaining = (l.data_devolucao_prevista - date.today()).days
                leitor_locs.append({
                    'loc_id': l.id,
                    'livro_title': l.livro.titulo if l.livro else 'Desconhecido',
                    'livro_isbn': l.livro.isbn if l.livro else '',
                    'loc_date': l.data_locacao,
                    'devolucao': l.data_devolucao_prevista,
                    'days_remaining': days_remaining
                })

    return render_template('devolver.html', leitor=leitor, leitor_locs=leitor_locs)

# STATUS
@app.route("/status")
def status():
    leitores = Leitor.query.all()
    livros = Livro.query.all()
    funcionarios = Funcionario.query.all()

    # Locações ativas
    locs_ativas = Locacao.query.join(Livro).filter(Livro.disponivel == False).all()

    # Prepara informações úteis para template
    leitor_counts = {}
    locs_ativas_info = []
    for l in locs_ativas:
        lid = l.leitor_id
        leitor_counts[lid] = leitor_counts.get(lid, 0) + 1
        days_remaining = (l.data_devolucao_prevista - date.today()).days
        locs_ativas_info.append(type('X', (), {
            'leitor_name': l.leitor.nome if l.leitor else 'Desconhecido',
            'livro_title': l.livro.titulo if l.livro else 'Desconhecido',
            'livro_isbn': l.livro.isbn if l.livro else '',
            'devolucao': l.data_devolucao_prevista,
            'days_remaining': days_remaining
        }))

    # busca por matrícula opcional para mostrar locações apenas daquele leitor
    selected_matricula = request.args.get('matricula')
    selected_leitor = None
    selected_locs_info = []
    if selected_matricula:
        selected_leitor = Leitor.query.filter_by(matricula=selected_matricula).first()
        if selected_leitor:
            locs = Locacao.query.filter_by(leitor_id=selected_leitor.id).join(Livro).filter(Livro.disponivel == False).all()
            for l in locs:
                days_remaining = (l.data_devolucao_prevista - date.today()).days
                selected_locs_info.append({
                    'livro_title': l.livro.titulo if l.livro else 'Desconhecido',
                    'livro_isbn': l.livro.isbn if l.livro else '',
                    'loc_date': l.data_locacao,
                    'devolucao': l.data_devolucao_prevista,
                    'days_remaining': days_remaining
                })

    return render_template('status.html', leitores=leitores, funcionarios=funcionarios, livros=livros,
                           locs_ativas_info=locs_ativas_info, leitor_counts=leitor_counts,
                           selected_matricula=selected_matricula, selected_leitor=selected_leitor,
                           selected_locs_info=selected_locs_info)

if __name__ == "__main__":
    setup_database() # Cria as tabelas na inicialização do script
    import os
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
