import json
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import GraphState, AgentStep
from config.settings import settings

# langchain-google-genai v4+ uses 'google_api_key' kwarg (confirmed still valid)
# but the env var GOOGLE_API_KEY is preferred; we pass it explicitly to be safe.
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0,
)


async def planner_node(state: GraphState) -> dict:
    """
    Decomposes the raw user query into 2-4 specialist sub-tasks.
    Returns a dict with only the keys this node updates (LangGraph best practice).
    """
    step = AgentStep(
        agent_name="planner",
        status="running",
        summary="Decomposing query into sub-tasks...",
        detail="",
    )

    prompt = (
        "You are a financial query planner. "
        "Decompose the following query into 2-4 specific sub-tasks for specialist agents.\n"
        f"Query: {state['query']}\n\n"
        'Return ONLY valid JSON in this exact format (no markdown, no extra text):\n'
        '{"sub_tasks": ["task1", "task2"]}'
    )

    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()

        # Strip markdown code fences if Gemini wraps the JSON
        if content.startswith("```"):
            # Remove opening fence (```json or ```)
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            # Remove closing fence
            if content.endswith("```"):
                content = content[:-3].strip()

        data = json.loads(content)
        sub_tasks = data.get("sub_tasks", [])
        error = None
    except Exception as e:
        sub_tasks = []
        error = f"Planner failed to parse LLM output: {e}"

    step["status"] = "done"
    step["summary"] = f"Planned {len(sub_tasks)} sub-tasks"
    step["prompt"] = prompt

    return {
        "sub_tasks": sub_tasks,
        "steps": [step],
        "error": error,
    }
