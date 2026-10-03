"""Spendable AI Chat Generator & Gemini SDK Integration.

Provides context-aware conversational financial intelligence for Spendable.
Ingests real user account context (balance, spendable runway, ML risk scores, recurring commitments, recent activity, active what-if scenario).
Identifies strictly as 'Spendable AI' and enforces strict financial scope guardrails.
"""

import os
import json
from typing import Dict, List, Optional, Any

from app.config import settings
from app.schemas.spendable import ChatMessage, ChatRequest, ChatResponse
from app.services.spendable_service import SpendableService


SPENDABLE_AI_SYSTEM_INSTRUCTION = """You are "Spendable AI", the official intelligent personal financial liquidity assistant embedded inside the Spendable application.

YOUR IDENTITY & NAME:
- You MUST identify yourself as "Spendable AI".
- NEVER refer to yourself as "Gemini", "Google Gemini", "ChatGPT", or "an AI trained by Google".
- INTRODUCTORY GREETING RULE: Include the introduction "I am Spendable AI, your personal financial liquidity assistant" ONLY in your FIRST reply in a conversation. On all subsequent messages/replies, DO NOT repeat "I am Spendable AI..." or re-introduce yourself — answer the user's question directly without repeating your intro greeting line.

YOUR PURPOSE & CAPABILITIES:
- Help users analyze their current liquid balance, safe spendable amount, 30-day forecasted balance trajectory, upcoming recurring commitments, ML cash-flow risk predictions (HistGradientBoosting model), and hypothetical What-If scenario simulations.
- Provide accurate, personalized, concise, actionable financial insights based STRICTLY on the user's REAL account data provided in context below.

STRICT SCOPE & SAFETY GUARDRAILS:
1. STRICT FINANCIAL & SPENDING SCOPE ONLY:
   - You are strictly dedicated to personal finance, money management, spending runway analysis, budgeting, cash flow forecasts, recurring commitments, and what-if financial scenario simulations.
2. REJECT OUT-OF-SCOPE / IRRELEVANT REQUESTS:
   - If the user asks for non-financial or irrelevant tasks (such as "write me a story", "write python code", "who won the game", "tell me a joke", "what is the capital of France", "help with math homework", or any general non-financial prompt), YOU MUST POLITELY DECLINE.
   - For a first prompt refusal, say:
     "I am Spendable AI, your personal financial liquidity assistant. I can only assist with questions related to your spending, finances, money management, or scenario simulations. How can I help you analyze your finances today?"
   - For subsequent prompt refusals, omit the intro and say:
     "I can only assist with questions related to your spending, finances, money management, or scenario simulations. How can I help you analyze your finances today?"
3. TRUTHFULNESS & DATA FAITHFULNESS:
   - Base your answers strictly on the REAL account context provided in the prompt.
   - Always format money amounts using the Bangladeshi Taka symbol (৳).
   - If specific data or context is missing, explain clearly based on observed facts without making up fake data or fake transactions.
4. TONALITY & FORMATTING:
   - Professional, encouraging, clear, and direct.
   - Use bullet points and bold text where helpful for readability.
"""


