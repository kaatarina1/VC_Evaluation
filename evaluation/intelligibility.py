# pip install openai-whisper jiwer
import whisper
from jiwer import wer, cer
import glob
import os

# Load model
model = whisper.load_model("small")  # or "medium" / "large"

# Reference transcripts (dict: {filename: text})
references = {
    "monitor_en_1.wav": "Good morning, I hope you slept well and that you are ready for a productive day filled with new opportunities.",
    "monitor_en_2.wav": "I would like a cup of coffee with a little milk and no sugar, because I prefer the natural taste.",
    "monitor_en_3.wav": "The weather has been suprisingly warm this week, which makes it perfect for walking in the park.",
    "monitor_en_4.wav": "Could you please help me find the nearest, because I am not familiar with this part of the city.",
    "monitor_en_5.wav": "In the evening, I enjoy reading interesting books, because it helps me relax and forget about daily stress.",
    "monitor_slo_1.wav": "Dobro jutro, upam, da si dobro spal in da si pripravljen na uspešen dan, poln novih priložnosti.",
    "monitor_slo_2.wav": "Rada bi skodelico kave z malo mleka in brez sladkorja, ker imam raje naraven okus.",
    "monitor_slo_3.wav": "Vreme je ta teden presenetljivo toplo, kar je popolno za sprehode v parku.",
    "monitor_slo_4.wav": "Mi lahko prosim pomagaš najti najbližjo avtobusno postajo, ker tega dela mesta ne poznam.",
    "monitor_slo_5.wav": "Zvečer rada berem zanimive knjige, saj mi to pomaga, da se sprostim in pozabim na vsakodnevni stres.",
    # add all...
}


for dir in glob.glob("data/m/*"):
    hypotheses_en, wers_en, cers_en = {}, {}, {}
    hypotheses_sl, wers_sl, cers_sl = {}, {}, {}
    for f in glob.glob(dir + "/*.wav"):
        f = os.path.normpath(f)
        path_parts = f.split(os.sep)
        path = os.path.join(*path_parts)
        path = os.path.normpath(path) 

        lang = path_parts[-1].split("_")[1] == "slo" and "sl" or "en"

        result = model.transcribe(path, language=lang)
        hyp = result["text"].strip()
        ref = references.get(path_parts[-1], "").strip()
        if (lang == "en"):
            hypotheses_en[f] = hyp
            wers_en[f] = wer(ref, hyp)
            cers_en[f] = cer(ref, hyp)
        else:
            hypotheses_sl[f] = hyp
            wers_sl[f] = wer(ref, hyp)
            cers_sl[f] = cer(ref, hyp)
    
    print("Average English Male WER for ", dir, ":", sum(wers_en.values())/len(wers_en))
    print("Average English Male CER: ", dir, ":", sum(cers_en.values())/len(cers_en))
    print("Average Slovenian Male WER for ", dir, ":", sum(wers_sl.values())/len(wers_sl))
    print("Average Slovenian Male CER: ", dir, ":", sum(cers_sl.values())/len(cers_sl))

for dir in glob.glob("data/f/*"):
    hypotheses_en, wers_en, cers_en = {}, {}, {}
    hypotheses_sl, wers_sl, cers_sl = {}, {}, {}
    for f in glob.glob(dir + "/*.wav"):
        f = os.path.normpath(f)
        path_parts = f.split(os.sep)
        path = os.path.join(*path_parts)
        path = os.path.normpath(path) 

        lang = path_parts[-1].split("_")[1] == "slo" and "sl" or "en"

        result = model.transcribe(path, language=lang)
        hyp = result["text"].strip()
        ref = references.get(path_parts[-1], "").strip()
        if (lang == "en"):
            hypotheses_en[f] = hyp
            wers_en[f] = wer(ref, hyp)
            cers_en[f] = cer(ref, hyp)
        else:
            hypotheses_sl[f] = hyp
            wers_sl[f] = wer(ref, hyp)
            cers_sl[f] = cer(ref, hyp)
    
    print("Average English Female WER for ", dir, ":", sum(wers_en.values())/len(wers_en))
    print("Average English Female CER: ", dir, ":", sum(cers_en.values())/len(cers_en))
    print("Average Slovenian Female WER for ", dir, ":", sum(wers_sl.values())/len(wers_sl))
    print("Average Slovenian Female CER: ", dir, ":", sum(cers_sl.values())/len(cers_sl))

