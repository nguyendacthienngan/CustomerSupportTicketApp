from ._anvil_designer import ContentTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from .HeadlineStats import HeadlineStats


class Content(ContentTemplate):
  """This Form populates all the data and charts on the Dashboard.
  
  The data is displayed using the following Custom Components:
      1) HeadlineStats x3
      2) ProgressGraph x2 
      3) ResolutionGraph
    
    The charts are all custom JavaScript components that accept certain arguments.
    They take care of their own display.
    """
  
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    # This event is called from the HeadlineStats Form
    self.flow_panel_headline_stats.set_event_handler('x-open-tickets', self.open_tickets)
    
  def initialise_headline_cards(self, headline_stats, period):
    """Add three HeadlineStats components to the Dashboard.
    
    Arguments:
      headline_stats: dict of data for each of the HeadlineStats components in this form:
                      {
                      'unassigned': {'delta':delta, 'number':number},
                      'unresolved':{'delta':delta, 'number':number},
                      'urgent':{'delta':delta, 'number':number}
                      }
      period (string): number of days of data being displayed            
    """
    self.flow_panel_headline_stats.clear()
    # Add three HeadlineStats components to the Dashboard
    self.flow_panel_headline_stats.add_component(HeadlineStats(title="Unassigned", delta=headline_stats['unassigned']['delta'], value=headline_stats['unassigned']['number'], time_period=period))
    self.flow_panel_headline_stats.add_component(HeadlineStats(title="Unresolved", delta=headline_stats['unresolved']['delta'], value=headline_stats['unresolved']['number'], time_period=period))
    self.flow_panel_headline_stats.add_component(HeadlineStats(title="Urgent", delta=headline_stats['urgent']['delta'], value=headline_stats['urgent']['number'], time_period=period))

  # This is called initially in the form_show event of the Dashboard Form
  def initialise_progress_charts(self, progress_dash_stats):
    """Collect data and populate the two ProgressGraph charts, and the text for the accompanying labels.
    
    Arguments:
      progress_dash_stats: dict of data in this form:
                          {
                            'resolved': {
                              'total_resolved': len(resolved_tickets), 'closed_on_first':len(closed_on_first)
                            }, 
                            'customers':{
                              'new_customers':len(new_customers), 'returning_customers':len(returning_customers)
                            }
                          }  
    """
    # Get number of total resolved tickets and number of tickets closed on the first reply
    total_resolved = progress_dash_stats['resolved']['total_resolved']
    closed_on_first = progress_dash_stats['resolved']['closed_on_first']
    # Set display values to zero if no tickets resolved over the period
    if total_resolved == 0:
      self.closed_on_first_label.text = "No tickets resolved"
      self.closed_on_first_chart.percentage = 0
    # If tickets were resolved over the period, populate the data accordingly
    else:
      closed_on_first_percent = round(max((closed_on_first/total_resolved), 0),2)
      self.closed_on_first_label.text = f"{closed_on_first} ticket(s) were resolved with the first reply"
      self.closed_on_first_chart.percentage = closed_on_first_percent
    # Get number of new customers and number of returning customers
    new_customers = progress_dash_stats['customers']['new_customers']
    returning_customers = progress_dash_stats['customers']['returning_customers']
    # If no new customers, set the data accordingly
    if new_customers == 0:
      self.new_custs_label.text = f"No new customers \n{returning_customers} returning customers"
      self.new_custs_chart.percentage = 0
      self.new_custs_chart.display_value = 0
    else:
      # Set percentage of new customers
      self.new_custs_chart.percentage = round(max((new_customers / (new_customers + returning_customers)), 0),2)
      self.new_custs_chart.display_value = new_customers
      self.new_custs_label.text = f"{new_customers} new customer(s) \n{returning_customers} returning customers"
    # Make both charts visible
    # These are left hidden until this point so that the Dashboard loads simultaneously
    self.header_column_panel.visible = True
    self.content_column_panel.visible = True

  def initialise_resolution_chart(self, resolution_data):
    """Collect data and populate the ResolutionGraph custom component. 
    
    Arguments:
      resolution_data: dict of data in this form:
                      {'dates':dates, 'data':
                          {'resolved':resolved, 
                          'unresolved':unresolved}
                      }
    Dates is a list of dates in the form '%A, %d' 
    e.g. ['Friday, 07', 'Saturday, 08', 'Sunday, 09', 'Monday, 10', 'Tuesday, 11', 'Wednesday, 12', 'Thursday, 13']
    Resolved and unresolved are lists of numbers of tickets created on the days in the dates list 
    e.g [1,0,1,2,3,4,5]
    """
    labels = resolution_data['dates']
    data = resolution_data['data']
    self.resolution_graph.labels = labels
    self.resolution_graph.datasets = [{
            'label': 'Resolved',
            'backgroundColor': '#9389DF',
            'borderColor': '#7D71D8',
            'data': data['resolved']
        },{
            'label': 'Unresolved',
            'backgroundColor': '#00FFAF',
            'borderColor': '#00FFAF',
            'data': data['unresolved']
        }]
   
  def open_tickets(self, title, **event_args):
    # This event is raised from the 'HeadlineStats' Form
    # Raise an event on the parent 'Dashboard' Form
    self.parent.raise_event('x-open-tickets', title=title)
  
  
  