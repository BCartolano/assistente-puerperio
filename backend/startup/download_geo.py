"""Download opcional do geo Parquet do Azure Blob no start (sem versionar dados)."""
import os
from pathlib import Path

# Raiz do projeto (backend/startup -> backend -> raiz)
BASE = Path(__file__).resolve().parent.parent.parent
GEO_BASE = BASE / "data" / "geo"


def download_from_azure(container: str, blob: str, dest: Path) -> bool:
    try:
        from azure.storage.blob import BlobServiceClient
    except Exception:
        print("[AZ] azure-storage-blob ausente; pulando download.")
        return False
    conn = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn:
        print("[AZ] CONNECTION_STRING ausente; pulando download.")
        return False
    svc = BlobServiceClient.from_connection_string(conn)
    blob_client = svc.get_blob_client(container=container, blob=blob)
    if not blob_client.exists():
        print(f"[AZ] blob não existe: {container}/{blob}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "wb") as f:
        data = blob_client.download_blob()
        f.write(data.readall())
    print(f"[AZ] baixado {container}/{blob} -> {dest}")
    return True


def ensure_geo() -> None:
    """Se não existir min nem full parquet local, tenta baixar do Azure Blob."""
    minp = GEO_BASE / "hospitals_geo.min.parquet"
    full = GEO_BASE / "hospitals_geo.parquet"
    if minp.exists() or full.exists():
        return
    container = os.getenv("AZURE_BLOB_CONTAINER", "geo")
    blob = os.getenv("AZURE_GEO_BLOB", "hospitals_geo.min.parquet")
    download_from_azure(container, blob, minp)


if __name__ == "__main__":
    ensure_geo()
