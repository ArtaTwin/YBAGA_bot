from PIL       import Image

__all__ = ['writing', 'pictorial', 'decoder']

changes = "apceoixy" #eng
targets = "арсеоіху" #ukr

def to_bits(num: int):
    return [symbol=="1" for symbol in f"{abs(num):b}"]

def writing(text: str, num: int):
    bits = to_bits(num)
    translator = dict(
        zip(targets,changes)
    )
    text = list(text)
    i = int()

    while bits:
        letter = text[i]
        if letter in targets and bits.pop():
            text[i] = translator[letter]
        i+=1

    return "".join(text)

def pictorial(num: int):
    if num == 0:
        pal= []
        maket = Image.new(
                "P",
                (0, 0)
            )
        return maket, pal


    pal=list(map(
        lambda x: 255 if x else 20,
        to_bits(num)
    ))

    count_cells, rest = divmod(
        (num).bit_length(), 3       #(num).bit_length() = len(pal)
    )
    width_cells= 5
    height_cells= 2

    if rest != 0:
         count_cells += 1
         pal += [128]*(3-rest)

    maket = Image.new(
        "P",
        (count_cells, 1)
    )
    maket.putpalette(pal)

    for x in range(count_cells):
        maket.putpixel((x,0), x+36)

    return maket.resize( (count_cells*width_cells, height_cells) ), pal

def decoder(text: str):
    bits = str()
    both_ct = changes + targets

    for letter in text:
        if letter in both_ct:
            if letter in changes:
                bits += "1"
            else:
                bits += "0"
    bits= bits[::-1]
    return bits, int(bits, 2)
