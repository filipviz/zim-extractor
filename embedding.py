import sys
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer

# Constants
matryoshka_dim = 512
embedding_model = "nomic-ai/nomic-embed-text-v1.5"

# Determine which device to use
if torch.cuda.is_available() and torch.backends.cuda.is_built():
    device = "cuda"
elif torch.backends.mps.is_available() and torch.backends.mps.is_built():
    device = "mps"
elif torch.cpu.is_available():
    device = "cpu"
else:
    print("No available torch device found.")
    sys.exit(1)

torch.set_default_device(device)
print(f"Using device: {device}.")

# Load the sentence embedding model.
model = SentenceTransformer(embedding_model, trust_remote_code=True, device=device)

def embed_chunks(chunks: list[str]):
    embeddings = model.encode(chunks, convert_to_tensor=True)
    embeddings = F.layer_norm(embeddings, normalized_shape=(embeddings.shape[1],))
    embeddings = embeddings[:, :matryoshka_dim]
    embeddings = F.normalize(embeddings, p=2, dim=1)
    
    return embeddings
    