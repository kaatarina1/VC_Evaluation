# pip install openai-whisper jiwer pandas praat-parselmouth librosa numpy
import whisper
from jiwer import wer, cer
import glob
import os
import pandas as pd
import numpy as np
import librosa
from pymcd.mcd import Calculate_MCD
import pyworld as pw
from scipy.spatial.distance import euclidean
from scipy import stats
from fastdtw import fastdtw

# ----------------------
# Load Whisper model
# ----------------------
model = whisper.load_model("small")  # change to "medium" / "large" for better accuracy

# ----------------------
# Reference transcripts
# ----------------------
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

# ----------------------
# Helper Functions
# ----------------------
def transcribe_and_score(path, lang, ref):
    """Transcribe file with Whisper, return hypothesis, WER, CER"""
    result = model.transcribe(path, language=lang)
    hyp = result["text"].strip()
    return hyp, wer(ref, hyp), cer(ref, hyp)

def extract_f0(audio_path, sr=24000):
    y, sr = librosa.load(audio_path, sr=sr)
    y = y.astype(np.float64)
    f0, time_axis = pw.dio(y, sr, frame_period=5.0)
    return pw.stonemask(y, f0, time_axis, sr)

def prosody_metrics(src_path, conv_path):
    f0_src = extract_f0(src_path)
    f0_conv = extract_f0(conv_path)

    # Truncate to the shorter length
    min_length = min(len(f0_src), len(f0_conv))
    f0_src = f0_src[:min_length]
    f0_conv = f0_conv[:min_length]

    # Create boolean masks for voiced frames
    voiced_src = f0_src > 0
    voiced_conv = f0_conv > 0

    # Find the intersection: frames that are voiced in BOTH sequences
    valid_voiced_frames = voiced_src & voiced_conv

    # Apply the mask and FORCE proper 1D array conversion
    f0_src_voiced = np.array(f0_src[valid_voiced_frames], dtype=np.float64)
    f0_conv_voiced = np.array(f0_conv[valid_voiced_frames], dtype=np.float64)

    # Check if we have enough data
    if len(f0_src_voiced) < 10 or len(f0_conv_voiced) < 10:
        print(f"Not enough voiced frames (src: {len(f0_src_voiced)}, conv: {len(f0_conv_voiced)})")
        f0_correlation = 0.0
        return f0_correlation
    else:
        # Reshape for DTW - ensure proper 2D arrays
        f0_src_voiced = f0_src_voiced.reshape(-1, 1)
        f0_conv_voiced = f0_conv_voiced.reshape(-1, 1)
                
        # Perform DTW
        try:
            distance, path = fastdtw(f0_src_voiced, f0_conv_voiced, dist=euclidean)
            
            aligned_f0_src = []
            aligned_f0_conv = []
            for i, j in path:
                aligned_f0_src.append(f0_src_voiced[i, 0])  # Use proper 2D indexing
                aligned_f0_conv.append(f0_conv_voiced[j, 0])
            
            aligned_f0_src = np.array(aligned_f0_src)
            aligned_f0_conv = np.array(aligned_f0_conv)
            
            f0_correlation, p_value = stats.pearsonr(aligned_f0_src, aligned_f0_conv)
            return f0_correlation
            
        except Exception as e:
            print(f"DTW failed: {e}")
            # Fallback to simple correlation
            f0_correlation, p_value = stats.pearsonr(f0_src_voiced, f0_conv_voiced)
            return f0_correlation

def spectral_distortion(src_path, conv_path):
    """Wrapper for MCD between two files"""
    try:
        mcd_toolbox = Calculate_MCD(MCD_mode="dtw")
        # Calculate MCD
        mcd_value = mcd_toolbox.calculate_mcd(src_path, conv_path)
        return mcd_value
    except Exception as e:
        print(f"⚠️ MCD error for {conv_path}: {e}")
        return np.nan

# ----------------------
# Evaluation Loop
# ----------------------
def eval_dir(input_dir, output_dir, gender, all_results):
    """Evaluate all voices in a directory and append results"""
    references = references_male if gender.lower() == "male" else references_female

    for conv_dir in glob.glob(os.path.join(output_dir, "*")):
        conv_name = os.path.basename(conv_dir)

        for f in glob.glob(os.path.join(conv_dir, "*.wav")):
            # Input file (baseline)
            f_input = f.replace(output_dir, input_dir)
            f_input = f_input.replace("monitor", "input")
            f_input_arr = f_input.split(os.sep)
            f_input_arr = f_input_arr[:-2] + f_input_arr[-1:]
            input_f = os.path.abspath(os.path.join(*f_input_arr))

            f = os.path.abspath(f)
            fname = os.path.basename(f)

            # Reference text
            ref = references.get(fname, "").strip()
            if not ref:
                print(f"⚠️ No reference for {fname}, skipping")
                continue

            lang = "sl" if "_slo" in fname else "en"

            # WER / CER
            hyp_in, wer_in, cer_in = transcribe_and_score(input_f, lang, ref)
            hyp_out, wer_out, cer_out = transcribe_and_score(f, lang, ref)

            # Relative WER/CER
            rel_wer = wer_out / wer_in if wer_in > 0 else wer_out
            rel_cer = cer_out / cer_in if cer_in > 0 else cer_out

            # Prosody
            pitch_corr = prosody_metrics(input_f, f)

            # Spectral Distortion
            mcd_val = spectral_distortion(input_f, f)

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
                "rel_cer": rel_cer,
                "pitch_corr": pitch_corr,
                "mcd": mcd_val
            })

# ----------------------
# Run Evaluation
# ----------------------
results = []
eval_dir("inputs\\m", "data\\m", "Male", results)
eval_dir("inputs\\f", "data\\f", "Female", results)

df = pd.DataFrame(results)
df.to_csv("voice_conversion_eval.csv", index=False, encoding="utf-8")

print("✅ Saved results to voice_conversion_eval.csv")
print(df.head())
