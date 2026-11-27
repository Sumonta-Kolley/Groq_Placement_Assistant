import json
import os
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from tools import ALL_TOOLS, list_application_drafts

if not os.getenv("GROQ_API_KEY"):
    raise RuntimeError(
        "GROQ_API_KEY was not found in your PC environment variables. "
        "Set GROQ_API_KEY and restart your terminal."
    )

TOOL_MAP = {item.name: item for item in ALL_TOOLS}

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(ALL_TOOLS)

SYSTEM_MESSAGE = (
    "You are Campus Opportunity Navigator, a careful college placement assistant. "
    "Use tools for opportunity searches, eligibility, stipend estimates, and draft operations. "
    "Never claim an application was submitted. A saved draft is only for human review. "
    "Do not invent opportunities, requirements, stipend amounts, or tool results. "
    "Explain eligibility using the tool result. Ask for missing details before saving a draft."
)


def ask_navigator(user_question: str) -> str:
    messages = [
        SystemMessage(content=SYSTEM_MESSAGE),
        HumanMessage(content=user_question),
    ]

    # Bound the number of model/tool rounds.
    for _ in range(5):
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)

        if not ai_message.tool_calls:
            return ai_message.content

        for call in ai_message.tool_calls:
            selected_tool = TOOL_MAP.get(call["name"])
            if selected_tool is None:
                result = {"error": "Tool is not registered."}
            else:
                try:
                    result = selected_tool.invoke(call["args"])
                except Exception as error:
                    result = {"error": str(error)}

            messages.append(
                ToolMessage(
                    content=json.dumps(result),
                    tool_call_id=call["id"],
                )
            )

    return "Maximum tool steps reached. Please make the request more specific."


def get_saved_drafts():
    return list_application_drafts.invoke({})