# Generated by Django 2.2.16 on 2023-06-26 18:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_auto_20230620_1641'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='title',
            new_name='name',
        ),
        migrations.RenameField(
            model_name='recipe',
            old_name='description',
            new_name='text',
        ),
        migrations.RenameField(
            model_name='recipeingredient',
            old_name='quantity',
            new_name='amount',
        ),
    ]