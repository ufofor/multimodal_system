"""Quick CLI to ingest a file and ask questions.

Usage:
  python run_cli.py <file>            # ingest + chat
  python run_cli.py <file> --debug    # show extracted text and retrieved chunks
  python run_cli.py --reset           # wipe Pinecone index and exit
"""
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.core.vector_store import VectorStore
from src.agents.router_agent import route_and_ingest, supported_extensions
from src.agents.rag_agent import query
from src.agents.vision_agent import _extract_text_from_image, SUPPORTED_EXTENSIONS as IMAGE_EXTENSIONS


def main():
    args = sys.argv[1:]

    # --reset: wipe Pinecone index
    if "--reset" in args:
        store = VectorStore()
        store._index.delete(delete_all=True)
        print("Pinecone index wiped.")
        sys.exit(0)

    debug = "--debug" in args
    file_args = [a for a in args if not a.startswith("--")]

    if not file_args:
        print("Usage: python run_cli.py <file> [--debug] [--reset]")
        sys.exit(1)

    file_path = Path(file_args[0])
    if not file_path.exists():
        print(f"File not found: {file_path}")
        sys.exit(1)

    store = VectorStore(persist_dir=".chromadb")

    # For images in debug mode, show extracted text before indexing
    if debug and file_path.suffix.lower() in IMAGE_EXTENSIONS:
        print(f"\n[DEBUG] Extracting text from {file_path.name} via Claude Vision...")
        extracted = _extract_text_from_image(file_path)
        print(f"\n[DEBUG] Extracted text:\n{'='*60}\n{extracted}\n{'='*60}\n")

    print(f"\nIngesting: {file_path.name} ...")
    result = route_and_ingest(file_path, store)

    modality = result.get("modality", "text")
    print(f"Done. {result['chunks_stored']} chunks indexed (modality: {modality}).")
    print(f"Total chunks in store: {store.count()}\n")
    print("Ask questions about your document. Type 'quit' to exit.\n")

    history = []
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue

        result = query(question, store, conversation_history=history, debug=debug)

        print(f"\nAssistant: {result['answer']}")
        if result["sources"]:
            sources_str = ", ".join(
                f"{s['source']} p.{s['page']} [{s['modality']}]" for s in result["sources"]
            )
            print(f"Sources: {sources_str}")
        if debug:
            print(f"[DEBUG] Chunks used: {result['chunks_used']}")
            for i, chunk in enumerate(result.get("debug_chunks", []), 1):
                print(f"[DEBUG] Chunk {i}: {chunk[:200]}...")
        print()

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": result["answer"]})


if __name__ == "__main__":
    main()
