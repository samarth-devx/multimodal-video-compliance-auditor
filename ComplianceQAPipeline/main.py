import logging
import sys
import uuid

from backend.src.graph.workflow import build_graph

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def main(url: str):
    video_id = f"vid_{uuid.uuid4().hex[:8]}"
    state = build_graph().invoke({"video_url": url, "video_id": video_id, "errors": []})

    if state.get("errors"):
        print("ERROR:", "; ".join(state["errors"]))
        return
    print(f"\nStatus: {state['status']}\n")
    for v in state["violations"]:
        print(f"- [{v.severity.value}] {v.category.value} @ {v.timestamp or '?'}: {v.description}")
        print(f"    evidence: {v.evidence}")
    print(f"\n{state['report']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "https://youtu.be/dT7S75eYhcQ")