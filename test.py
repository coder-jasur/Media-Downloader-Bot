from faster_whisper import WhisperModel

model_size = "tiny"   # yoki "tiny" agar kam resurs bo'lsa
model = WhisperModel(model_size, device="cpu")  # agar GPU bo'lsa device="cuda"

segments, info = model.transcribe("audiaudiofull.ogg", language="uz", beam_size=5)
text = " ".join([seg.text for seg in segments])
print(text)
