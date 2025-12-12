print("Importing CrossEncoder...")
from sentence_transformers import CrossEncoder
import time

print("Initializing Model...")
start = time.time()
model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
print(f"Model loaded in {time.time() - start:.2f}s")

pairs = [('How many people live in Berlin?', 'Berlin had a population of 3,520,031 registered inhabitants in an area of 891.82 square kilometers.')]
print("Predicting...")
scores = model.predict(pairs)
print(f"Scores: {scores}")
print("Success!")
