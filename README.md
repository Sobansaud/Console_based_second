# 🤖 Console-Based Support Agent System using OpenAI Agents SDK

####     👤 Author
#       Muhammad Soban

This project was created as part of a class assignment demonstrating multi-agent systems using the OpenAI Agents SDK.



This project is a **multi-agent support system** built entirely in the console using the **OpenAI Agents SDK**. It simulates a real-world customer service system that can intelligently route and respond to user queries like **billing issues**, **technical problems**, and more.

Designed as part of an academic assignment, this system demonstrates the use of **triage logic**, **context-aware tool activation**, **agent handoffs**, **guardrails**, and **live streaming output** — all with a clean and modular Python implementation.

---

## 🎯 Objective

The goal of this project is to implement a **console-based AI support system** that:

- Uses at least 3 agents (triage + 2 specialists)
- Routes user input dynamically
- Enables/disables tools based on context
- Shares context between agents
- Uses guardrails to prevent inappropriate input/output
- Displays real-time streaming output

---

## 🧠 System Architecture

### 👨‍🔧 Agents

| Agent                  | Description                                                                 |
|------------------------|-----------------------------------------------------------------------------|
| `triage_agent`         | Analyzes the user query and forwards it to the appropriate specialist agent |
| `billing_agent`        | Handles refund requests (only for premium users)                            |
| `technical_support_agent` | Solves technical issues like service restarts                             |

---

### 🧰 Tools

| Tool              | Purpose                                          | Activation Condition                  |
|-------------------|--------------------------------------------------|----------------------------------------|
| `refund()`        | Process a refund                                 | Only if `is_premium_user == True`     |
| `restart_service()` | Restart the user's service                     | Only if `issue_type == "technical"`   |

---

### 📦 Context Model

Implemented using **Pydantic**, the context object carries:

- `name`: User's name
- `is_premium_user`: Boolean flag
- `issue_type`: Either "billing", "technical", etc.
- `user_id`: Unique identifier for the user

This context is automatically passed to all agents and tools.

---

### 🛡️ Guardrails

| Guardrail         | Purpose                                                 |
|-------------------|---------------------------------------------------------|
| `input_guardrail` | Blocks user inputs that contain apology phrases         |
| `output_guardrail`| Ensures the system never replies with apologies         |

Both are powered by a custom schema (`GuardrailOutput`) and backed by Agents SDK functionality.


### ⚡ Real-Time Streaming Output

The system uses `Runner.run_streamed()` and `stream_events()` to simulate live AI responses, enhancing realism in the console.

### ⚡ 📚 Technologies Used
Python 3.11+

OpenAI Agents SDK

Pydantic

dotenv

asyncio

Gemini API (OpenAI-compatible endpoint)

