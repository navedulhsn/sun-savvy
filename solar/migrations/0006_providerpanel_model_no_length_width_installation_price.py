# Generated manually to add new fields to ProviderPanel model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('solar', '0005_providerpanel'),
    ]

    operations = [
        migrations.AddField(
            model_name='providerpanel',
            name='model_no',
            field=models.CharField(blank=True, help_text='Model number or SKU', max_length=100),
        ),
        migrations.AddField(
            model_name='providerpanel',
            name='length',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Length in meters', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='providerpanel',
            name='width',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Width in meters', max_digits=6, null=True),
        ),
        migrations.AddField(
            model_name='providerpanel',
            name='installation_price',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Installation price in PKR', max_digits=12, null=True),
        ),
    ]

