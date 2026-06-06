# DevBasement

Um gerenciador de projetos para desenvolvedores.

## Descrição do objetivo do sistema e problema resolvido

Durante o processo de aprendizado e desenvolvimento de software, é comum acumular links, trechos de código, documentações e anotações espalhadas em diferentes locais, como favoritos do navegador, blocos de notas ou mensagens salvas. O DevBasement resolve esse problema centralizando todas essas informações em um único ecossistema.

A plataforma permite que desenvolvedores organizem repositórios do GitHub, links de documentação, arquivos Markdown, snippets de código e textos em painéis unificados. Além de servir como um organizador pessoal, o sistema mitiga o isolamento do desenvolvedor ao permitir a publicação desses projetos para a comunidade, viabilizando a troca de feedbacks, curtidas, comentários e apoio mútuo entre profissionais.

## Usuários suportados e permissões

O sistema conta com três níveis de acesso bem definidos:

### 1. Usuário Não Autenticado (Visitante)

* Visualizar o feed principal com projetos públicos em destaque.
* Utilizar a barra de pesquisa global para buscar projetos e perfis públicos.
* Visualizar detalhes de projetos públicos, incluindo suas seções e comentários.
* Visualizar perfis públicos de outros desenvolvedores.
* Acessar as páginas de login e cadastro.

### 2. Usuário Autenticado (Desenvolvedor)

* Todas as permissões do Visitante.
* Criar, editar, atualizar e excluir seus próprios projetos.
* Definir a visibilidade dos seus projetos como públicos ou privados.
* Gerenciar seções dentro dos seus projetos (criar, editar, excluir, fixar itens e responder seções).
* Interagir com projetos de terceiros por meio de curtidas, comentários e favoritados.
* Seguir ou deixar de seguir outros desenvolvedores da plataforma.
* Editar as informações do seu próprio perfil.

### 3. Administrador (Staff)

* Todas as permissões do Usuário Autenticado.
* Acesso ao painel administrativo nativo do Django para gerenciamento completo do banco de dados.
* Acesso ao Painel de Moderação dedicado na interface do sistema.
* Visualizar a listagem de denúncias (reports) enviadas pelos usuários.
* Moderar ou remover conteúdos que violem as diretrizes da comunidade.

## Requisitos de instalação e execução

Siga os passos abaixo para configurar e executar o projeto em um ambiente de testes local.

### Pré-requisitos

* Python 3.10 ou superior instalado.
* Git instalado.

### Passo a passo para instalação

1. Clone o repositório em uma pasta limpa:

```bash
git clone https://github.com/ImJotaM/DevBasement.git
cd DevBasement
```

2. Crie um ambiente virtual (venv):

```bash
python -m venv venv
```

3. Ative o ambiente virtual:

* **Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

* **Linux/Mac:**

```bash
source venv/bin/activate
```

4. Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

5. Execute as migrações do banco de dados para criar a estrutura inicial:
```bash
python manage.py migrate
```

## Opções de Inicialização para Testes

> **Importante:** Certifique-se de executar o comando `python manage.py migrate` antes de prosseguir com qualquer uma das opções abaixo.

### Opção A: Ambiente Limpo (Sem dados prévios)

Caso prefira realizar os testes em um banco de dados totalmente zerado e criar seus registros manualmente, crie uma conta de administrador inicial utilizando o terminal:

```bash
python manage.py createsuperuser
```

Defina as credenciais conforme solicitado pelas instruções do terminal e, em seguida, inicie o servidor:

```bash
python manage.py runserver
```

### Opção B: Ambiente Preparado (População automática de dados)

Para carregar um cenário de testes robusto contendo múltiplos usuários, seguidores, projetos com seções estruturadas, respostas, curtidas, comentários e denúncias, execute o script de automação a partir do diretório raiz:

```bash
python scripts/populate.py
```

#### Argumentos suportados pelo script

Você pode controlar o comportamento da população de dados passando parâmetros adicionais no terminal:

| Argumento | Ação executada |
| --- | --- |
| *(Nenhum)* | Mantém os registros existentes e adiciona uma nova carga de dados de teste por cima. |
| `--clean` | Limpa completamente os registros antigos de dados do banco (exceto o usuário administrador original `@adm`) antes de rodar a nova população. |
| `--clean-only` | Apenas limpa o banco de dados e encerra a execução sem inserir novas informações. |

*Exemplo de uso com limpeza completa:*

```bash
python scripts/populate.py --clean
```

Após a conclusão da carga, inicie o servidor de desenvolvimento:

```bash
python manage.py runserver
```

A aplicação estará disponível em `http://localhost:8000/`.

**Credenciais para teste rápido (Opção B):**

* **Contas de usuários criadas:** joao, clara, lucas, amanda, felipe, bruna, rafael, marina, pedro.
* **Senha padrão para todas as contas:** 1234
* **Conta de administrador:** adm (possui acesso total ao Painel de Moderação, a senha se mantém 1234).

## Instruções de uso das principais funcionalidades

### Criação de Projetos

Após efetuar o login, clique no botão com o ícone de adição (+) localizado na barra de navegação superior ou utilize o atalho no painel central. Você será redirecionado para a rota `/project/create/`, onde poderá definir o título, descrição e visibilidade do projeto.

### Organização em Seções

Dentro da página de detalhes do seu projeto, utilize os controles dinâmicos para adicionar novos blocos de conteúdo. É possível segmentar o projeto em repositórios, links externos ou snippets de código, além de poder fixar (pin) as seções mais importantes no topo da página.

### Sistema de Busca Avançada

A barra de pesquisa na navbar realiza consultas em tempo real a partir do segundo caractere digitado. Ela segmenta de forma automática projetos públicos e perfis de desenvolvedores relevantes, bloqueando a exibição de conteúdos marcados como privados.

### Moderação de Conteúdo

Para testar o fluxo de administração, faça login com uma conta que possua permissões de administrador (como o usuário `adm` fornecido no script de automação). O bloco chamado "Painel de Moderação" ficará visível na barra lateral direita da página inicial, permitindo auditar e gerenciar projetos que foram reportados.
