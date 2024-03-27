import psycopg2
from configparser import ConfigParser
from transformers import BertModel, BertTokenizer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Database configuration parser
def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file.')
    return db

# Load metadata from the database
def load_metadata():
    conn = None
    metadata = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT id, title, url, description FROM ecommerce_metadata.metadata;")
        metadata = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return metadata

# Load BERT model and tokenizer
def load_bert_model():
    model_name = 'bert-base-uncased'
    tokenizer = BertTokenizer.from_pretrained(model_name)
    model = BertModel.from_pretrained(model_name)
    return tokenizer, model

# Serialize embeddings and update the database
def serialize_embeddings_and_update_db(metadata, tokenizer, model):
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        for item in metadata:
            metadata_id, title, url, desc = item
            inputs = tokenizer(desc, return_tensors="pt", padding=True, truncation=True, max_length=512)
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy()
            serialized_embedding = pickle.dumps(embedding)
            cur.execute("UPDATE ecommerce_metadata.metadata SET bert_embedding = %s WHERE id = %s;", (serialized_embedding, metadata_id))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

# Load dataset embeddings and names for recommendation
def load_dataset_embeddings_and_names():
    conn = None
    dataset_embeddings = []
    dataset_titles = []
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT title, bert_embedding FROM ecommerce_metadata.metadata;")
        for title, embedding in cur.fetchall():
            dataset_titles.append(title)
            dataset_embeddings.append(pickle.loads(embedding))
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return np.vstack(dataset_embeddings), dataset_titles  # Ensure embeddings are properly stacked

# Recommend datasets based on query
def recommend_datasets(query, tokenizer, model):
    dataset_embeddings, dataset_titles = load_dataset_embeddings_and_names()
    query_embedding = generate_embeddings(tokenizer, model, [query])[0].reshape(1, -1)  # Generate query embedding
    similarities = cosine_similarity(query_embedding, dataset_embeddings).flatten()  # Calculate cosine similarities
    recommended_indices = np.argsort(similarities)[::-1]  # Sort datasets by similarity
    print("Top recommended datasets:")  # Print top 5 recommendations
    for idx in recommended_indices[:5]:
        print(f"Dataset: {dataset_titles[idx]}, Similarity: {similarities[idx]}")

# Generate embeddings for metadata descriptions
def generate_embeddings(tokenizer, model, descriptions):
    embeddings = []
    for desc in descriptions:
        inputs = tokenizer(desc, return_tensors="pt", padding=True, truncation=True, max_length=512)
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).detach().numpy().squeeze()  # Ensure embedding is squeezed
        embeddings.append(embedding)
    return np.array(embeddings)

def main():
    metadata = load_metadata()  # Load metadata
    tokenizer, model = load_bert_model()  # Load BERT tokenizer and model
    serialize_embeddings_and_update_db(metadata, tokenizer, model)  # Update database with embeddings
    recommend_datasets("women's fashion", tokenizer, model)  # Example recommendation

if __name__ == "__main__":
    main()
