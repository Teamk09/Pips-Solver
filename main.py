import numpy as np
from nicegui import ui
from typing import Dict, Any
import random
import asyncio
from solver import solve_puzzle

#keeps track of game state, constantly updated by refresh functions
app_state: Dict[str, Any] = {
    'board_size': 5,
    'domino_input': '',
    'regions': {},
    'cell_to_region': {},
    'active_region_id': None,
    'new_region_name': '',
    'solution': {},
}

RULES = {
    '': {'label': 'Blank (No Rule)', 'value_required': False},
    '=': {'label': 'Equals (=)', 'value_required': False},
    '≠': {'label': 'Not Equals (≠)', 'value_required': False},
    '>': {'label': 'Greater Than (>)', 'value_required': True},
    '<': {'label': 'Less Than (<)', 'value_required': True},
    '∑': {'label': 'Sum of Pips (∑)', 'value_required': True},
}
RULE_OPTIONS = {key: value['label'] for key, value in RULES.items()}

#default hard puzzle because entering the same puzzle over and over again is annoying
def load_official_hard_puzzle():
    """Wipes the current state and loads the user's specific puzzle with the correct, verified data."""
    reset_board_state()
    app_state['board_size'] = 5
    app_state['domino_input'] = '1-4, 3-4, 5-3, 0-1, 5-1, 0-3, 0-5, 2-5, 4-0, 2-4'
    
    puzzle_data = {
        '(24)': {'rule': '∑', 'value': 24, 'cells': [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]},
        '(>1)':   {'rule': '>', 'value': 1,  'cells': [(0, 1)]},
        '(0 first)':    {'rule': '∑', 'value': 0,  'cells': [(0, 2)]},
        '(4)':  {'rule': '∑', 'value': 4,  'cells': [(2, 0), (3, 0), (4, 0)]},
        '(= first)':    {'rule': '=', 'value': 0,  'cells': [(2, 1), (2, 2)]},
        '(= second)':   {'rule': '=', 'value': 0,  'cells': [(3, 1), (3, 2), (3, 3)]},
        '(0 second)':  {'rule': '∑', 'value': 0,  'cells': [(4, 1), (4, 2)]},
        'Blank':       {'rule': '', 'value': 0,  'cells': [(0, 3), (2, 3), (4, 3)]},
    }

    for region_id, data in puzzle_data.items():
        app_state['regions'][region_id] = {
            'rule': data['rule'],
            'value': data['value'],
            'cells': data['cells'],
            'color': get_random_color(),
        }
        for r, c in data['cells']:
            app_state['cell_to_region'][(r, c)] = region_id
    
    region_palette.refresh()
    rule_definitions.refresh()
    grid_container.refresh()
    board_size_input.value = app_state['board_size']
    domino_input_field.value = app_state['domino_input']

def get_random_color():
    return f'#{random.randint(0, 0xFFFFFF):06x}'

def add_region():
    name = app_state['new_region_name'].strip()
    if name and name not in app_state['regions']:
        app_state['regions'][name] = { 'rule': '', 'value': 0, 'cells': [], 'color': get_random_color() }
        app_state['new_region_name'] = ''
        region_palette.refresh()
        rule_definitions.refresh()
    else:
        ui.notify("Region name is empty or already exists.", type='warning')

def set_active_region(region_id: str):
    app_state['active_region_id'] = region_id
    region_palette.refresh()

def assign_cell_to_region(r: int, c: int):
    active_id = app_state['active_region_id']
    if not active_id:
        ui.notify("Please select a region from the palette first.", type='warning')
        return

    old_region_id = app_state['cell_to_region'].get((r, c))
    if old_region_id and (r, c) in app_state['regions'][old_region_id]['cells']:
        app_state['regions'][old_region_id]['cells'].remove((r, c))

    app_state['cell_to_region'][(r, c)] = active_id
    if (r, c) not in app_state['regions'][active_id]['cells']:
        app_state['regions'][active_id]['cells'].append((r, c))
    grid_container.refresh()

def get_cell_style(r: int, c: int) -> str:
    region_id = app_state['cell_to_region'].get((r, c))
    if region_id:
        return f'background-color: {app_state["regions"][region_id]["color"]};'
    return ''

def reset_board_state():
    app_state.update({ 'regions': {}, 'cell_to_region': {}, 'active_region_id': None, 'solution': {} })
    if 'board_size_input' in globals(): board_size_input.value = app_state['board_size']
    if 'domino_input_field' in globals(): domino_input_field.value = ''
    region_palette.refresh(); rule_definitions.refresh(); grid_container.refresh()

def handle_board_size_change():
    reset_board_state()

