"""
Quick end-to-end test for the Task 1 LangGraph pipeline.

Run from the backend/ directory with PYTHONPATH set:
    cd backend
    export PYTHONPATH=$(pwd)
    python test_graph.py
"""
import asyncio
from graph.nodes import build_graph


async def main():
    graph = build_graph()

    initial_state = {
        "query": "Will Nifty 50 have a bear market next month?",
        "user_id": "test_user",
        "tier": "free",
        "sub_tasks": [],
        "steps": [],
        "evidence": [],
        "advocate_arg": "",
        "devil_arg": "",
        "final_decision": "",
        "confidence": 0.0,
        "bias_report": {},
        "error": None,
    }

    print("=" * 60)
    print("Executing LangGraph: Planner → 4 Parallel Workers")
    print("=" * 60)

    # stream_mode="updates" (default) yields {node_name: state_delta} dicts
    async for event in graph.astream(initial_state, stream_mode="updates"):
        for node_name, update in event.items():
            print(f"\n--- Node: {node_name} ---")

            if not update:
                continue

            steps = update.get("steps", [])
            for s in steps:
                status_icon = "✓" if s["status"] == "done" else "⟳"
                print(f"  [{status_icon}] {s['agent_name']}: {s['summary']}")

            if node_name == "planner" and update.get("sub_tasks"):
                print(f"  Sub-tasks:")
                for i, t in enumerate(update["sub_tasks"], 1):
                    print(f"    {i}. {t}")

            ev_list = update.get("evidence", [])
            if ev_list:
                print(f"  Evidence ({len(ev_list)} item(s)):")
                for e in ev_list:
                    print(f"    • [{e['relevance_score']:.2f}] {e['source']}")

            if update.get("error"):
                print(f"  ⚠ Error: {update['error']}")

    print("\n" + "=" * 60)
    print("Graph execution complete.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
