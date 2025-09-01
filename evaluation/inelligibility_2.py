# pip install openai-whisper jiwer pandas
import whisper
from jiwer import wer, cer
import glob
import os
import pandas as pd
from pymcd.mcd import Calculate_MCD

# Load Whisper model (small is OK for eval, medium/large = more accurate)
model = whisper.load_model("small")

# Reference transcripts
references_male = {
    "monitor_en_1.wav": "Good morning, I hope you slept well and that you are ready for a productive day filled with new opportunities.",
    "monitor_en_2.wav": "I would like a cup of coffee with a little milk and no sugar, because I prefer the natural taste.",
    "monitor_en_3.wav": "The weather has been suprisingly warm this week, which makes it perfect for walking in the park.",
    "monitor_en_4.wav": "Could you please help me find the nearest, because I am not familiar with this part of the city.",
    "monitor_en_5.wav": "In the evening, I enjoy reading interesting books, because it helps me relax and forget about daily stress.",
    "monitor_slo_1.wav": "Dobro jutro, upam, da si dobro spal in da si pripravljen na uspešen dan, poln novih priložnosti.",
    "monitor_slo_2.wav": "Rad bi skodelico kave z malo mleka in brez sladkorja, ker imam raje naraven okus.",
    "monitor_slo_3.wav": "Vreme je ta teden presenetljivo toplo, kar je popolno za sprehode v parku.",
    "monitor_slo_4.wav": "Mi lahko prosim pomagaš najti najbližjo avtobusno postajo, ker tega dela mesta ne poznam.",
    "monitor_slo_5.wav": "Zvečer rad berem zanimive knjige, ker mi to pomaga, da se sprostim in pozabim na vsakodnevni stres.",
}

references_female = {
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
}


def transcribe_and_score(path, lang, ref):
    """Transcribe file with Whisper, return hypothesis, WER, CER"""
    path = os.path.abspath(os.path.normpath(path))
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")
    
    result = model.transcribe(path, language=lang)
    hyp = result["text"].strip()
    return hyp, wer(ref, hyp), cer(ref, hyp)


def eval_dir(input_dir, output_dir, gender, all_results):
    """Evaluate all voices in a directory and append results per file"""
    # Choose references depending on gender
    if gender.lower() == "male":
        references = references_male
    else:
        references = references_female

    for conv_dir in glob.glob(os.path.join(output_dir, "*")):
        conv_name = os.path.basename(conv_dir)

        for f in glob.glob(os.path.join(conv_dir, "*.wav")):
            # Input (baseline) file path
            f_input = f.replace(output_dir, input_dir)
            f_input = f_input.replace("monitor", "input")
            f_input_arr = f_input.split("\\")
            f_input_arr = f_input_arr[:-2] + f_input_arr[-1:] 
            f_input = os.path.join(*f_input_arr)
            input_f = os.path.abspath(os.path.normpath(f_input))

            f = os.path.abspath(os.path.normpath(f))
            fname = os.path.basename(f)

            # Skip if no reference
            ref = references.get(fname, "").strip()
            if not ref:
                print(f"⚠️ No reference for {fname}, skipping")
                continue

            # Detect language
            lang = "sl" if "_slo" in fname else "en"

            # Transcribe input (baseline)
            hyp_in, wer_in, cer_in = transcribe_and_score(input_f, lang, ref)
            # Transcribe converted
            hyp_out, wer_out, cer_out = transcribe_and_score(f, lang, ref)

            # Normalized (relative to baseline)
            rel_wer = wer_out / wer_in if wer_in > 0 else wer_out
            rel_cer = cer_out / cer_in if cer_in > 0 else cer_out

            all_results.append({
                "gender": gender,
                "model": conv_name,
                "file": fname,
                "language": lang,
                "ref": ref,
                "hyp_input": hyp_in,
                "wer_input": wer_in,
                "cer_input": cer_in,
                "hyp_output": hyp_out,
                "wer_output": wer_out,
                "cer_output": cer_out,
                "rel_wer": rel_wer,
                "rel_cer": rel_cer
            })


# Collect all results
results = []
eval_dir("inputs\\m", "data\\m", "Male", results)
eval_dir("inputs\\f", "data\\f", "Female", results)

# Save to CSV
df = pd.DataFrame(results)
df.to_csv("voice_conversion_eval.csv", index=False, encoding="utf-8")

print("✅ Saved results to voice_conversion_eval.csv")
print(df.head())
