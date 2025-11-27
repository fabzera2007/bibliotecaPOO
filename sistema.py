# sistema.py
import uuid
from datetime import date, timedelta
import random

# ==============================================================================
# 1. CLASSES BASE E HERANÇA
# ==============================================================================
class Pessoa:
    """Classe base (mãe) para Leitor e Funcionario."""
    def __init__(self, nome: str, cpf: str = ""):
        self.nome = nome
        self.cpf = cpf
        self.id_geral = str(uuid.uuid4())

    def exibir_info(self):
        return f"Nome: {self.nome} | CPF: {self.cpf}"

class Leitor(Pessoa):
    """Classe Leitor: Herda de Pessoa. Representa o usuário."""
    def __init__(self, nome: str, cpf: str = "", limite_livros: int = 3):
        super().__init__(nome, cpf)
        self.matricula = f"L-{random.randint(1000, 9999)}"
        self.limite_livros = limite_livros
        self.locacoes_ativas = 0
        # print(f"-> Leitor cadastrado: {self.nome} (Matrícula: {self.matricula})")

    def fazer_locacao(self, livro, funcionario):
        """Tenta realizar a locação, checando disponibilidade e limite."""
        if not livro.disponivel:
            return None, f"ERRO: Livro '{livro.titulo}' indisponível."
        if self.locacoes_ativas >= self.limite_livros:
            return None, f"ERRO: Leitor {self.nome} atingiu o limite de {self.limite_livros} locações."
        locacao = Locacao(self, livro, funcionario, prazo_dias=self.get_prazo())
        livro.emprestar()
        self.locacoes_ativas += 1
        return locacao, None

    def devolver_livro(self, locacao_registro, data_real: date):
        """Processa a devolução e calcula multa."""
        if locacao_registro.livro.devolver():
            self.locacoes_ativas = max(0, self.locacoes_ativas - 1)
            locacao_registro.registrar_devolucao(data_real)
            multa = locacao_registro.calcular_multa()
            return multa
        return 0.0

    def get_prazo(self):
        # prazo padrão do leitor
        return 7

class Funcionario(Pessoa):
    """Classe Funcionario: Herda de Pessoa. Responsável por cadastros e registros."""
    def __init__(self, nome: str, cpf: str = "", cargo: str = ""):
        super().__init__(nome, cpf)
        self.id_funcionario = f"F-{random.randint(100, 999)}"
        self.cargo = cargo
        # print(f"-> Funcionário cadastrado: {self.nome} (ID: {self.id_funcionario})")

    def registrar_locacao(self, leitor: Leitor, livro):
        """Inicia a locação via método do Leitor (funcionário pode registrar para leitor)."""
        locacao, erro = leitor.fazer_locacao(livro, self)
        return locacao, erro

    def cadastrar_livro(self, biblioteca, livro):
        """Adiciona um livro ao inventário da biblioteca."""
        biblioteca.adicionar_livro(livro)
        return True

    def get_prazo(self):
        # prazo padrão do funcionário (quando o funcionário pega para si)
        return 14

# ==============================================================================
# 2. CLASSES PARA POLIMORFISMO E ASSOCIAÇÃO
# ==============================================================================
class Livro:
    """Classe Livro (base para Polimorfismo). Define o livro comum."""
    def __init__(self, titulo: str, autor: str, isbn: str):
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.disponivel = True
        self.multa_diaria = 1.00

    def emprestar(self) -> bool:
        self.disponivel = False
        return True

    def devolver(self) -> bool:
        self.disponivel = True
        return True

    def exibir_info(self):
        status = "Disponível" if self.disponivel else "Locado"
        return f"[{self.isbn}] Título: {self.titulo} | Status: {status} | Multa Diária: R$ {self.multa_diaria:.2f}"

    def get_valor_multa_diaria(self) -> float:
        return self.multa_diaria

class LivroReferencia(Livro):
    """Subclasse (Polimorfismo): Multa maior para livros de referência."""
    def __init__(self, titulo: str, autor: str, isbn: str):
        super().__init__(titulo, autor, isbn)
        self.multa_diaria = 5.00

    def get_valor_multa_diaria(self) -> float:
        return self.multa_diaria

class Locacao:
    """Classe de Associação: Conecta Leitor, Livro e Funcionario."""
    def __init__(self, leitor: Leitor, livro: Livro, funcionario: Funcionario, prazo_dias: int = 7):
        self.leitor = leitor
        self.livro = livro
        self.funcionario = funcionario
        self.data_locacao = date.today()
        self.data_devolucao_prevista = self.data_locacao + timedelta(days=prazo_dias)
        self.data_devolucao_real = None

    def calcular_multa(self) -> float:
        """Calcula a multa real baseada nos dias de atraso e no valor polimórfico do Livro."""
        if self.data_devolucao_real and self.data_devolucao_real > self.data_devolucao_prevista:
            dias_atraso = (self.data_devolucao_real - self.data_devolucao_prevista).days
            valor_multa = dias_atraso * self.livro.get_valor_multa_diaria()
            return float(valor_multa)
        return 0.0

    def registrar_devolucao(self, data_real: date):
        self.data_devolucao_real = data_real

