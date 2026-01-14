
import asyncio
import json
from typing import List, Dict, Any, Optional

from textual import on, work
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, ScrollableContainer
from textual.widgets import Input, Button, Static, Markdown, LoadingIndicator, Label
from textual.message import Message

from src.cli.llm.ollama import OllamaClient
from src.cli.llm.tools import get_tool_definitions
# Import tool functions to execute them
from src import clinvar, genomics, pathways, population

class ChatMessage(Static):
    """A single chat message bubble."""
    
    def __init__(self, role: str, content: str, tool_calls: Optional[List] = None):
        super().__init__()
        self.role = role
        self.content = content
        self.tool_calls = tool_calls
        
    def compose(self) -> ComposeResult:
        classes = "message-user" if self.role == "user" else "message-assistant"
        if self.role == "system": classes = "message-system"
        
        with Vertical(classes=f"message-container {classes}"):
            yield Label(self.role.capitalize(), classes="message-role")
            if self.content:
                yield Markdown(self.content)
            
            if self.tool_calls:
                for tc in self.tool_calls:
                    yield Static(f"🔧 Calling tool: `{tc.name}`", classes="tool-call-info")

class ChatWidget(Vertical):
    """
    Main Chat Interface Component.
    """
    
    DEFAULT_CSS = """
    ChatWidget {
        height: 1fr;
        background: #1e1e2e;
    }
    
    #chat_history {
        height: 1fr;
        overflow-y: scroll;
        padding: 1;
        background: #1e1e2e;
    }
    
    #input_container {
        height: auto;
        dock: bottom;
        background: #181825;
        padding: 1;
    }
    
    .message-container {
        padding: 1;
        margin-bottom: 1;
        background: #313244;
        border-radius: 1;
        width: 100%;
        height: auto;
    }
    
    .message-user {
        background: #45475a;
        margin-left: 20%;
    }
    
    .message-assistant {
        background: #313244;
        margin-right: 20%;
        border-left: tall #89b4fa;
    }
    
    .message-role {
        color: #a6adc8;
        text-style: bold;
        margin-bottom: 1;
    }
    
    .tool-call-info {
        color: #f9e2af;
        text-style: italic;
        background: #1e1e2e;
        padding: 0 1;
        margin-top: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.llm = OllamaClient(model="qwen2.5:7b") # Configurable?
        self.messages: List[Dict] = []
        self.system_prompt = "You are a helpful genomics research assistant."

    def compose(self) -> ComposeResult:
        with ScrollableContainer(id="chat_history"):
            yield Markdown("### 🤖 GenomeMCP Assistant\n\nAsk me about variants, genes, or phenotypes!")
        
        with Horizontal(id="input_container"):
            yield Input(placeholder="Ask a question...", id="chat_input")
            yield Button("Send", variant="primary", id="send_btn")

    @on(Input.Submitted, "#chat_input")
    def on_input_submit(self, event: Input.Submitted):
        self._handle_user_input(event.value)

    @on(Button.Pressed, "#send_btn")
    def on_btn_press(self):
        inp = self.query_one("#chat_input", Input)
        self._handle_user_input(inp.value)

    def _handle_user_input(self, text: str):
        if not text.strip(): return
        
        # Clear input
        self.query_one("#chat_input", Input).value = ""
        
        # Add User Message
        self._add_message("user", text)
        
        # Trigger LLM
        self.run_worker(self._process_llm_response())

    def _add_message(self, role: str, content: str, tool_calls: field = None):
        self.messages.append({"role": role, "content": content})
        
        history = self.query_one("#chat_history")
        history.mount(ChatMessage(role, content, tool_calls))
        history.scroll_end(animate=True)

    async def _process_llm_response(self):
        try:
            # 1. Prepare messages
            context = [{"role": "system", "content": self.system_prompt}] + self.messages[-10:] # Keep context window manageable
            
            # 2. Call LLM
            response = await self.llm.chat(context, tools=get_tool_definitions())
            
            # 3. Add Assistant Message (initial)
            self._add_message("assistant", response.content, response.tool_calls)
            
            # 4. Handle Tool Calls
            if response.tool_calls:
                await self._handle_tool_calls(response.tool_calls)
                
        except Exception as e:
            self.notify(f"LLM Error: {e}", severity="error")
            self._add_message("system", f"Error: {e}")

    async def _handle_tool_calls(self, tool_calls):
        messages_with_tools = self.messages[:] # Copy current history
        
        # Iterate and execute tools
        for tc in tool_calls:
            tool_name = tc.name
            args = tc.arguments
            
            result = await self._execute_tool(tool_name, args)
            
            # Add Tool Output Message
            tool_msg = {
                "role": "tool",
                "content": json.dumps(result, default=str),
                "name": tool_name,
                "tool_call_id": tc.id 
                # Note: Ollama format might differ slightly from OpenAI on IDs, 
                # strictly OpenAI needs tool_call_id to match.
            }
            # For this simple implementation, we might simulate the conversation continuing
            # by feeding the result back to the LLM.
            
            # Render Tool Output to Chat immediately for visibility
            self._add_message("system", f"**Tool Result ({tool_name})**:\n```json\n{json.dumps(result, indent=2)[:500]}...\n```")
            
            # In a real rigorous loop, we'd append to context and call chat() again.
            # Implementing a single-turn follow-up for now.
            context = [{"role": "system", "content": self.system_prompt}] + self.messages[-5:]
            context.append({"role": "assistant", "content": "", "tool_calls": [
                {"type": "function", "function": {"name": tc.name, "arguments": json.dumps(args)}}
            ]})
            context.append(tool_msg)
            
            # Follow-up response
            follow_up = await self.llm.chat(context)
            if follow_up.content:
                 self._add_message("assistant", follow_up.content)

    async def _execute_tool(self, name: str, args: dict) -> Any:
        """Map tool names to actual functions."""
        try:
            if name == "search_clinvar":
                return await clinvar.search_clinvar(args.get("term"))
            elif name == "get_variant_report":
                return await clinvar.get_variant_report(args.get("variant_id"))
            elif name == "get_gene_info":
                return await clinvar.get_gene_info(args.get("gene_symbol"))
            elif name == "get_population_stats":
                return await population.get_population_stats(args.get("variant_str"))
            elif name == "get_pathway_info":
                return await pathways.get_pathway_info(args.get("gene_symbol"))
            elif name == "find_related_genes":
                return await pathways.find_related_genes(args.get("phenotype_or_disease"))
            # Add other tools as needed
            return {"error": f"Tool {name} not implemented"}
        except Exception as e:
            return {"error": str(e)}

