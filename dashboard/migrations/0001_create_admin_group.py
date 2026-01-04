
from django.db import migrations


def create_admin_group(apps, schema_editor):
    """Create Admin group when migration runs"""
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='Admin')


class Migration(migrations.Migration):

    dependencies = [
        # If you have a previous migration, it will be auto-filled here
        # If this is your first migration, leave it empty: ('dashboard', [])
    ]

    operations = [
        migrations.RunPython(create_admin_group),
    ]