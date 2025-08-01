from agents import (
    Agent, Runner, AsyncOpenAI,
    OpenAIChatCompletionsModel, function_tool,
    RunContextWrapper, TResponseInputItem, GuardrailFunctionOutput,
    input_guardrail,output_guardrail , set_tracing_disabled
)
from openai.types.responses import ResponseTextDeltaEvent
import asyncio
from dotenv import load_dotenv
from pydantic import BaseModel
import os

# Load .env
load_dotenv()

# Set tracing disabled
set_tracing_disabled(disabled=True)


gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# Set up Gemini provider and model
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider,
)

# Context model
class UserContext(BaseModel):
    name: str
    is_premium_user: bool
    issue_type: str
    user_id: str

#  Guardrail schema
class GuardrailOutput(BaseModel):
    apology: bool
    reasoning: str
    output: str

#  Input Guardrail
input_guardrail_agent = Agent(
    name="InputGuardrailAgent",
    instructions="Reject input that contains an apology.",
    model=model,
    output_type=GuardrailOutput,
)

@input_guardrail
async def input_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrail_agent, input)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.apology
    )

#  Output Guardrail
output_guardrail_agent = Agent(
    name="OutputGuardrailAgent",
    instructions="Reject output that contains an apology.",
    model=model,
    output_type=GuardrailOutput,
)

@output_guardrail
async def output_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    input: str | list[TResponseInputItem]
) -> GuardrailFunctionOutput:
    result = await Runner.run(output_guardrail_agent, input)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.apology
    )

#  Refund tool
@function_tool(is_enabled=lambda wrapper, agent: wrapper.context.is_premium_user)
def refund(wrapper: RunContextWrapper[UserContext]) -> str:
    if wrapper.context.is_premium_user:
        return f"✅ Refund has been successfully processed for user {wrapper.context.name} (ID: {wrapper.context.user_id})."
    else:
        return "You are not a premium user, you are not eligible for a refund."

#  Restart Service tool
@function_tool(is_enabled=lambda wrapper, agent: wrapper.context.issue_type == "technical")
def restart_service(wrapper: RunContextWrapper[UserContext]) -> str:
    if wrapper.context.issue_type == "technical":
        return f"Service restarted for technical issue for user {wrapper.context.name} (ID: {wrapper.context.user_id})"
    else:
        return "Service restart not applicable for non-technical issues."


#  User context setup
context_data = UserContext(
    name="Muhammad Soban",
    is_premium_user=True,
    issue_type="technical",
    user_id="12363187"
)

#  Billing Agent
billing_agent = Agent(
    name="billing_agent",
    model=model,
    instructions="""
    You are a billing agent. If the user is a premium user (based on context), call the `refund` tool immediately.
    Do not ask again for confirmation. Just respond using the tool if eligible.
    """,
    tools=[refund],
)

#  Technical Support Agent
technical_support_agent = Agent(
    name="technical_support_agent",
    model=model,
    instructions="""
    You are a technical support agent. Your job is to assist users with technical issues.
    If the user’s context indicates the issue is technical (context.issue_type == 'technical'), immediately call the `restart_service` tool.
    Do not ask the user to confirm the issue again. Simply respond with the result of the tool execution if applicable.
    If the issue is not technical, inform the user that you cannot assist and defer to another agent.
    """,
    tools=[restart_service],
)

#  Triage Agent with guardrails
triage_agent = Agent(
    name="triage_agent",
    model=model,
    instructions="""
    You are a triage agent. Analyze the user input and decide whether it should go to billing or technical support.
    Use billing agent for refund/payment issues.
    Use technical support agent for service-related issues.
    """,
    handoffs=[billing_agent, technical_support_agent],
    input_guardrails=[input_guardrail],
    output_guardrails=[output_guardrail],
)

async def main():
    #  User input
    user_input = input("Please enter your query: ")
    result = Runner.run_streamed(
        triage_agent,
        user_input,
        context=context_data
    )
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    
if __name__ == "__main__":
    asyncio.run(main())
    


