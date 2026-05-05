from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class ModuleSpec:
    key: str
    label: str
    description: str
    primary_metric_label: str
    default_unit: str
    amount_label: str
    default_status: str
    category: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


MODULES = [
    ModuleSpec('task', 'Tasks', 'Track personal actions and routines.', 'Progress score', 'points', 'Budget impact', 'planned', 'execution'),
    ModuleSpec('note', 'Notes', 'Capture ideas, reflections, and plans.', 'Depth score', 'points', 'Reference value', 'active', 'knowledge'),
    ModuleSpec('contact', 'Contacts', 'Maintain key relationships and context.', 'Relationship score', 'points', 'Support budget', 'active', 'network'),
    ModuleSpec('expense', 'Expenses', 'Track spending and money habits.', 'Volume', 'items', 'Amount', 'logged', 'finance'),
    ModuleSpec('subscription', 'Subscriptions', 'Manage recurring memberships.', 'Cycle length', 'days', 'Recurring amount', 'active', 'finance'),
    ModuleSpec('workout', 'Workouts', 'Record training sessions and movement.', 'Duration', 'minutes', 'Energy spend', 'done', 'fitness'),
    ModuleSpec('meal', 'Meals', 'Log meals and nutrition observations.', 'Quality score', 'points', 'Meal cost', 'logged', 'nutrition'),
    ModuleSpec('reading', 'Reading', 'Measure learning and reading momentum.', 'Pages', 'pages', 'Book spend', 'done', 'knowledge'),
    ModuleSpec('health', 'Health', 'Track body signals and wellbeing indicators.', 'Health score', 'points', 'Care cost', 'logged', 'wellbeing'),
    ModuleSpec('life_event', 'Life Events', 'Capture milestones, travel, and memories.', 'Impact score', 'points', 'Experience cost', 'recorded', 'memory'),
]

MODULE_MAP = {module.key: module for module in MODULES}


def get_module(module_key: str) -> ModuleSpec:
    if module_key not in MODULE_MAP:
        raise KeyError(f'Unknown module: {module_key}')
    return MODULE_MAP[module_key]
