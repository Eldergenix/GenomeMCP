"""
ReAct-style agent for GenomeMCP.

Orchestrates LLM and tool execution for genomics analysis.
"""

import asyncio
import json
from typing import Callable, Any

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from .llm.client import LLMClient, LLMResponse
from .llm.tools import GENOMICS_TOOLS, GENOMICS_SYSTEM_PROMPT

console = Console()


class GenomicsAgent:
    """
    ReAct-style agent that uses LLM with GenomeMCP tools.
    
    Flow:
    1. User query → LLM with tools
    2. If tool call → Execute tool → Return to LLM
    3. Repeat until final answer
    """
    
    MAX_ITERATIONS = 10
    
    def __init__(
        self,
        llm_client: LLMClient,
        tools: list[dict] | None = None,
        verbose: bool = False,
    ):
        self.llm = llm_client
        self.tools = tools or GENOMICS_TOOLS
        self.verbose = verbose
        self._tool_functions = self._load_tool_functions()
    
    def _load_tool_functions(self) -> dict[str, Callable]:
        """Load the actual tool functions from GenomeMCP modules."""
        from src import clinvar, genomics, population, pathways
        
        return {
            "search_clinvar": clinvar.search_clinvar,
            "get_variant_report": clinvar.get_variant_report,
            "get_gene_info": clinvar.get_gene_info,
            "get_supporting_literature": clinvar.get_supporting_literature,
            "find_related_genes": clinvar.find_related_genes,
            "get_discovery_evidence": clinvar.get_discovery_evidence,
            "get_genomic_context": genomics.get_genomic_context,
            "get_population_stats": population.get_population_stats,
            "get_pathway_info": pathways.get_pathway_info,
            "visualize_pathway": pathways.visualize_pathway,
        }
    
    async def run(self, query: str) -> str:
        """
        Run the agent with a user query.
        
        Args:
            query: User's genomics question.
            
        Returns:
            Final response from the LLM.
        """
        messages = [
            {"role": "system", "content": GENOMICS_SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]
        
        for iteration in range(self.MAX_ITERATIONS):
            if self.verbose:
                console.print(f"[dim]Iteration {iteration + 1}...[/dim]")
            
            # Call LLM
            response = await self.llm.chat(messages, self.tools)
            
            # Check for tool calls
            if response.has_tool_calls:
                # Execute tools and add results
                tool_results = await self._execute_tools(response.tool_calls)
                
                # Add assistant message with tool calls
                messages.append({
                    "role": "assistant",
                    "content": response.content or "",
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": json.dumps(tc.arguments),
                            }
                        }
                        for tc in response.tool_calls
                    ]
                })
                
                # Add tool results
                for tc, result in zip(response.tool_calls, tool_results):
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(result) if not isinstance(result, str) else result,
                    })
            else:
                # No tool calls - final answer
                return response.content
        
        return "I apologize, but I couldn't complete the analysis within the iteration limit."
    
    async def _execute_tools(self, tool_calls) -> list[Any]:
        """Execute a list of tool calls and return results."""
        results = []
        
        for tc in tool_calls:
            if self.verbose:
                console.print(f"[cyan]🔧 Calling {tc.name}({tc.arguments})[/cyan]")
            
            try:
                result = await self._execute_single_tool(tc.name, tc.arguments)
                results.append(result)
                
                if self.verbose:
                    preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
                    console.print(f"[green]✓ Result: {preview}[/green]")
                    
            except Exception as e:
                error_msg = f"Error executing {tc.name}: {str(e)}"
                results.append({"error": error_msg})
                
                if self.verbose:
                    console.print(f"[red]✗ {error_msg}[/red]")
        
        return results
    
    async def _execute_single_tool(self, name: str, arguments: dict) -> Any:
        """Execute a single tool by name."""
        if name not in self._tool_functions:
            return {"error": f"Unknown tool: {name}"}
        
        func = self._tool_functions[name]
        
        # Call the async function with arguments
        result = await func(**arguments)
        return result


class ChatSession:
    """
    Interactive chat session with the genomics agent.
    """
    
    def __init__(self, agent: GenomicsAgent):
        self.agent = agent
        self.history: list[tuple[str, str]] = []
    
    async def chat(self, user_input: str) -> str:
        """Process user input and return response."""
        response = await self.agent.run(user_input)
        self.history.append((user_input, response))
        return response
    
    def clear_history(self):
        """Clear chat history."""
        self.history = []
