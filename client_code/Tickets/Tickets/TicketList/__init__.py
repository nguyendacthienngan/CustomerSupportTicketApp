from ._anvil_designer import TicketListTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server


class TicketList(TicketListTemplate):
  """This Form is responsible for fetching tickets from the server and displaying them.
    
  It also handles ticket pagination, selecting tickets and deleting tickets.
  """
  
  def __init__(self, **properties):
    self.selected_tickets = []
    self.filtered_tickets = []
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    # Any code you write here will run when the form opens.
    # Set event handlers on repeating_panel_1 that will be raised from the 'TicketRow' Form
    self.repeating_panel_1.set_event_handler('x-select-ticket', self.select_ticket)
    self.repeating_panel_1.set_event_handler('x-deselect-ticket', self.deselect_ticket)
    self.repeating_panel_1.set_event_handler('x-update-ticket-priority', self.update_ticket_priority)

  def load_tickets(self, filters, sort='date', date_filter={}):
    """Load a list of tickets from the 'Tickets' Data Table.
    
    Arguments:
      filters: dict of filters
      sort - string (optional): how should tickets be sorted
      date_filter: dict of date filters
    """
    # Initialise self.filters if 'filters' have been passed in
    if filters is not None:
      self.filters = filters
    if date_filter is not None:
      self.date_filter = date_filter
    # Fetch tickets from the server
    self.filtered_tickets = anvil.server.call('get_tickets', sort, self.filters, self.date_filter)
    # Refresh data bindings to update the 'items' property of repeating_panel_1 that displays a list of tickets
    self.refresh_data_bindings()
    self.set_pages()
  
  # Update the ticket priority if the priority_dropdown on the TicketRow Form is changed
  def update_ticket_priority(self, ticket, ticket_dict, **event_args):
    anvil.server.call('update_ticket_priority', ticket, ticket_dict['priority'])
    Notification("Ticket priority updated").show()

  # Change the order of tickets being displayed
  def sort_dropdown_change(self, **event_args):
    if self.sort_dropdown.selected_value == 'Agent':
      sort = 'owner'
    else:
      sort = self.sort_dropdown.selected_value.lower()
    self.load_tickets(filters=None, sort=sort)

  # PAGINATION CONTROLS
  def previous_page_link_click(self, **event_args):
    self.data_grid_1.previous_page()
    self.set_pages()

  def next_page_link_click(self, **event_args):
    self.data_grid_1.next_page()
    self.set_pages()
    
  def first_page_link_click(self, **event_args):
    self.data_grid_1.jump_to_first_page()
    self.set_pages()

  def last_page_link_click(self, **event_args):
    self.data_grid_1.jump_to_last_page()
    self.set_pages()
  
  # Calculating "Tickets X-Y of Z"  
  def set_pages(self):
    page = self.data_grid_1.get_page()
    no_rows = self.data_grid_1.rows_per_page
    start_page = ((page + 1) * no_rows)
    end_page = min(start_page, len(self.filtered_tickets))
    text = f"{(page * no_rows) + 1}-{end_page} of {len(self.filtered_tickets)}"
    self.pagination_label.text = text

  # Selecting and deselecting tickets
  def select_ticket(self, ticket, **event_args):
    self.selected_tickets.append(ticket)
    self.update_selected_tickets()
    
  def deselect_ticket(self, ticket, **event_args):
    self.selected_tickets.remove(ticket)
    self.update_selected_tickets()
  
  def select_all_box_change(self, **event_args):
    self.selected_tickets = []
    if self.select_all_box.checked:
      self.selected_tickets += self.filtered_tickets
      for t in self.repeating_panel_1.get_components():
        t.role = "tickets-repeating-panel-selected"
        t.check_box_1.checked = True
    else:
      for t in self.repeating_panel_1.get_components():
        t.role = "tickets-repeating-panel"
        t.check_box_1.checked = False
    self.update_selected_tickets()

  def clear_selected_link_click(self, **event_args):
    self.select_all_box.checked = False
    self.select_all_box_change()
    self.update_selected_tickets()
  
  # Update the number of selected tickets
  def update_selected_tickets(self):
    if len(self.selected_tickets) == 0:
      self.selected_label.text = ""
      self.selected_label.visible = False
      self.clear_selected_link.visible = False
    else:
      self.selected_label.text = f"{len(self.selected_tickets)} tickets selected"
      self.selected_label.visible = True
      self.clear_selected_link.visible = True

  # Closing tickets
  def close_tickets_link_click(self, **event_args):
    if self.selected_tickets:
      if confirm("Are you sure you want to close the following tickets?: \n{}" .format(' \n'.join(t['title'] for t in self.selected_tickets)),
                 large=True):
        anvil.server.call('close_tickets', self.selected_tickets)
        self.selected_tickets = []
        self.update_selected_tickets()
        self.load_tickets(self.filters, date_filter=self.date_filter)
    else:
      alert("No tickets selected")











