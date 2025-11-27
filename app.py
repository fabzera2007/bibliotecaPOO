# app.py
from flask import Flask, render_template, request, redirect
from sistema import *

app = Flask(__name__)
biblioteca = Biblioteca()

@app.route("/")
def home():
    return render_template("index.html")

# CADASTRO
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if request.method == "POST":
        tipo = request.form.get("tipo")
        if tipo == "leitor":
            nome = request.form.get("nome") or "Sem Nome"
            cpf = request.form.get("cpf") or ""
            leitor = Leitor(nome, cpf)
            biblioteca.adicionar_leitor(leitor)
        elif tipo == "funcionario":
            nome = request.form.get("nome") or "Sem Nome"
            cpf = request.form.get("cpf") or ""
            cargo = request.form.get("cargo") or ""
            func = Funcionario(nome, cpf, cargo)
            biblioteca.adicionar_funcionario(func)
        elif tipo == "livro":
            titulo = request.form.get("titulo") or "Sem Título"
            autor = request.form.get("autor") or ""
            isbn = request.form.get("isbn") or f"ISBN-{random.randint(1000,9999)}"
            # precisa existir funcionario para cadastrar via funcionario, se não houver, adiciona direto
            if biblioteca.funcionarios:
                primeiro = next(iter(biblioteca.funcionarios.values()))
                primeiro.cadastrar_livro(biblioteca, Livro(titulo, autor, isbn))
            else:
                biblioteca.adicionar_livro(Livro(titulo, autor, isbn))
        elif tipo == "referencia":
            titulo = request.form.get("titulo") or "Sem Título"
            autor = request.form.get("autor") or ""
            isbn = request.form.get("isbn") or f"ISBN-{random.randint(1000,9999)}"
            if biblioteca.funcionarios:
                primeiro = next(iter(biblioteca.funcionarios.values()))
                primeiro.cadastrar_livro(biblioteca, LivroReferencia(titulo, autor, isbn))
            else:
                biblioteca.adicionar_livro(LivroReferencia(titulo, autor, isbn))
        return redirect("/")
    return render_template("cadastrar.html")

# LOCAÇÃO
@app.route("/locar", methods=["GET", "POST"])
def locar():
    if request.method == "POST":
        mat = request.form.get("matricula")
        isbn = request.form.get("isbn")
        leitor = biblioteca.encontrar_leitor(mat)
        livro = biblioteca.encontrar_livro(isbn)
        func = next(iter(biblioteca.funcionarios.values())) if biblioteca.funcionarios else None
        if not (leitor and livro and func):
            # simples redirect sem mensagens pra não complicar
            return redirect("/status")
        loc, err = func.registrar_locacao(leitor, livro)
        if loc:
            biblioteca.locacoes.append(loc)
        return redirect("/status")
    return render_template("locar.html")

# DEVOLUÇÃO
@app.route("/devolver", methods=["GET", "POST"])
def devolver():
    if request.method == "POST":
        mat = request.form.get("matricula")
        isbn = request.form.get("isbn")
        data_real_str = request.form.get("data_real")
        data_real = parse_date(data_real_str) if data_real_str else date.today()
        leitor = biblioteca.encontrar_leitor(mat)
        registro_encontrado = None
        for loc in biblioteca.locacoes:
            if loc.leitor.matricula == mat and loc.livro.isbn == isbn and not loc.livro.disponivel:
                registro_encontrado = loc
                break
        if registro_encontrado and leitor:
            multa = leitor.devolver_livro(registro_encontrado, data_real)
        return redirect("/status")
    return render_template("devolver.html")

# STATUS
@app.route("/status")
def status():
    leitores = list(biblioteca.leitores.values())
    livros = list(biblioteca.livros.values())
    locs = [loc for loc in biblioteca.locacoes if not loc.livro.disponivel]
    return render_template("status.html", leitores=leitores, livros=livros, locacoes=locs)

if __name__ == "__main__":
    app.run(debug=True)
