# Generated by Django 2.2.16 on 2023-06-15 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_auto_20230611_1730'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={'verbose_name': 'RecipeIngredient', 'verbose_name_plural': 'RecipeIngredients'},
        ),
    ]
