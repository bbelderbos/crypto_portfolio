# Generated by Django 3.1.7 on 2021-03-26 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_portfolioholdings_amount_in_usd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolioholdings',
            name='type',
            field=models.CharField(default='Click to choose Buy or Sell', max_length=10),
        ),
    ]
