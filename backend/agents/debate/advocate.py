import json
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import GraphState, AgentStep
from config.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0,
)

async def advocate_node(state: GraphState) -> dict:
    step = AgentStep(
        agent_name="advocate",
        status="running",
        summary="Generating favorable argument...",
        detail="Analyzing evidence to construct a positive case."
    )
    
    evidence_text = "\n".join([f"- {e['source']}: {e['passage']}" for e in state.get("evidence", [])])
    
    prompt = (
        "You are an Advocate agent analyzing a financial query.\n"
        f"Query: {state.get('query', '')}\n"
        "Your task is to construct a strong, favorable argument based on the following evidence:\n"
        f"{evidence_text}\n\n"
        "Focus on the positives, opportunities, and constructive aspects. Keep it concise."
    )
    
    try:
        response = await llm.ainvoke(prompt)
        arg = response.content.strip()
    except Exception as e:
        arg = f"Failed to generate argument: {str(e)}"

    step["status"] = "done"
    step["summary"] = "Advocate argument generated"
    
    return {
        "advocate_arg": arg,
        "steps": [step]
    }
