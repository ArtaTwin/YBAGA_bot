import time

from PIL       import Image

__all__ = ['painter']

def color(t, alarm):
    score = (time.time()-t)/7200 #one score is two hours

    if alarm:
        if score >= 2:
            return (50,0,0)
        elif score >= 1:
            return (100,0,0)
        else:
            return (150,0,0)
    else:
        if score >= 2:
            return (0,120,100)
        elif score >= 1:
            return (0,120,50)
        else:
            return (0,120,0)

def painter(situation, add_maket, add_pal):
    pal = [
        150,0,0,
        100,0,0,
        50,0,0,
        0,120,0,
        0,120,50,
        0,120,100,
        0,0,0,
        30,30,30,
        100,100,100,
        130,130,130,
        255,255,255
    ]

    image = Image.open(r"static/map.png")
    image.putpalette(
        [
            primary_color
            for state in situation
            for primary_color in color(state["date"], state["alarm"])
        ]+ pal+ add_pal
    )

    image.paste(add_maket)

    return image
