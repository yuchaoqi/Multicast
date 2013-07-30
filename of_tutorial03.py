# Copyright 2012 James McCauley
#
# This file is part of POX.
#
# POX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# POX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with POX.  If not, see <http://www.gnu.org/licenses/>.

"""
This component is for use with the OpenFlow tutorial.

It acts as a simple hub, but can be modified to act like an L2
learning switch.

It's quite similar to the one for NOX.  Credit where credit due. :)
"""

from pox.lib.packet import *
from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.gf as gf

log = core.getLogger()



class Tutorial (object):
  """
  A Tutorial object is created for each switch that connects.
  A Connection object for that switch is passed to the __init__ function.
  """
  def __init__ (self, connection):
    # Keep track of the connection to the switch so that we can
    # send it messages!
    self.connection = connection

    # This binds our PacketIn event listener
    connection.addListeners(self)

    # Use this table to keep track of which ethernet address is on
    # which switch port (keys are MACs, values are ports).
    self.mac_to_port = {}
    self.myGF = gf.GF(8, 0X187)


  def resend_packet (self, packet_in, out_port):
    """
    Instructs the switch to resend a packet that it had sent to us.
    "packet_in" is the ofp_packet_in object the switch had sent to the
    controller due to a table-miss.
    """
    msg = of.ofp_packet_out()
    msg.data = packet_in

    # Add an action to send to the specified port
    action = of.ofp_action_output(port = out_port)
    msg.actions.append(action)

    # Send message to switch
    self.connection.send(msg)

  def parseUDPPacket(self, packet):
   # parse the IP packet into udp Packet
    if packet.type == ethernet.IP_TYPE:
      ip_packet = packet.payload
      if ip_packet.protocol == ipv4.UDP_PROTOCOL:
        udp_packet = ip_packet.payload
        udp_payload = udp_packet.payload
        if type(udp_payload) == bytes:
	  log.debug("udpPacket payload: %s"% udp_payload)
 	elif isinstance(udp_payload, packet_base):
	  log.debug("udpPacket payload is the istance of packet_base")
	else:
	  log.debug("cannot parse udpPacket")

	# Get the udpPayload Length
	assert isinstance(udp_packet, bytes)
        udpPacketLen = len(udp_packet)
        udp_payloadLen = udpPacketLen -8
        log.debug("udp_payloadLen is : %d"% udp_payloadLen)

        # Try to encode udp_payload with the pre_bytes
	log.debug("Print udpPayload :")
	print udp_payload
	pre_bytes = 'aaaaaaaaaaaaaaa'
	log.debug("pre_bytesLen is : %d"% len(pre_bytes))
	# a*X ^ b*Y
	encodeNum1 = 2
	encodeNum2 = 1
	encodedBytes = self.myGF.encode_mul_XOR(pre_bytes,encodeNum1,udp_payload,encodeNum2)
	
	# encodedBytes = self.myGF.gf_XOR(pre_bytes,udp_payload)	
	log.debug("encodedBytes are : %s"% encodedBytes)

	# Try to decode the original udp_payload
	## Try to decode the pre_bytes(paket1)
	##decodedBytes = self.myGF.decode_div_XOR(udp_payload, encodeNum2, encodeNum1, encodedBytes, len(pre_bytes)) 	
	## Try to decode the udp_payload(packet2)
	decodedBytes = self.myGF.decode_div_XOR(pre_bytes, encodeNum1, encodeNum2, encodedBytes, len(udp_payload))
	decodedBytes = self.myGF.gf_XOR(pre_bytes, encodedBytes)
	log.debug("decodedBytes are : %s" % decodedBytes)
	
	# if this packet is udp_packet, return 1
	return 1
    return 0

  def act_like_hub (self, packet, packet_in):
    """
    Implement hub-like behavior -- send all packets to all ports besides
    the input port.
    """

    # We want to output to all ports -- we do that using the special
    # OFPP_ALL port as the output port.  (We could have also used
    # OFPP_FLOOD.)
    """
	if packet.dst == '10.0.1.2'
        self.resend_packet(packet_in, 1)
	return
    """
    self.resend_packet(packet_in, of.OFPP_ALL)

    # Note that if we didn't get a valid buffer_id, a slightly better
    # implementation would check that we got the full data before
    # sending it (len(packet_in.data) should be == packet_in.total_len)).


  def act_like_switch (self, packet, packet_in, event):
    self.mac_to_port[packet.src] = event.port
    udpFlag = self.parseUDPPacket(packet)
    if 1==udpFlag:
      log.debug("Get a udp packet from %s to %s "%(packet.src, packet.dst))
    
    if packet.dst.is_multicast:
      self.resend_packet(packet_in, of.OFPP_ALL)
      log.debug ("This packet is a Multicast packet!")
    else:
      if packet.dst not in self.mac_to_port:
        # Flood the packet out everything but the input port
        self.resend_packet(packet_in, of.OFPP_ALL)
      else:
        port = self.mac_to_port[packet.dst]
        if port == event.port:
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          return
        log.debug("installing flow for %s.%i -> %s.%i" % (packet.src, event.port, packet.dst, port))
          # Install flow table entry in the switch so that this flow goes out the appopriate port
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port = port)) 
        msg.data = event.ofp # Send the packet out appropriate port
        self.connection.send(msg)          

  def _handle_PacketIn (self, event):
    """
    Handles packet in messages from the switch.
    """

    packet = event.parsed # This is the parsed packet data.
    if not packet.parsed:
      log.warning("Ignoring incomplete packet")
      return

    packet_in = event.ofp # The actual ofp_packet_in message.

    # Comment out the following line and uncomment the one after
    # when starting the exercise.
    #self.act_like_hub(packet, packet_in)
    self.act_like_switch(packet, packet_in, event)



def launch ():
  """
  Starts the component
  """
  def start_switch (event):
    log.debug("Controlling %s" % (event.connection,))
    Tutorial(event.connection)
  core.openflow.addListenerByName("ConnectionUp", start_switch)
