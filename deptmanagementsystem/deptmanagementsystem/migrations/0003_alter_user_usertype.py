# Generated by Django 4.2.9 on 2024-03-14 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deptmanagementsystem', '0002_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='userType',
            field=models.CharField(choices=[('prof', 'Professor'), ('stud', 'Student'), ('hod', 'Head of Department'), ('clerk', 'Clerk')], max_length=10),
        ),
    ]