from django.db import models

class Помещение(models.Model):
    длина = models.FloatField(verbose_name="Длина, м")
    ширина = models.FloatField(verbose_name="Ширина, м")
    высота = models.FloatField(verbose_name="Высота, м")
    кол_окон = models.IntegerField(default=0, verbose_name="Количество окон")
    ширина_окна = models.FloatField(default=0, verbose_name="Ширина окна, м")
    высота_окна = models.FloatField(default=0, verbose_name="Высота окна, м")
    кол_дверей = models.IntegerField(default=0, verbose_name="Количество дверей")
    ширина_двери = models.FloatField(default=0, verbose_name="Ширина двери, м")
    высота_двери = models.FloatField(default=0, verbose_name="Высота двери, м")

class Wallpaper(models.Model):
    название = models.CharField(max_length=100, verbose_name="Название")
    ширина_рулона = models.FloatField(verbose_name="Ширина рулона, м")
    длина_рулона = models.FloatField(verbose_name="Длина рулона, м")
    текстура = models.ImageField(upload_to='wallpapers/', verbose_name="Текстура")

    def __str__(self):
        return self.название