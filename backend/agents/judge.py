import json
from langchain_google_genai import ChatGoogleGenerativeAI
from graph.state import GraphState, AgentStep
from config.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0,
)

async def judge_node(state: GraphState) -> dict:
    step = AgentStep(
        agent_name="judge",
        status="running",
        summary="Evaluating arguments...",
        detail="Synthesizing advocate and devil's advocate arguments."
    )
    
    query = state.get("query", "")
    adv = state.get("advocate_arg", "")
    dev = state.get("devil_arg", "")
    
    prompt = (
        "You are an impartial Judge evaluating a financial decision.\n"
        f"Original Query: {query}\n\n"
        f"Advocate's Argument (Pro):\n{adv}\n\n"
        f"Devil's Advocate Argument (Con):\n{dev}\n\n"
        "Your task is to synthesize these viewpoints, provide a well-reasoned final decision, "
        "and score your confidence and the fairness (balance) of the arguments.\n"
        'Return ONLY valid JSON in this exact format (no markdown, no extra text):\n'
        '{"final_decision": "string", "confidence": float_0_to_1, "fairness_score": float_0_to_1, "reasoning": "string"}'
    )
    
    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3].strip()

        data = json.loads(content)
        decision = data.get("final_decision", "Failed to parse final decision.")
        confidence = data.get("confidence", 0.0)
        bias_report = {"fairness": data.get("fairness_score", 0.0), "reason": data.get("reasoning", "")}
        error = None
    except Exception as e:
        decision = f"Judge failed to evaluate: {str(e)}"
        confidence = 0.0
        bias_report = {}
        error = str(e)

    step["status"] = "done"
    step["summary"] = "Judge rendered a final decision"
    
    # State expects these keys
    return {
        "final_decision": decision,
        "confidence": confidence,
        "bias_report": bias_report,
        "steps": [step]
    }
