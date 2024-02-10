Simple weather display for a Raspberry Pi Zero W with a Waveshare 2.13" V4 e-Paper HAT display.

Based off of the python example from https://github.com/waveshare/e-Paper.git


### Usage

Create a transient timer to update the display every 15 minutes, thus no need for a lengthly sleep() call in the code:

    systemd-run -u epaper-weather -r --uid=1000 \
        -E OPENWEATHERMAP_CITY=<city> -E OPENWEATHERMAP_KEY=<apikey> \
        --on-boot=60 --on-unit-active=900 python /path/to/weather.py

To manage the service, use systemd's built-ins:

    systemctl list-timers --all
    systemctl status epaper-weather.timer epaper-weather.service
    systemctl stop epaper-weather.timer

The program currently displays the temperature in metric, however there are two variables to change if you wish to use imperial units.

### Screenshot

![Screenshot](output.jpg)

### In Action

![Action Shot](display.jpg)
