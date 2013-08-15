
"""Custom topology example

author: Brandon Heller (brandonh@stanford.edu)

Two directly connected switches plus a host for each switch:

   host --- switch --- switch --- host

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo, Node

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self, enable_all = True ):
        "Create custom topo."

        # Add default members to class.
        super( MyTopo, self ).__init__()

        # Set Node IDs for hosts and switches
        middleupHost = 1
		leftdownHost = 2
        rightdownHost = 3
        leftupSwitch = 4
        rightupSwitch = 5
        middleupSwitch = 6
        middledownSwitch = 7
		
        # Add nodes
        self.add_node( leftupSwitch, Node( is_switch=True ) )
        self.add_node( rightupSwitch, Node( is_switch=True ) )
        self.add_node( middleupSwitch, Node( is_switch=True ) )
        self.add_node( middledownSwitch, Node( is_switch=True ) )
        self.add_node( middleupHost, Node( is_switch=False ) )
        self.add_node( leftdownHost, Node( is_switch=False ) )
        self.add_node( rightdownHost, Node( is_switch=False ) )

        # Add edges
        self.add_edge( middleupHost, leftupSwitch)
        self.add_edge( middleupHost, rightupSwitch )
        self.add_edge( leftupSwitch, middleupSwitch )
        self.add_edge( rightupSwitch, middleupSwitch )
        self.add_edge( leftupSwitch, leftdownHost )
        self.add_edge( rightupSwitch, rightdownHost )
        self.add_edge( middleupSwitch, middledownSwitch )
        self.add_edge( middledownSwitch, leftdownHost )
        self.add_edge( middledownSwitch, rightdownHost )
        
        
        # Consider all switches and hosts 'on'
        self.enable_all()


topos = { 'mytopo': ( lambda: MyTopo() ) }

