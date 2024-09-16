# Chroma DB Setup and Usage Guide

## Installation

To install Chroma DB, run the following command:

```bash
pip install chromadb
```

## Basic Usage

### Importing and Initializing

```python
from chromadb import Client

# For in-memory database (development)
client = Client()

# For persistent storage (production)
from chromadb import PersistentClient
client = PersistentClient(path="/path/to/save")
```

### Creating a Collection

```python
collection = client.create_collection("my_collection")
```

### Adding Data

```python
collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my_source"}, {"source": "my_source"}],
    ids=["id1", "id2"]
)
```

### Querying Data

```python
results = collection.query(
    query_texts=["This is a query document"],
    n_results=2,
    where={"metadata_field": "metadata_value"}
)
```

### Updating and Deleting Data

```python
# Update
collection.update(
    ids=["id1"],
    documents=["This is an updated document"],
    metadatas=[{"source": "updated_source"}]
)

# Delete
collection.delete(ids=["id2"])
```

## Advanced Features

### Metadata Filtering

Use the `where` parameter in queries for metadata filtering:

```python
results = collection.query(
    query_texts=["Query text"],
    where={"metadata_field": {"$gt": 0.5}}
)
```

### Distance Functions

Specify the distance function in queries:

```python
results = collection.query(
    query_texts=["Query text"],
    n_results=2,
    distance_function="cosine"  # Options: "l2", "ip", "cosine"
)
```

For more detailed information, refer to the [official Chroma DB documentation](https://docs.trychroma.com/).
