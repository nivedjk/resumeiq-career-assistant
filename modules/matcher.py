from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def match_score(resume_text, jd_text):

    resume_embedding = model.encode(
        [resume_text]
    )

    jd_embedding = model.encode(
        [jd_text]
    )

    score = cosine_similarity(
        resume_embedding,
        jd_embedding
    )[0][0]

    return round(score * 100, 2)