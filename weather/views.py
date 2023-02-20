from django.shortcuts import render
from .models import City
from .forms import CityForm
import requests


def index(request):
    url = 'https://api.weatherapi.com/v1/current.json?key=acf397923ff642be91c94723210710&q={}&aqi=yes'
    queryset = City.objects.all()
    set_cities = set(sorted([city['name'] for city in list(queryset.values())]))
    city = sorted([city['name'] for city in list(queryset.values())])[0]
    if request.method == 'POST':
        city = request.POST['name']
        if city not in set_cities:
            form = CityForm(request.POST)
            form.save()
    form = CityForm()
    cities = City.objects.all()
    temp = sorted([city['name'] for city in list(cities.values())])
    print(temp)
    set_cities = set()
    for i in temp:
        set_cities.add(i)
    print(set_cities)

    r = requests.get(url.format(city)).json()
    link = 'https://' + r['current']["condition"]['icon'][2:]
    city_weather = {
        'city': city.capitalize(),
        'temperature': r['current']['temp_c'],
        'description': r['current']['condition']['text'],
        'icon': link,
        'wind': r['current']['wind_kph'],
        'wind_direction': r['current']['wind_dir'],
        'uv': r['current']['uv'],
        'aqi': max(int(r['current']['air_quality']['co'] / 100),
                   int(r['current']['air_quality']['no2']),
                   int(r['current']['air_quality']['o3']),
                   int(r['current']['air_quality']['so2']),
                   int(r['current']['air_quality']['pm2_5']),
                   int(r['current']['air_quality']['pm10'])),
    }
    aqi = city_weather['aqi']
    if aqi < 51:
        city_weather['quality'] = 'Good'
    elif aqi < 101:
        city_weather['quality'] = 'Moderate'
    elif aqi < 151:
        city_weather['quality'] = 'Unhealthy for sensitive groups'
    elif aqi < 201:
        city_weather['quality'] = 'Unhealthy'
    elif aqi < 301:
        city_weather['quality'] = 'Very unhealthy'
    else:
        city_weather['quality'] = 'Hazardous'
    print(city_weather)
    context = {'city_weather': city_weather, 'cities': temp, 'form': form}
    return render(request, 'weather/weather.html', context)
