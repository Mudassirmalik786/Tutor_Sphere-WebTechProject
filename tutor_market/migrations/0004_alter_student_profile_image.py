# Generated by Django 5.0.6 on 2024-07-03 07:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutor_market', '0003_alter_student_profile_image_alter_tutor_ratings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='student_images'),
        ),
    ]