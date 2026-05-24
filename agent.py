"""LangGraph NL-to-SQL data agent PoC using Nebius through LangChain."""
from __future__ import annotations

import json
import os
import re
from typing import Any, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from config import DEFAULT_DOMAIN, DOMAINS
from dataset import DemoDataset
from sql_safety import validate_select_sql
from visualization import suggest_chart

load_dotenv()

DEFAULT_MODEL = os.getenv("MODEL_NAME", "gemini-3.1-flash-lite")

class DataAgentState(TypedDict, total=False):
    question: str
    history: list[tuple[str, str]]
    standalone_question: str
    domain: str
    sql: str
    validated_sql: str
    columns: list[str]
    rows: list[dict[str, Any]]
    answer: str
    chart: dict[str, str] | None
    error: str | None


class DataAgent:
    """A compact data-agent pipeline: route, write SQL, validate, execute, answer."""

    def __init__(self, dataset: DemoDataset | None = None, verbose: bool = False) -> None:
        self.dataset = dataset or DemoDataset()
        self.verbose = verbose
        self.llm = ChatGoogleGenerativeAI(
            model=DEFAULT_MODEL,
            google_api_key=os.environ["GOOGLE_API_KEY"],
            temperature=0,
        )
        self.graph = self._build_graph()

    def query(
        self,
        question: str,
        history: list[tuple[str, str]] | None = None,
    ) -> DataAgentState:
        return self.graph.invoke({"question": question, "history": history or []})

    def _build_graph(self):
        graph = StateGraph(DataAgentState)
        graph.add_node("rewrite", self._rewrite_question)
        graph.add_node("route", self._route_question)
        graph.add_node("write_sql", self._write_sql)
        graph.add_node("validate_sql", self._validate_sql)
        graph.add_node("execute_sql", self._execute_sql)
        graph.add_node("answer", self._answer)

        graph.set_entry_point("rewrite")
        graph.add_edge("rewrite", "route")
        graph.add_edge("route", "write_sql")
        graph.add_edge("write_sql", "validate_sql")
        graph.add_edge("validate_sql", "execute_sql")
        graph.add_edge("execute_sql", "answer")
        graph.add_edge("answer", END)
        return graph.compile()

    def _rewrite_question(self, state):
        question = state["question"]
        history = state.get("history", [])

        history_text = "\n".join(
            [f"Q: {h[0]}\nA: {h[1]}" for h in history[-4:]]
            )

        messages = [
            (
                "system",
                "Rewrite the user's latest question into a standalone question. "
                "Return only the rewritten question.",
            ),
            (
                "human",
                f"Conversation history:\n{history_text}\n\nLatest question:\n{question}",
            ),
        ]

        response = self.llm.invoke(messages)
        rewritten = response.content

        if isinstance(rewritten, list):
            rewritten = " ".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in rewritten
            )

        rewritten = str(rewritten).strip()

        return {"standalone_question": rewritten}

    def _route_question(self, state):
        question = state["standalone_question"]

        messages = [
            (
                "system",
                "You are a routing assistant.\n"
                "Choose the best domain for the question.\n"
                "Available domains:\n"
                "- sales\n"
                "- support\n\n"
                "Return ONLY one word: sales or support.",
            ),
            ("human", question),
        ]

        response = self.llm.invoke(messages)
        raw_domain = response.content

        if isinstance(raw_domain, list):
            raw_domain = " ".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in raw_domain
            )

        raw_domain = str(raw_domain).strip().lower()

        domain = "sales"
        if "support" in raw_domain:
            domain = "support"

        return {"domain": domain}

    def _write_sql(self, state):
        question = state["standalone_question"]
        domain = state["domain"]

        schema = self.dataset.schema_text(DOMAINS[domain].tables)
        messages = [
            (
                "system",
                f"""
    You are an expert SQLite analyst.

    Generate a SINGLE read-only SQL query.

    Rules:
    - Output ONLY SQL
    - No markdown
    - No explanations
    - No comments
    - Use only these tables:

    {schema}
    """,
            ),
            ("human", question),
        ]

        response = self.llm.invoke(messages)

        sql = response.content

        if isinstance(sql, list):
            sql = " ".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in sql
            )

        sql = str(sql).strip()

        return {"sql": _extract_sql(sql)}

    def _validate_sql(self, state: DataAgentState) -> dict[str, Any]:
        domain = DOMAINS[state["domain"]]
        result = validate_select_sql(state.get("sql", ""), set(domain.tables))
        if not result.ok:
            return {"error": result.error, "validated_sql": ""}
        return {"validated_sql": result.sql, "error": None}

    def _execute_sql(self, state: DataAgentState) -> dict[str, Any]:
        if state.get("error"):
            return {"rows": [], "columns": [], "chart": None}

        try:
            result = self.dataset.execute(state["validated_sql"])
        except Exception as exc:
            return {"error": f"Query failed: {exc}", "rows": [], "columns": [], "chart": None}

        chart = suggest_chart(result.rows)
        return {"rows": result.rows, "columns": result.columns, "chart": chart}

    def _answer(self, state):
        question = state["standalone_question"]
        sql = state["sql"]
        rows = state["rows"]

        messages = [
            (
                "system",
                "You are a business analytics assistant.\n"
                "Summarize query results clearly and concisely.",
            ),
            (
                "human",
                f"""
    Question:
    {question}

    SQL:
    {sql}

    Rows:
    {rows}
    """,
            ),
        ]

        response = self.llm.invoke(messages)

        answer = response.content

        if isinstance(answer, list):
            answer = " ".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in answer
            )

        answer = str(answer).strip()

        return {"answer": answer}


def _format_history(history: list[tuple[str, str]]) -> str:
    return "\n".join(f"{role}: {content}" for role, content in history)


def _pick_domain(text: str) -> str | None:
    for domain in DOMAINS:
        if re.search(rf"\b{re.escape(domain)}\b", text, re.IGNORECASE):
            return domain
    return None


def _keyword_domain(question: str) -> str | None:
    lowered = question.lower()
    support_words = {"ticket", "tickets", "support", "priority", "resolution", "refund", "damaged"}
    sales_words = {"revenue", "sales", "orders", "products", "inventory", "channel", "region"}
    if any(word in lowered for word in support_words):
        return "support"
    if any(word in lowered for word in sales_words):
        return "sales"
    return None


def _extract_sql(text: str) -> str:
    if not text:
        return ""

    if isinstance(text, list):
        text = " ".join(
            item.get("text", "") if isinstance(item, dict) else str(item)
            for item in text
        )

    cleaned = str(text).strip()

    if cleaned.startswith("```sql"):
        cleaned = cleaned.replace("```sql", "").replace("```", "").strip()

    elif cleaned.startswith("```"):
        cleaned = cleaned.replace("```", "").strip()

    return cleaned


def _fallback_answer(row_count: int, rows: list[dict[str, Any]]) -> str:
    if row_count == 0:
        return "The query ran successfully but returned no rows."
    return f"The query returned {row_count} rows. First row: {rows[0]}"

