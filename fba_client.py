from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer
import time
import sys

class MulticastClientUDP(DatagramProtocol):

    def datagramReceived(self, datagram, address):
            print("Received:" + repr(datagram))

# Send multicast on 224.0.0.1:8005, on our dynamically allocated port
mes={"foo":"$10","bar":"$30","foo":"$20","bar":"$20","foo":"$30","bar":"$10"}
l=['foo:$10','bar:$30','foo:$20','bar:$20','foo:$30','bar:$10']

print(mes)
pr_nb=int(sys.argv[1])

for h1 in l:
    # h1=str(k+v)
    b1 = h1.encode('utf-8')
    print(h1)
    reactor.listenUDP(0, MulticastClientUDP()).write(b1,
                                                 ('224.0.0.1', pr_nb))
    time.sleep(5)

reactor.run()
