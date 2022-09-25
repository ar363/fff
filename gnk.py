import os
from time import time
import genanki

ddeck = genanki.Deck(int(time()), name="B Modules - Haloalkanes and Haloarenes")

ld = os.listdir("temp/bhnh/")

for i in range(0, len(ld), 2):
    print(i)
    ddeck.add_note(
        genanki.Note(
            model=genanki.BASIC_MODEL,
            fields=[f'<img src="{ld[i]}">', f'<img src="{ld[i+1]}">'],
        )
    )

pkg = genanki.Package()
pkg.media_files = ["" + i for i in os.listdir("temp/bhnh/")]

pkg.decks = [ddeck]

pkg.write_to_file("bhh.apkg")