class SpendableAIChatEngine:
    """Context-aware Spendable AI Chat engine powered by Gemini SDK with deterministic fallback."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        if api_key is not None:
            self.api_key = api_key
        else:
            self.api_key = os.environ.get("GEMINI_API_KEY") or getattr(settings, "GEMINI_API_KEY", "")

        if model_name is not None:
            self.model_name = model_name
        else:
            self.model_name = os.environ.get("GEMINI_MODEL") or getattr(settings, "GEMINI_MODEL", "gemini-3.5-flash-lite")

    def build_account_context(
        self,
        service: SpendableService,
        user_id: str,
        scenario_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Fetch and structure real user account context, ML model predictions, and recent activities."""
        context: Dict[str, Any] = {"user_id": user_id}

        try:
            overview = service.get_overview(user_id=user_id)
            context["current_balance"] = overview.current_balance
            context["spendable_amount"] = overview.spendable_amount
            context["protected_amount"] = overview.protected_amount
            context["liquidity_state"] = overview.liquidity_state.value if hasattr(overview.liquidity_state, "value") else str(overview.liquidity_state)
            context["expected_inflow"] = overview.expected_inflow
            context["expected_outflow"] = overview.expected_outflow
            context["upcoming_commitments"] = overview.upcoming_commitments
            context["forecasted_minimum_balance"] = overview.forecasted_minimum_balance
            context["safety_reserve"] = overview.safety_reserve
            context["snapshot_time"] = overview.snapshot_time
            context["recommendations_count"] = len(overview.recommendations)
        except Exception:
            pass

        try:
            activities_res = service.get_activities(user_id=user_id, limit=15, offset=0)
            tx_list = []
            for item in activities_res.activities:
                tx_list.append({
                    "date": item.timestamp_utc,
                    "counterparty": item.counterparty_name,
                    "category": item.category,
                    "type": item.activity_type,
                    "amount": item.amount,
                    "direction": item.direction,
                    "balance_after": item.balance_after,
                })
            context["recent_transactions"] = tx_list
        except Exception:
            pass

        if scenario_result:
            context["active_simulated_scenario"] = scenario_result

        return context

    def answer(
        self,
        user_message: str,
        chat_history: List[ChatMessage],
        account_context: Dict[str, Any],
    ) -> ChatResponse:
        """Generate response via Gemini SDK or fallback engine."""
        msg_lower = user_message.strip().lower()
        is_first_turn = not chat_history or len(chat_history) <= 1

        # Keyword pre-check for obvious out-of-scope non-financial queries
        out_of_scope_triggers = [
            "write me a story", "write a story", "tell me a story",
            "write python code", "write code", "python script", "write a program",
            "who is the president", "who won", "joke", "tell a joke",
            "essay", "poem", "recipe", "sing a song"
        ]
        if any(trigger in msg_lower for trigger in out_of_scope_triggers):
            refusal_prefix = "I am Spendable AI, your personal financial liquidity assistant. " if is_first_turn else ""
            return ChatResponse(
                reply=f"{refusal_prefix}I can only assist with questions related to your spending, finances, money management, or scenario simulations. How can I help you analyze your finances today?",
                agent_name="Spendable AI",
                context_used={"status": "out_of_scope_rejected"}
            )

        if not self.api_key or self.api_key.strip() == "":
            return self._generate_fallback(user_message, account_context, is_first_turn=is_first_turn)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)

            # Build conversation string
            formatted_history = []
            for h in chat_history[-6:]:
                role = "User" if h.role == "user" else "Spendable AI"
                formatted_history.append(f"{role}: {h.content}")

            history_str = "\n".join(formatted_history)

            prompt = f"""REAL ACCOUNT CONTEXT JSON:
{json.dumps(account_context, indent=2)}

RECENT CONVERSATION HISTORY:
{history_str if history_str else "None"}

IS_FIRST_REPLY_IN_CONVERSATION: {is_first_turn}

USER QUESTION:
{user_message}
"""

            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SPENDABLE_AI_SYSTEM_INSTRUCTION,
                    temperature=0.3,
                ),
            )

            reply_text = response.text or ""
            if not reply_text.strip():
                return self._generate_fallback(user_message, account_context, is_first_turn=is_first_turn)

            return ChatResponse(
                reply=reply_text.strip(),
                agent_name="Spendable AI",
                context_used=account_context,
            )
        except Exception as e:
            # Fallback if Gemini API call fails or hits capacity limits
            return self._generate_fallback(user_message, account_context, is_first_turn=is_first_turn, error_str=str(e))

    def _generate_fallback(
        self,
        user_message: str,
        account_context: Dict[str, Any],
        is_first_turn: bool = True,
        error_str: Optional[str] = None,
    ) -> ChatResponse:
        """Deterministic intelligent fallback when Gemini API key is missing or fails."""
        bal = account_context.get("current_balance", 0.0)
        spendable = account_context.get("spendable_amount", 0.0)
        protected = account_context.get("protected_amount", 0.0)
        state = account_context.get("liquidity_state", "HEALTHY")
        min_bal = account_context.get("forecasted_minimum_balance", 0.0)
        commitments = account_context.get("upcoming_commitments", 0.0)
        reserve = account_context.get("safety_reserve", 0.0)
        scen = account_context.get("active_simulated_scenario")

        reply_parts = []
        if is_first_turn:
            reply_parts.append("Hello! I am **Spendable AI**, your personal financial liquidity assistant.\n")

        if scen:
            scen_type = scen.get("scenario_type", "SIMULATION")
            scen_spendable = scen.get("scenario_spendable_amount", spendable)
            delta = scen.get("spendable_delta", 0.0)
            scen_state = scen.get("scenario_liquidity_state", state)
            reply_parts.append(f"**Simulated Scenario Active**: {scen_type}")
            reply_parts.append(f"- Simulated Safe Spendable Runway: **৳{scen_spendable:,.2f}** (Delta: ৳{delta:,.2f})")
            reply_parts.append(f"- Simulated Liquidity Status: **{scen_state}**\n")

        reply_parts.append(f"**Current Financial Health Overview**:")
        reply_parts.append(f"- Total Account Balance: **৳{bal:,.2f}**")
        reply_parts.append(f"- Safe Spendable Runway: **৳{spendable:,.2f}**")
        reply_parts.append(f"- Protected Obligations & Reserve: **৳{protected:,.2f}** (Commitments: ৳{commitments:,.2f}, Safety Buffer: ৳{reserve:,.2f})")
        reply_parts.append(f"- 30-Day Forecasted Minimum: **৳{min_bal:,.2f}**")
        reply_parts.append(f"- Overall Liquidity Status: **{state}**\n")

        reply_parts.append("Based on your observed transaction patterns and ML cash-flow risk assessment, your liquidity cushion remains monitored. You can ask me specific questions about safe purchase amounts, monthly bills, or scenario impacts!")

        return ChatResponse(
            reply="\n".join(reply_parts),
            agent_name="Spendable AI",
            context_used=account_context,
        )

