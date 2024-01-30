def tete(**args):
    text = "hello, {name}!"
    text = text.format(**args)
    print(text)


tete(name="Sel")