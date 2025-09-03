from nicegui import ui

def create_grid(n: int):
    if hasattr(create_grid, 'grid_container') and create_grid.grid_container:
        create_grid.grid_container.clear()
    else:
        create_grid.grid_container = ui.element('div').classes('w-full grid gap-2')
    
    create_grid.grid_container.style(f'grid-template-columns: repeat({n}, minmax(0, 1fr))')
    
    # Create n x n buttons
    for i in range(n):
        for j in range(n):
            button_id = i * n + j + 1
            ui.button(f'Button {button_id}', 
                     on_click=lambda btn_id=button_id: ui.notify(f'You clicked Button {btn_id}!')
                     ).classes('w-full h-full').move(create_grid.grid_container)

def on_input_change(event):
    try:
        n = int(event.value)
        if n > 0 and n <= 10:
            create_grid(n)
        else:
            ui.notify('Please enter a number between 1 and 10', type='warning')
    except ValueError:
        ui.notify('Please enter a valid number', type='negative')

ui.label('Enter a number to create an n by n grid of buttons:').classes('text-xl mt-4')
ui.number(value=3, min=1, max=10, step=1, on_change=on_input_change).classes('w-32')

create_grid(3)

ui.run()
