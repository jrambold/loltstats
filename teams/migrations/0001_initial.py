# Generated by Django 2.0.5 on 2018-06-05 22:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FlexMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gameId', models.BigIntegerField()),
                ('champion', models.IntegerField()),
                ('season', models.IntegerField()),
                ('timestamp', models.BigIntegerField()),
                ('role', models.CharField(max_length=200)),
                ('lane', models.CharField(max_length=200)),
                ('game_version', models.CharField(max_length=200)),
                ('win', models.BooleanField()),
                ('top', models.BigIntegerField(default=0)),
                ('mid', models.BigIntegerField(default=0)),
                ('jun', models.BigIntegerField(default=0)),
                ('adc', models.BigIntegerField(default=0)),
                ('sup', models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('riot_id', models.BigIntegerField()),
                ('account_id', models.BigIntegerField()),
                ('name', models.CharField(max_length=200)),
                ('profile_icon_id', models.IntegerField()),
                ('revision_date', models.IntegerField()),
                ('summoner_level', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SoloMatch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gameId', models.BigIntegerField()),
                ('champion', models.IntegerField()),
                ('season', models.IntegerField()),
                ('timestamp', models.BigIntegerField()),
                ('role', models.CharField(max_length=200)),
                ('lane', models.CharField(max_length=200)),
                ('game_version', models.CharField(max_length=200)),
                ('win', models.BooleanField()),
                ('top', models.BigIntegerField(default=0)),
                ('mid', models.BigIntegerField(default=0)),
                ('jun', models.BigIntegerField(default=0)),
                ('adc', models.BigIntegerField(default=0)),
                ('sup', models.BigIntegerField(default=0)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Player')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('server', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='player',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Team'),
        ),
        migrations.AddField(
            model_name='flexmatch',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.Player'),
        ),
    ]
