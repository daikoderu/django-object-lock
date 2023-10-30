# Generated by Django 4.2.5 on 2023-10-30 21:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_locked', models.BooleanField(default=False, help_text='Whether this object is locked or not. Locked objects cannot be edited.', verbose_name='is locked')),
                ('title', models.CharField(help_text='The title of this article.', max_length=120, verbose_name='title')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ArticleSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('heading', models.CharField(help_text='The heading for this section.', max_length=120, verbose_name='heading')),
                ('content', models.TextField(help_text='The contents of this section.', verbose_name='content')),
                ('order', models.IntegerField(help_text='The relative position of this field in relation to other sections in the same report.', verbose_name='order')),
                ('parent', models.ForeignKey(help_text='The article containing this section.', on_delete=django.db.models.deletion.CASCADE, to='articles.article', verbose_name='parent article')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
