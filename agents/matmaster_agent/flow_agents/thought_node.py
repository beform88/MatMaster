from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from typing import Any, List, Literal, Optional


ThoughtStatus = Literal['active', 'pruned', 'terminal']


@dataclass
class ThoughtNode:
    """Represents a single node in a Tree-of-Thought style search.

    Attributes:
        state_snapshot: Deep copy of the conversation state at this node.
        actions: Sequence of steps selected so far.
        score: Heuristic score assigned during evaluation.
        depth: Current depth in the search tree (root starts at 0).
        parent_id: Identifier of the parent node, if any.
        status: Search status flag (active/pruned/terminal).
    """

    state_snapshot: dict[str, Any]
    actions: List[dict[str, Any]] = field(default_factory=list)
    score: float = 0.0
    depth: int = 0
    parent_id: Optional[str] = None
    status: ThoughtStatus = 'active'
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def clone_with_updates(
        self,
        *,
        state_snapshot: Optional[dict[str, Any]] = None,
        actions: Optional[List[dict[str, Any]]] = None,
        depth: Optional[int] = None,
        parent_id: Optional[str] = None,
        status: Optional[ThoughtStatus] = None,
    ) -> 'ThoughtNode':
        """Create a new node derived from the current one."""

        return ThoughtNode(
            state_snapshot=copy.deepcopy(state_snapshot or self.state_snapshot),
            actions=copy.deepcopy(actions or self.actions),
            score=self.score,
            depth=depth if depth is not None else self.depth,
            parent_id=parent_id if parent_id is not None else self.parent_id,
            status=status if status is not None else self.status,
        )


__all__ = ['ThoughtNode', 'ThoughtStatus']
