from nicegui import ui
from typing import Dict, Any
import random

app_state: Dict[str, Any] = {
    'board_size': 4,
    'domino_input': '6-0, 2-2',
    'regions': {},           
    'cell_to_region': {}, 
    'active_region_id': None,
    'new_region_name': '',
    'solution': {},
}

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
    elif not name:
        ui.notify("Region name cannot be empty.", type='warning')
    else:
        ui.notify(f"Region '{name}' already exists.", type='warning')

def set_active_region(region_id: str):
    app_state['active_region_id'] = region_id

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
    with ui.row():
        for region_id, data in app_state['regions'].items():
            is_active = (region_id == app_state['active_region_id'])
            button_style = 'background-color: ' + data.get('color', '#ffffff')
            button_classes = 'text-white font-bold ring-blue-500' if is_active else 'text-black'
            ui.button(
                region_id,
                on_click=lambda _, r_id=region_id: set_active_region(r_id)
            ).style(button_style).classes(button_classes)

with ui.row():
    with ui.card():
        ui.label('NYT Pips Solver').classes('text-3xl font-bold')

        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('Step 1: Board Setup').classes('text-xl font-semibold mb-2')
            with ui.row().classes('w-full'):
                ui.number(
                    'Board Size (N x N)', min=2, max=10, step=1
                ).bind_value(app_state, 'board_size')
                ui.input('Dominoes (e.g., 1-2, 3-4)').bind_value(app_state, 'domino_input').classes('grow')

        with ui.card().classes('w-full p-4 mb-4'):
            ui.label('Step 2: Define & Assign Regions').classes('text-xl font-semibold mb-2')
            with ui.row().classes('w-full'):
                ui.input('New Region Name').bind_value(app_state, 'new_region_name')
                ui.button('Add Region', on_click=add_region)
            region_palette()

        with ui.row().classes('w-full gap-4'):
            with ui.card():
                grid_container()



ui.run()
