from django.db import migrations

def popular_tecnologias(apps, schema_editor):
    Technology = apps.get_model('projects', 'Technology')
    
    lista_techs = [
        "Python", "Django", "JavaScript", "React", 
        "PostgreSQL", "Docker", "Bootstrap", "Node.js",
        "C", "C++", "Rust", "Go", "C#", ".NET"
    ]
    
    for tech_name in lista_techs:
        from django.utils.text import slugify
        
        name_lower = tech_name.lower()
        name_lower = name_lower.replace('c++', 'cpp')
        name_lower = name_lower.replace('c#', 'csharp')
        name_lower = name_lower.replace('.net', 'dotnet')
        
        tech_slug = slugify(name_lower)
        
        Technology.objects.get_or_create(
            name=tech_name,
            defaults={'slug': tech_slug}
        )

class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_technology_project_technologies'),
    ]

    operations = [
        migrations.RunPython(popular_tecnologias),
    ]