async def handle_solve_click():
    app_state['solution'] = {}
    grid_container.refresh()
    solution_output.clear()

    try:
        domino_str = app_state['domino_input'].replace(' ', '')
        if not domino_str:
            ui.notify('Domino input cannot be empty.', type='negative'); return
        domino_pairs = domino_str.split(',')
        dominoes = [tuple(sorted(map(int, pair.split('-')))) for pair in domino_pairs]
    except Exception:
        ui.notify('Invalid domino format.', type='negative'); return

    board_size = int(app_state['board_size'])
    active_cells = list(app_state['cell_to_region'].keys())
    if not active_cells:
        ui.notify('The board is empty.', type='negative'); return

    ui.notify('Solver started... check the console for progress.', type='info')

    loop = asyncio.get_running_loop()
    solution_board = await loop.run_in_executor(
        None, solve_puzzle, board_size, dominoes, app_state['regions'], active_cells
    )

    if solution_board is not None:
        ui.notify('Solution found!', type='positive')
        app_state['solution'] = {(r, c): solution_board[r, c] for r, c in active_cells}
        grid_container.refresh()
    else:
        ui.notify('No solution was found for this configuration.', type='negative')

    with solution_output:
        if solution_board is not None:
            ui.label('Solved Board:').classes('text-lg font-bold')
            for row in solution_board:
                display_row = [str(val) if val != -2 else 'x' for val in row]
                ui.label(f"[{', '.join(display_row)}]").classes('font-mono')

@ui.refreshable
def grid_container():
    board_size = int(app_state['board_size'])
    with ui.grid(columns=board_size).classes('gap-1 p-4 mx-auto'):
        for r in range(board_size):
            for c in range(board_size):
                style = get_cell_style(r, c)
                card = ui.card().classes('w-20 h-20 flex justify-center items-center cursor-pointer').style(style)
                card.on('click', lambda _, r=r, c=c: assign_cell_to_region(r, c))
                with card:
                    val = app_state['solution'].get((r, c))
                    if val is not None:
                        ui.label(str(val)).classes('text-3xl font-bold')
                    elif (r, c) in app_state['cell_to_region']:
                         ui.label(f'').classes('text-xs text-gray-400')
                    else:
                        ui.label(f'({r},{c})').classes('text-xs text-gray-400')
@ui.refreshable
def region_palette():
    with ui.row().classes('w-full items-center gap-2'):
        for region_id, data in app_state['regions'].items():
            is_active = (region_id == app_state['active_region_id'])
            button_style = 'background-color: ' + data.get('color', '#ffffff')
            button_classes = 'text-white font-bold ring-4 ring-blue-500' if is_active else 'text-black'
            ui.button(region_id, on_click=lambda _, r_id=region_id: set_active_region(r_id)).style(button_style).classes(button_classes)

@ui.refreshable
def rule_definitions():
    if not app_state['regions']:
        ui.label("Add a region to define its rules.").classes('text-gray-500'); return
    for region_id, data in app_state['regions'].items():
        with ui.row().classes('w-full items-center gap-4 p-2 border-b'):
            ui.label(f"Region '{region_id}':").classes('w-32 font-bold')
            visibility_state = {'visible': RULES.get(data['rule'], {}).get('value_required', False)}
            def on_rule_change(e, state=visibility_state):
                state['visible'] = RULES.get(e.value, {}).get('value_required', False)
            ui.select(options=RULE_OPTIONS, label='Rule', value=data['rule'], on_change=on_rule_change).bind_value(data, 'rule').classes('w-48')
            ui.number(label='Value').bind_value(data, 'value').bind_visibility_from(visibility_state, 'visible')

with ui.row().classes('w-full justify-center'):
    with ui.card().classes('w-full max-w-5xl m-4 p-6'):
        ui.label('NYT Pips Solver').classes('text-3xl font-bold text-center mb-6')
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('Step 1: Board Setup').classes('text-xl font-semibold mb-2')
            with ui.row().classes('w-full items-center justify-between gap-4'):
                board_size_input = ui.number('Board Size', min=2, max=10, step=1, on_change=handle_board_size_change).bind_value(app_state, 'board_size')
                domino_input_field = ui.input('Dominoes').bind_value(app_state, 'domino_input').classes('grow')
                ui.button('Load Official Hard Puzzle', on_click=load_official_hard_puzzle, icon='download').props('color=secondary')
        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('Step 2: Define & Assign Regions').classes('text-xl font-semibold mb-2')
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                ui.input('New Region Name').bind_value(app_state, 'new_region_name')
                ui.button('Add Region', on_click=add_region)
            ui.label('Region Palette:').classes('text-sm text-gray-600 mb-2')
            region_palette()
        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('w-auto p-2'):
                grid_container()
            with ui.card().classes('w-1/2 p-4'):
                ui.label('Step 3: Define Region Rules').classes('text-xl font-semibold mb-2')
                rule_definitions()
        ui.separator().classes('my-6')
        ui.button('Solve Puzzle', on_click=handle_solve_click).props('color=primary size=lg').classes('w-full')
        solution_output = ui.column().classes('mt-4 p-4 bg-gray-100 rounded w-full')

handle_board_size_change()
ui.run()