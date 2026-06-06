import os
import sys
import random
import django

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DevBasement.settings")
django.setup()

from django.contrib.auth import get_user_model

from accounts.models import Profile
from projects.models import (
    Technology,
    Project,
    ProjectSection,
    SectionReferenceLink,
    SectionAnswer,
    Comment,
    ProjectLike,
)
from moderation.models import Report

User = get_user_model()

def clean_database():
    print("Limpando banco de dados...")

    Report.objects.all().delete()
    Comment.objects.all().delete()
    SectionAnswer.objects.all().delete()
    SectionReferenceLink.objects.all().delete()
    ProjectSection.objects.all().delete()
    ProjectLike.objects.all().delete()
    Project.objects.all().delete()

    User.objects.exclude(
        username="adm"
    ).delete()

    print("Banco limpo.")

def seed():

    print("Carregando e sincronizando tecnologias...")

    tech_names = [
        "Python", "Django", "JavaScript", "React", "Vue",
        "PostgreSQL", "MySQL", "Docker", "Linux", "Tailwind",
        "HTML", "CSS", "C++", "OpenGL", "Raylib",
    ]

    for name in tech_names:
        Technology.objects.get_or_create(name=name)

    technologies = list(Technology.objects.all())

    print("Criando usuários...")

    users_info = [
        ("adm", "Administrador"),
        ("joao", "João"),
        ("clara", "Clara"),
        ("lucas", "Lucas"),
        ("amanda", "Amanda"),
        ("felipe", "Felipe"),
        ("bruna", "Bruna"),
        ("rafael", "Rafael"),
        ("marina", "Marina"),
        ("pedro", "Pedro"),
    ]

    users = []

    for username, first_name in users_info:
        user_defaults = {
            "email": f"{username}@devbasement.com",
            "first_name": first_name,
            "is_active": True,
        }

        if username == "adm":
            user_defaults["is_staff"] = True
            user_defaults["is_superuser"] = True

        user, created = User.objects.get_or_create(
            username=username,
            defaults=user_defaults,
        )

        if created:
            user.set_password("1234")
            user.save()
        else:
            if username == "adm" and (not user.is_staff or not user.is_superuser):
                user.is_staff = True
                user.is_superuser = True
                user.save()

        profile = user.profile
        profile.bio = f"Desenvolvedor apaixonado por {random.choice(tech_names)}."
        profile.github_url = f"https://github.com/{username}"
        profile.website = f"https://{username}.dev"
        profile.save()

        users.append(user)

    project_templates = [
        (
            "Sistema de Gestão Escolar",
            "Plataforma para gerenciamento acadêmico."
        ),
        (
            "DevBasement",
            "Rede social voltada para desenvolvedores."
        ),
        (
            "Task Manager",
            "Aplicação para gerenciamento de tarefas."
        ),
        (
            "Portfolio Profissional",
            "Portfólio moderno e responsivo."
        ),
        (
            "API de E-commerce",
            "Backend para lojas virtuais."
        ),
        (
            "Sistema de Inventário",
            "Controle de estoque e produtos."
        ),
        (
            "Chat em Tempo Real",
            "Mensageria utilizando WebSockets."
        ),
        (
            "Code Snippets",
            "Organizador de trechos de código."
        ),
    ]

    all_projects = []

    print("Criando projetos...")

    for user in users:

        amount = random.randint(1, 4)

        for title, description in random.sample(
            project_templates,
            amount,
        ):

            final_title = (
                f"{title}"
            )

            project, created = Project.objects.get_or_create(
                owner=user,
                title=final_title,
                defaults={
                    "description": description,
                    "is_private": random.choice(
                        [True, False]
                    ),
                    "status": random.choice(
                        [
                            "planning",
                            "in_progress",
                            "completed",
                        ]
                    ),
                },
            )

            project.technologies.set(
                random.sample(
                    technologies,
                    random.randint(1, 4),
                )
            )

            all_projects.append(project)

    print("Criando seções e referências...")

    for project in all_projects:

        if project.sections.exists():
            continue

        ProjectSection.objects.create(
            project=project,
            title="Descrição",
            content=project.description,
            section_type="text",
            is_description=True,
            is_pinned=True,
            order=0,
        )

        question = ProjectSection.objects.create(
            project=project,
            title="Como melhorar a arquitetura?",
            content="Gostaria de sugestões para escalabilidade.",
            section_type="question",
            is_pinned=random.random() < 0.4,
            order=1,
        )

        reference_section = ProjectSection.objects.create(
            project=project,
            title="Documentação e Links Úteis",
            content="Abaixo compilei os principais materiais, repositórios e links de artigos que serviram de fundação teórica para mim durante o escopo deste desenvolvimento.",
            section_type="reference",
            is_pinned=random.random() < 0.3,
            order=2,
        )

        links_templates = [
            ("Repositório Principal no GitHub", f"https://github.com/{project.owner.username}"),
            ("Documentação Oficial do Framework", "https://docs.djangoproject.com/"),
            ("Referência de Deploy e Infra", "https://www.docker.com/"),
            ("Design System e UI Kit Utilitário", "https://tailwindcss.com/")
        ]
        
        for description, url in random.sample(links_templates, random.randint(1, 3)):
            SectionReferenceLink.objects.create(
                section=reference_section,
                description=description,
                url=url
            )

        responders = [
            u for u in users
            if u != project.owner
        ]

        for responder in random.sample(
            responders,
            random.randint(
                1,
                min(3, len(responders))
            ),
        ):

            SectionAnswer.objects.create(
                section=question,
                user=responder,
                content=random.choice([
                    "Utilize cache para reduzir consultas.",
                    "Considere filas assíncronas.",
                    "Docker pode facilitar a implantação.",
                    "Separar serviços pode ajudar.",
                    "Excelente abordagem estrutural.",
                ]),
            )

    print("Criando interações e favoritos...")

    public_projects = [
        p for p in all_projects
        if not p.is_private
    ]

    for project in public_projects:

        possible_users = [
            u
            for u in users
            if u != project.owner
        ]

        for user in random.sample(
            possible_users,
            random.randint(0, len(possible_users)),
        ):
            ProjectLike.objects.get_or_create(
                user=user,
                project=project,
            )

        for user in random.sample(
            possible_users,
            random.randint(0, len(possible_users)),
        ):
            project.favorites.add(user)

        for user in random.sample(
            possible_users,
            random.randint(0, len(possible_users)),
        ):
            Comment.objects.create(
                project=project,
                user=user,
                content=random.choice([
                    "Projeto muito interessante.",
                    "Gostei da arquitetura.",
                    "Parabéns pelo trabalho.",
                    "Vou testar depois.",
                    "Excelente documentação.",
                    "Ideia genial!",
                ]),
            )

    print("Criando denúncias...")

    reasons = [
        "spam",
        "inappropriate",
        "copyright",
        "other",
    ]

    if public_projects:

        for project in random.sample(
            public_projects,
            min(3, len(public_projects)),
        ):

            reporter = random.choice(
                [
                    u
                    for u in users
                    if u != project.owner
                ]
            )

            Report.objects.get_or_create(
                project=project,
                user=reporter,
                defaults={
                    "reason": random.choice(reasons),
                    "description":
                        "Denúncia gerada para testes.",
                },
            )

    print()
    print("================================")
    print("Dados de teste criados.")
    print("Senha de todos os usuários: 1234")
    print()
    print("Usuários disponíveis:")

    for user in users:
        print(f"  @{user.username}")

    print("================================")


if __name__ == "__main__":

    if "--clean-only" in sys.argv:
        clean_database()
        sys.exit(0)

    if "--clean" in sys.argv:
        clean_database()

    seed()