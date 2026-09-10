from functools import lru_cache
from pinecone import Pinecone, ServerlessSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from src.config import get_settings


@lru_cache
def get_embeddings():
    s = get_settings()
    if not s.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    return OpenAIEmbeddings(
        api_key=s.openai_api_key,
        model=s.embedding_model,
        dimensions=s.embedding_dimension,
    )




def get_pinecone_client():
    s = get_settings()
    if not s.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY is not configured")
    return Pinecone(api_key=s.pinecone_api_key)




def ensure_index():
    """Create the Pinecone index if needed and verify embedding dimension compatibility."""
    s = get_settings()
    pc = get_pinecone_client()
    existing = {x.name for x in pc.list_indexes()}

    if s.pinecone_index_name not in existing:
        pc.create_index(
            name=s.pinecone_index_name,
            dimension=s.embedding_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud=s.pinecone_cloud, region=s.pinecone_region),
        )
    else:
        desc = pc.describe_index(s.pinecone_index_name)
        existing_dimension = getattr(desc, "dimension", None)
        if existing_dimension is None and isinstance(desc, dict):
            existing_dimension = desc.get("dimension")
        if existing_dimension and int(existing_dimension) != s.embedding_dimension:
            raise RuntimeError(
                f"Pinecone index '{s.pinecone_index_name}' has dimension {existing_dimension}, "
                f"but {s.embedding_model} is configured for {s.embedding_dimension}. "
                "Use a new index name or recreate the index with the correct dimension."
            )

    return pc.Index(s.pinecone_index_name)



def get_vector_store():
    s = get_settings()
    index = ensure_index()
    return PineconeVectorStore(
        index=index,
        embedding=get_embeddings(),
        namespace=s.pinecone_namespace,
    )




def get_retriever():
    s = get_settings()
    return get_vector_store().as_retriever(search_kwargs={"k": s.top_k})
