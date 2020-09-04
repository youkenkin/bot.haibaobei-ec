import json

a = "Fmaj7=113231_8"
print (a[-1])

with open("data/guitar-chords.json", "rt") as f:
    chord_charts = json.load(f)
    f.close()

new_chord_charts = {}
for key in chord_charts.keys():
    new_cc = sorted(chord_charts[key], key=lambda kv: kv['name'][-1] )
    new_chord_charts[key] = new_cc

with open('data/sorted_guitar_chords.json', "wt") as f:
    json.dump(new_chord_charts, f)
    f.close()