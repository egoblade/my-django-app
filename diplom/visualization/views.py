from django.shortcuts import render
from .models import Wallpaper

def room_visualization(request):
    # дефолтные параметры (можно задать любые)
    ctx = {
        'L': 5, 'W': 4, 'H': 3,
        'num_win': 1, 'win_w': 1, 'win_h': 1.2,
        'num_door': 1, 'door_w': 0.9, 'door_h': 2,
        'wallpapers': Wallpaper.objects.all(),
    }
    return render(request, 'visualization/index.html', ctx)
