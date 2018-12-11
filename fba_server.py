from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.application.internet import MulticastServer
import pickledb
import sys
import pickle
import re


mes=None
des=None
prevVot=None
prevCon=None
prevmessage=None
count=0
conCount=0
voteCount=0
confirmCount=0
port=[3001,3002,3000,3003]

list=[]
lm=['foo:$10','bar:$30','foo:$20','bar:$20','foo:$30','bar:$10']

class MulticastServerUDP(DatagramProtocol):
    def startProtocol(self):
        print ('Started Listening')
        # Join a specific multicast group, which is the IP we will respond to
        self.transport.joinGroup('224.0.0.1')

    def datagramReceived(self, datagram, address):
        # The uniqueID check is to ensure we only service requests from
        # ourselves
        c=datagram
        print(c)
        global mes
        global count
        global des
        global voteCount
        global conCount
        global prevVot
        global prevCon
        global prevmessage
        if  count==0:
            list.append(mes)
        print(list)

        mes=c.decode('UTF-8')

        print("message recieved in server",mes ,count )
        print("prevote recieved in server",prevVot)
        if  prevmessage==None and count==0 and conCount==0  and voteCount==0  and prevCon==None and prevVot==None:
            print("++++++++++++++++++++++++++++++++1+++++++++++++++++++++++++++++++++++++++",count)
            prevmessage=mes
            self.datagramSend(prevmessage)
            count+=1
        elif prevmessage!=None and prevmessage==mes and count<4  and prevCon==None and prevVot==None:
            print("++++++++++++++++++++++++++++++++2+++++++++++++++++++++++++++++++++++++++",count)
            count+=1
            self.datagramSend(prevmessage)
        elif count>=3 and count<6 and prevVot==None and prevCon==None and prevmessage==mes and voteCount==0 :
            print("++++++++++++++++++++++++++++++++3+++++++++++++++++++++++++++++++++++++++",count)
            prevVot=prevmessage
            self.voting(prevVot)
            print("ratifying has been done+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" ,prevVot)
            count=0
            prevmessage=None
        elif 'v' in mes and prevVot==mes and voteCount<3 and prevCon==None and prevmessage==None:
            print("++++++++++++++++++++++++++++++++4+++++++++++++++++++++++++++++++++++++++",voteCount)
            voteCount+=1
        elif 'v' in mes and  voteCount<6 and prevVot==mes and prevCon==None and prevmessage==None:
            print("++++++++++++++++++++++++++++++++5+++++++++++++++++++++++++++++++++++++++",voteCount)
            mes.replace('v', '')
            mes.strip('v')
            prevCon=mes
            print("voting has been done+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",prevCon)
            voteCount=0
            prevVot=None
            mes = None
            prevCon.replace('v', '')
            prevCon.strip('v')
            self.confirm(prevCon.strip('v'))
            conCount+=1
        elif 'c' in mes and  conCount>1 and conCount<4 and prevCon==mes and prevmessage==None:
            print("++++++++++++++++++++++++++++++++6+++++++++++++++++++++++++++++++++++++++",conCount)
            conCount+=1
        elif 'c' in mes and conCount<6 and prevCon==mes and prevmessage==None:
            print("++++++++++++++++++++++++++++++++7+++++++++++++++++++++++++++++++++++++++",conCount)
            mes.replace('c', '')
            mes.strip('c')
            print("confirmation has been achieved for this node++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++", mes)
            self.storinDb(mes)
            prevCon = None
            conCount = 0
            mes=None

    def storinDb(self,data):
        global db
        data.replace('v', '')
        data.strip('v')
        data.replace('c', '')
        data.strip('c')
        data.replace('vc', '')
        data.strip('vc')

        data = re.sub('[vc]', '', data)
        a = data.split(':$')

        print(a)
        f = db.get(a[0])
        # print(f)
        if f == False:
            j=int(a[1])
            db.set(a[0],j)
        else:
            g=int(db.get(a[0]))
            d = int(g) + int(a[1])
            db.set(a[0],d)
        db.dump()
        print(db)


    def voting(self,prevVots):
        global prevVot
        global voteCount
        prevVot=prevVots+'v'
        voteCount+=1
        self.datagramSend(prevVot)

    def confirm(self,prevCons):
        global prevCon
        global conCount
        prevCon=prevCons+'c'
        conCount+=1
        self.datagramSend(prevCon)


    def datagramSend(self,message, address=None):
        global mes
        print("message for other server",mes)
        mes=message.encode("UTF-8")
        global port
        print(port)
        for i in port:
            if i!=pr_nb:
                self.transport.write(mes, ('224.0.0.1', i))


pr_nb=int(sys.argv[1])
dbname='example'+str(pr_nb)+'.db'
db = pickledb.load(dbname, False)

reactor.listenMulticast(pr_nb, MulticastServerUDP())

reactor.run()
