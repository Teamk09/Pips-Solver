from nicegui import ui
from typing import Dict, Any
import random
import numpy as np
from solver import solve_puzzle

app_state: Dict[str, Any] = {
    'board_size': 4,
    'domino_input': '6-0, 2-2',
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

def get_random_color() -> str:
    #random hex color for painting in square
    return f'#{random.randint(0, 0xFFFFFF):06x}'

def add_region():
    name = app_state['new_region_name'].strip()
    if name and name not in app_state['regions']:
        app_state['regions'][name] = {
            'rule': '',
            'value': 0,
            'cells': [],
            'color': get_random_color(),
        }
        app_state['new_region_name'] = ''
        region_palette.refresh()
        rule_definitions.refresh()
    elif not name:
        ui.notify("Region name cannot be empty.", type='warning')
    else:
        ui.notify(f"Region '{name}' already exists.", type='warning')

def set_active_region(region_id: str):
    app_state['active_region_id'] = region_id
    region_palette.refresh() # Refresh to show which region is active

def assign_cell_to_region(r: int, c: int):
    active_id = app_state['active_region_id']
    if not active_id:
        ui.notify("Please select a region from the palette first.", type='warning')
        return

    old_region_id = app_state['cell_to_region'].get((r, c))
    if old_region_id and old_region_id in app_state['regions']:
        if (r, c) in app_state['regions'][old_region_id]['cells']:
            app_state['regions'][old_region_id]['cells'].remove((r, c))

    app_state['cell_to_region'][(r, c)] = active_id
    if (r, c) not in app_state['regions'][active_id]['cells']:
        app_state['regions'][active_id]['cells'].append((r, c))

    grid_container.refresh()
    region_palette.refresh()

def get_cell_style(r: int, c: int) -> str:
    """Determines the background color and style of a cell based on its assigned region."""
    region_id = app_state['cell_to_region'].get((r, c))
    if region_id and region_id in app_state['regions']:
        color = app_state['regions'][region_id]['color']
        # Add a border if the region is active to show what you're painting with
        border = 'border-4 border-blue-500' if app_state['active_region_id'] == region_id else 'border-2'
        return f'background-color: {color};'
    return ''

@ui.refreshable
def grid_container():
    board_size = int(app_state['board_size'])
    with ui.grid(columns=board_size):
        for r in range(board_size):
            for c in range(board_size):
                card = ui.card()
                card.on('click', lambda _, r=r, c=c: assign_cell_to_region(r, c))

                region_id = app_state['cell_to_region'].get((r, c))
                if region_id and region_id in app_state['regions']:
                    color = app_state['regions'][region_id]['color']
                    card.style(f'background-color: {color}')
                    

                with card:
                    solution_val = app_state['solution'].get((r, c))
                    if solution_val is not None:
                        ui.label(str(solution_val))
                    else:
                        ui.label(f'({r},{c})')

@ui.refreshable
def region_palette():
    with ui.row().classes('w-full items-center gap-2'):
        for region_id, data in app_state['regions'].items():
            is_active = (region_id == app_state['active_region_id'])
            button_style = 'background-color: ' + data.get('color', '#ffffff')
            button_classes = 'text-white font-bold ring-4 ring-blue-500' if is_active else 'text-black'
            ui.button(
                region_id,
                on_click=lambda _, r_id=region_id: set_active_region(r_id)
            ).style(button_style).classes(button_classes)

@ui.refreshable
def rule_definitions():
    if not app_state['regions']:
        ui.label("Add a region to define its rules.").classes('text-gray-500')
        return

    for region_id, data in app_state['regions'].items():
        with ui.row().classes('w-full items-center gap-4 p-2 border-b'):
            ui.label(f"Region '{region_id}':").classes('w-32 font-bold')
            
            visibility_state = {'visible': RULES.get(data['rule'], {}).get('value_required', False)}
            
            def on_rule_change(e, state=visibility_state):
                 state['visible'] = RULES.get(e.value, {}).get('value_required', False)

            # A single select element for the rule, with the on_change handler.
            ui.select(options=RULE_OPTIONS, label='Rule', value=data['rule'], on_change=on_rule_change) \
                .bind_value(data, 'rule').classes('w-48')

            ui.number(label='Value').bind_value(data, 'value') \
                .bind_visibility_from(visibility_state, 'visible')

@ui.refreshable
def grid_container():
    """The main grid display. Refreshes on cell assignment."""
    board_size = int(app_state['board_size']) # Ensure board_size is an integer
    with ui.grid(columns=board_size).classes('gap-2 p-6 mx-auto'):
        for r in range(board_size):
            for c in range(board_size):
                style = get_cell_style(r, c)
                card = ui.card().classes('w-20 h-20 flex justify-center items-center cursor-pointer transition-all duration-200').style(style)
                card.on('click', lambda _, r=r, c=c: assign_cell_to_region(r, c))
                with card:
                    # Display the solved number when available
                    solution_val = app_state['solution'].get((r, c))
                    if solution_val is not None:
                        ui.label(str(solution_val)).classes('text-3xl font-bold')
                    else:
                        ui.label(f'({r},{c})').classes('text-xs text-gray-400')

def reset_board_state():
    """Clears all region and cell data to allow for a new board size."""
    app_state['regions'].clear()
    app_state['cell_to_region'].clear()
    app_state['active_region_id'] = None
    app_state['solution'].clear()
    region_palette.refresh()
    rule_definitions.refresh()
    grid_container.refresh()

def handle_board_size_change():
    reset_board_state()
    grid_container.refresh()

def handle_solve_click():
    solution_output.clear()
    app_state['solution'] = {}
    grid_container.refresh()

    try:
        domino_str = app_state['domino_input'].replace(' ', '')
        if not domino_str:
            ui.notify('Domino input cannot be empty.', type='negative')
            return
        domino_pairs = domino_str.split(',')
        dominoes = [tuple(sorted(map(int, pair.split('-')))) for pair in domino_pairs]
    except Exception:
        ui.notify('Invalid domino format. Please use "1-2, 3-4".', type='negative')
        return

    board_size = int(app_state['board_size'])
    if not app_state['cell_to_region']:
        ui.notify('The board is empty. Please assign cells to regions.', type='negative')
        return
    active_cells = list(app_state['cell_to_region'].keys())

    ui.notify('Solving', type='info')

    solution_board = solve_puzzle(board_size, dominoes, app_state['regions'], active_cells)

    if solution_board is not None:
        ui.notify('Solution found!', type='positive')
        for r in range(board_size):
            for c in range(board_size):
                if solution_board[r, c] != -2:
                    app_state['solution'][(r, c)] = solution_board[r, c]
        grid_container.refresh()
    else:
        ui.notify('No solution', type='negative')

    with solution_output:
        if solution_board is not None:
            ui.label('Solved Board:').classes('text-lg font-bold')
            for row in solution_board:
                # replaces -2 with x to be easier to visually understand
                display_row = [str(val) if val != -2 else 'x' for val in row]
                ui.label(f"[{', '.join(display_row)}]").classes('font-mono')


# --- Main UI Layout ---
with ui.row().classes('w-full justify-center'):
    with ui.card().classes('w-full max-w-5xl m-4 p-6'):
        ui.label('NYT Pips Solver').classes('text-3xl font-bold text-center mb-6')

        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('Step 1: Board Setup').classes('text-xl font-semibold mb-2')
            with ui.row().classes('w-full items-center justify-center gap-4'):
                ui.number(
                    'Board Size (N x N)', min=2, max=10, step=1,
                    on_change=handle_board_size_change
                ).bind_value(app_state, 'board_size')
                ui.input('Dominoes (e.g., 1-2, 3-4)').bind_value(app_state, 'domino_input').classes('grow')

        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('Step 2: Define & Assign Regions').classes('text-xl font-semibold mb-2')
            with ui.row().classes('w-full items-center gap-2 mb-4'):
                ui.input('New Region Name').bind_value(app_state, 'new_region_name')
                ui.button('Add Region', on_click=add_region)
            ui.label('Region Palette (Click to select, then click grid to assign):').classes('text-sm text-gray-600 mb-2')
            region_palette()

        with ui.row().classes('w-full gap-4'):
            with ui.card().classes('w-auto p-2'): # Grid on the left
                grid_container()
            with ui.card().classes('w-1/2 p-4'): # Rules on the right
                ui.label('Step 3: Define Region Rules').classes('text-xl font-semibold mb-2')
                rule_definitions()

        # button to get output
        ui.separator().classes('my-6')
        ui.button('Process Puzzle Input', on_click=handle_solve_click).props('color=primary size=lg').classes('w-full')
        solution_output = ui.column().classes('mt-4 p-4 bg-gray-100 rounded w-full')

# Initial creation of the grid
handle_board_size_change()

ui.run()