# ==============================================================================
# 3. CLASSE DE GERENCIAMENTO (Biblioteca) E FUNÇÕES DO MENU
# ==============================================================================
class Biblioteca:
    """Classe que atua como o banco de dados e gerenciador de coleções (em memória)."""
    def __init__(self):
        self.livros = {}
        self.leitores = {}
        self.funcionarios = {}
        self.locacoes = []

    def adicionar_livro(self, livro: Livro):
        self.livros[livro.isbn] = livro

    def adicionar_leitor(self, leitor: Leitor):
        self.leitores[leitor.matricula] = leitor

    def adicionar_funcionario(self, funcionario: Funcionario):
        self.funcionarios[funcionario.id_funcionario] = funcionario

    def encontrar_leitor(self, matricula: str) -> Leitor:
        return self.leitores.get(matricula)

    def encontrar_funcionario(self, id_func: str) -> Funcionario:
        return self.funcionarios.get(id_func)

    def encontrar_livro(self, isbn: str) -> Livro:
        return self.livros.get(isbn)

# util
def parse_date(date_str: str):
    """Converte string (AAAA-MM-DD) para objeto date."""
    try:
        return date.fromisoformat(date_str)
    except Exception:
        return None

# main CLI (opcional)
def main():
    biblioteca = Biblioteca()
    print("--- ATENÇÃO: Cadastre um funcionário, um leitor e um livro para testar! ---")
    # loop CLI deixado de propósito simples — não utilizado pelo Flask
    while True:
        print("\n1. Cadastrar Pessoas/Livros")
        print("2. Locar Livro")
        print("3. Devolver Livro")
        print("4. Exibir Status")
        print("5. Sair")
        escolha = input("Escolha: ")
        if escolha == '1':
            t = input("Tipo (leitor/funcionario/livro/ref): ")
            if t == 'leitor':
                nome = input("Nome: "); cpf = input("CPF: ")
                biblioteca.adicionar_leitor(Leitor(nome, cpf))
            elif t == 'funcionario':
                nome = input("Nome: "); cpf = input("CPF: "); cargo = input("Cargo: ")
                biblioteca.adicionar_funcionario(Funcionario(nome, cpf, cargo))
            elif t in ['livro','ref']:
                titulo = input("Título: "); autor = input("Autor: "); isbn = input("ISBN: ")
                livro = LivroReferencia(titulo, autor, isbn) if t == 'ref' else Livro(titulo, autor, isbn)
                # cadastrar com primeiro funcionário se houver
                if biblioteca.funcionarios:
                    primeiro = next(iter(biblioteca.funcionarios.values()))
                    primeiro.cadastrar_livro(biblioteca, livro)
                else:
                    biblioteca.adicionar_livro(livro)
            else:
                print("Opção inválida.")
        elif escolha == '2':
            mat = input("Matrícula do leitor: "); isbn = input("ISBN do livro: ")
            leitor = biblioteca.encontrar_leitor(mat); livro = biblioteca.encontrar_livro(isbn)
            func = next(iter(biblioteca.funcionarios.values())) if biblioteca.funcionarios else None
            if not (leitor and livro and func):
                print("ERRO: faltando dados")
            else:
                loc, err = func.registrar_locacao(leitor, livro)
                if loc:
                    biblioteca.locacoes.append(loc)
                    print("Locação criada.")
                else:
                    print(err)
        elif escolha == '3':
            mat = input("Matrícula: "); isbn = input("ISBN: "); data_str = input("Data devolução (AAAA-MM-DD): ")
            data_real = parse_date(data_str)
            leitor = biblioteca.encontrar_leitor(mat)
            registro_encontrado = None
            for loc in biblioteca.locacoes:
                if loc.leitor.matricula == mat and loc.livro.isbn == isbn and not loc.livro.disponivel:
                    registro_encontrado = loc
                    break
            if registro_encontrado:
                multa = leitor.devolver_livro(registro_encontrado, data_real)
                print(f"Devolução registrada. Multa: R$ {multa:.2f}")
            else:
                print("Registro não encontrado.")
        elif escolha == '4':
            print("-- Leitores --")
            for l in biblioteca.leitores.values():
                print(f"{l.matricula} - {l.nome} - Ativas: {l.locacoes_ativas}")
            print("-- Livros --")
            for lv in biblioteca.livros.values():
                print(lv.exibir_info())
            print("-- Locações Ativas --")
            for loc in biblioteca.locacoes:
                if not loc.livro.disponivel:
                    print(f"{loc.livro.titulo} -> {loc.leitor.nome} (prev: {loc.data_devolucao_prevista})")
        elif escolha == '5':
            break
        else:
            print("Inválido.")

if __name__ == "__main__":
    main()
