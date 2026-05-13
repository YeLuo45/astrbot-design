"""Query Expander using LLM for query reformulation and expansion."""

import json
from typing import List


class QueryExpander:
    """LLM-based query expander for generating query variations."""

    def __init__(self, llm):
        """
        Initialize query expander.

        Args:
            llm: LLM client with a .complete() method.
        """
        self.llm = llm

    async def expand(self, query: str, max_expansions: int = 3) -> List[str]:
        """
        Expand query with LLM-generated synonym reformulations.

        Args:
            query: The original query.
            max_expansions: Maximum number of reformulations to generate.

        Returns:
            List containing the original query plus expansions.
        """
        prompt = f"""为以下查询生成{max_expansions}个同义改写。返回JSON数组。

查询: {query}
输出: ["改写1", "改写2", "改写3"]"""
        try:
            response = await self.llm.complete(prompt)
            expansions = json.loads(response)
            if isinstance(expansions, list):
                return [query] + expansions[:max_expansions]
        except Exception:
            pass
        return [query]
