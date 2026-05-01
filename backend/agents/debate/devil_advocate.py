import json
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import GraphState, AgentStep
from config.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0,
)

async def devil_advocate_node(state: GraphState) -> dict:
    step = AgentStep(
        agent_name="devil_advocate",
        status="running",
        summary="Generating counter-argument...",
        detail="Critiquing evidence to construct a devil's advocate position."
    )
    
    evidence_text = "\n".join([f"- {e['source']}: {e['passage']}" for e in state.get("evidence", [])])
    
    prompt = (
        "You are a Devil's Advocate agent analyzing a financial query.\n"
        f"Query: {state.get('query', '')}\n"
        "Your task is to construct a critical counter-argument based on the following evidence:\n"
        f"{evidence_text}\n\n"
        "Focus on the risks, downsides, constraints, and negative factors. Provide a skeptical viewpoint. Keep it concise."
    )
    
    try:
        response = await llm.ainvoke(prompt)
        arg = response.content.strip()
    except Exception as e:
        arg = f"Failed to generate counter-argument: {str(e)}"

    step["status"] = "done"
    step["summary"] = "Counter-argument generated"
    step["prompt"] = prompt
    step["argument"] = arg
    
    return {
        "devil_arg": arg,
        "steps": [step]
    }
