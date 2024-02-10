import sys
import os

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib")
if os.path.exists(libdir):
    sys.path.append(libdir)

from datetime import date
from PIL import Image, ImageOps, ImageDraw, ImageFont

import requests
from waveshare_epd import epd2in13_V4

# Units are "standard" (kelvin), "imperial", or "metric"
units = "metric"
symbol = "C"

def get_weather(api_key, city_id):
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # Replace "id" with "q" to search for a city name instead
    # You can also pass "lat" and "lon" instead of "id" to use your location
    complete_url = base_url + "appid=" + api_key + "&id=" + city_id + "&units=" + units

    # Get response from server
    response = requests.get(complete_url)

    # Returns data from api as a dictionary
    data = response.json()

    if data["cod"] != "404":
        return data

def get_weather_icon(code):
    complete_url = "http://openweathermap.org/img/wn/" + code + ".png"
    response = requests.get(complete_url, stream=True)

    img = Image.open(response.raw)
    img = img.convert(mode="RGB")
    img = img.resize((80,80), Image.BICUBIC)
    img = ImageOps.invert(img)

    return img

if __name__ == "__main__":
    epd = epd2in13_V4.EPD()

    ow_api_key = os.environ.get("OPENWEATHERMAP_KEY")
    ow_city_id = os.environ.get("OPENWEATHERMAP_CITY")
    weather = get_weather(ow_api_key, ow_city_id)

    temp_current = str(round(weather["main"]["temp"]))
    temp_feels   = "Feels like " + str(round(weather["main"]["feels_like"]))
    temp_low     = str(round(weather["main"]["temp_min"]))
    temp_high    = str(round(weather["main"]["temp_max"]))
    temp_desc    = weather["weather"][0]["description"]
    temp_loc     = weather["name"] + ", " + weather["sys"]["country"]
    temp_icon    = get_weather_icon(weather["weather"][0]["icon"])

    image = Image.new("1", (epd.width, epd.height), 255)
    canvas = ImageDraw.Draw(image)

    fontSmall  = ImageFont.truetype(os.path.join(libdir, "Font.ttc"), 12)
    fontLarge  = ImageFont.truetype(os.path.join(libdir, "Font.ttc"), 60)
    fontMedium = ImageFont.truetype(os.path.join(libdir, "Font.ttc"), 24)

    # Draw the background layout
    canvas.rectangle([0, 0, epd.width, 20], fill=0)
    canvas.line([0, 100, 122, 100], fill=0)
    canvas.line([0, 150, 122, 150], fill=0)
    canvas.line([epd.width / 2, 100, epd.width / 2, 150], fill=0)

    # Labels
    canvas.text((epd.width / 4, 104), "High", font=fontSmall, fill=0, anchor="mt")
    canvas.text((epd.width / 4 * 3, 104), "Low", font=fontSmall, fill=0, anchor="mt")
    canvas.text((epd.width - 10, 30), symbol, font=fontSmall, fill=0, anchor="mt") # Replace with your preferred units identifier

    # Header text
    canvas.text((5, 6), "rpi", font=fontSmall, fill=255, anchor="lt")
    canvas.text((epd.width - 5, 6), str(date.today()), font=fontSmall, fill=255, anchor="rt")

    # Weather temperatures
    canvas.text((epd.width / 2, 55), temp_current, font=fontLarge, fill=0, anchor="mm")
    canvas.text((epd.width / 4, 132), temp_high, font=fontMedium, fill=0, anchor="mm")
    canvas.text((epd.width / 4 * 3, 132), temp_low, font=fontMedium, fill=0, anchor="mm")
    canvas.text((epd.width / 2, 90), temp_feels, font=fontSmall, fill=0, anchor="mm")

    # Icon and description
    image.paste(temp_icon, (20, 158))
    canvas.text((epd.width / 2, 160), temp_desc, font=fontSmall, fill=0, anchor="mm")

    # Footer
    canvas.rectangle([0, epd.height - 20, epd.width, epd.height], fill=0)
    canvas.text((epd.width / 2, epd.height - 4), temp_loc, font=fontSmall, fill=255, anchor="mb")

    # Send the resulting image to the E-Paper Display
    epd.init()
    epd.display(epd.getbuffer(image))
    epd.sleep()
