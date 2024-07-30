from PIL       import Image

__all__ = ['writing', 'pictorial', 'decoder']

changes = "apceoixy" #eng
targets = "арсеоіху" #ukr

def to_bits(num: int):
    return [symbol=="1" for symbol in f"{abs(num):b}"]

def writing( text: str, num: int):
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
    pal=list(map(
        lambda x: 20+ x*235,
        to_bits(num)
    ))

    count_cells, rest = divmod(
        (num).bit_length(), 3       #(num).bit_length() = len(pal)
    )

    if rest != 0:
         count_cells += 1
         for i in range(3-rest):
             pal.append(20)

    maket = Image.new(
        "P", #mode
        (5 * count_cells, 2) #size
    )
    maket.putpalette(pal)
    pixlist = maket.load()

    for cell_number in range(count_cells):
#        pixlist[cell_number*5: 5+cell_number*5, 0:1] = cell_number+36
        for a in range(5):
            pixlist[cell_number*5+a, 0] = cell_number+36 #id in palette
            pixlist[cell_number*5+a, 1] = cell_number+36
    return maket, pal

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
