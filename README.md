# Sistema de Biblioteca POO

Uma aplicação web de gerenciamento de biblioteca desenvolvida com Flask e SQLAlchemy, demonstrando conceitos de Programação Orientada a Objetos (OOP): **herança, polimorfismo e associação**.

## 🏗️ Arquitetura OOP
## 🏗️ Arquitetura OOP (explicação detalhada)

Esta aplicação foi projetada para demonstrar claramente três conceitos de POO: **Herança**, **Polimorfismo** e **Associação**. A seguir explico como cada um foi implementado no código e como eles interagem nas rotas.

### Herança

Usamos classes base que representam entidades genéricas e subclasses que estendem comportamento e atributos.

- `Pessoa` é a classe base para `Leitor` e `Funcionario`.

  Exemplo (trecho de `sistema.py`):

  ```python
  class Pessoa(db.Model):
     id = db.Column(db.String, primary_key=True)
     nome = db.Column(db.String(100), nullable=False)
     cpf = db.Column(db.String(14))
     tipo = db.Column(db.String(50))
     __mapper_args__ = {'polymorphic_identity': 'pessoa', 'polymorphic_on': tipo}

  class Leitor(Pessoa):
     __mapper_args__ = {'polymorphic_identity': 'leitor'}
     matricula = db.Column(db.String(20), unique=True, index=True)

  class Funcionario(Pessoa):
     __mapper_args__ = {'polymorphic_identity': 'funcionario'}
     cargo = db.Column(db.String(50))
  ```

### Polimorfismo (Single Table Inheritance)

Para `Livro` aplicamos Single Table Inheritance (STI): as subclasses compartilham a mesma tabela mas têm comportamentos diferentes.

 - `Livro` é a classe base com os campos comuns (`isbn`, `titulo`, `autor`, `disponivel`, `multa_diaria`).
 - `LivroReferencia` herda de `Livro` e altera comportamento (ex.: multa diária maior).

Exemplo:

```python
class Livro(db.Model):
   isbn = db.Column(db.String(20), primary_key=True)
   titulo = db.Column(db.String(200), nullable=False)
   disponivel = db.Column(db.Boolean, default=True)
   multa_diaria = db.Column(db.Float, default=1.00)
   tipo = db.Column(db.String(50))
   __mapper_args__ = {'polymorphic_identity': 'livro_comum', 'polymorphic_on': tipo}

class LivroReferencia(Livro):
   __mapper_args__ = {'polymorphic_identity': 'livro_referencia'}
   def __init__(self, titulo, autor, isbn, **kwargs):
      super().__init__(titulo=titulo, autor=autor, isbn=isbn, **kwargs)
      self.multa_diaria = 5.00
```

Como consequência, quando você faz `Livro.query.all()` o SQLAlchemy retorna instâncias do tipo correto (`Livro` ou `LivroReferencia`) e chamar `l.get_valor_multa_diaria()` aplica a regra correta dependendo da subclasse.

### Associação (classe de associação `Locacao`)

Para representar empréstimos usamos a tabela `Locacao` como **classe de associação** que conecta `Leitor`, `Livro` e `Funcionario`.

Principais pontos:

- `Locacao` tem chaves estrangeiras para `pessoas.id` (leitor e funcionario) e `livros.isbn` (livro).
- A `Locacao` armazena datas `data_locacao`, `data_devolucao_prevista` e `data_devolucao_real`.
- Relacionamentos (`db.relationship`) permitem navegar facilmente entre objetos: `locacao.leitor`, `locacao.livro`, `locacao.funcionario`.

Exemplo simplificado:

```python
class Locacao(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   data_locacao = db.Column(db.Date, default=date.today)
   leitor_id = db.Column(db.String, db.ForeignKey('pessoas.id'))
   livro_isbn = db.Column(db.String(20), db.ForeignKey('livros.isbn'))

   leitor = db.relationship('Leitor', backref='locacoes_feitas')
   livro = db.relationship('Livro', backref='registros_locacao')
```


## 📋 Funcionalidades

✅ Cadastrar Leitores, Funcionários, Livros e Livros de Referência  
✅ Locar livros para leitores  
✅ Devolver livros com cálculo de multa por atraso  
✅ Status do sistema (resumo, listas, locações ativas)  
✅ Pesquisar locações por matrícula de leitor  
✅ Feedback visual com mensagens de sucesso/erro  

## 🚀 Deploy no Render.com

### Pré-requisitos
1. Repositório GitHub com o código: `fabzera2007/bibliotecaPOO`
2. Conta no [Render.com](https://render.com) (gratuita)

### Passos de Deploy

1. **Acesse [render.com](https://render.com)** e faça login com sua conta GitHub

2. **Clique em "New +"** → **"Web Service"**

3. **Selecione o repositório**:
   - Procure por `bibliotecaPOO`
   - Clique em "Connect"

4. **Configure o serviço**:
   - **Name**: `biblioteca-poo` (ou qualquer nome)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Free Plan** (ou pago, se preferir)

5. **Clique em "Deploy"**

6. **Aguarde** (~2-5 minutos). Você verá a URL da sua app como:
   ```
   https://biblioteca-poo.onrender.com
   ```

### Notas Importantes

- O banco de dados SQLite é local (Render não persiste arquivos entre reinicializações)
- Para dados persistentes, integre com PostgreSQL (oferecido pelo Render)
- Mensagens de flash funcionam com sessões (secret_key configurada)

## 💻 Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar a aplicação
python app.py
# Acesse: http://localhost:5000
```

## 📁 Estrutura do Projeto

```
bibliotecaPOO/
├── app.py              # Routes Flask
├── sistema.py          # Modelos ORM
├── requirements.txt    # Dependências
├── render.yaml         # Configuração Render
├── .gitignore          # Arquivos ignorados
├── static/
│   └── style.css       # Estilos
└── templates/
    ├── base.html       # Layout base
    ├── index.html      # Home
    ├── cadastrar.html  # Cadastros
    ├── locar.html      # Locação
    ├── devolver.html   # Devolução
    └── status.html     # Status
```

## 🔧 Tecnologias

- **Backend**: Flask 2.3.3
- **ORM**: Flask-SQLAlchemy 3.0.5
- **Servidor**: Gunicorn 21.2.0
- **Frontend**: HTML5 + CSS3 + Vanilla JavaScript

---

**Desenvolvido com conceitos de POO (Herança, Polimorfismo, Associação)**
