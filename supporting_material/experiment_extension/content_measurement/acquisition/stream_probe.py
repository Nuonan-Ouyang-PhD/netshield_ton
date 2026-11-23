"""Content-only Wi-Fi probe. No truth labels are deployed."""
import base64
import hashlib
import json
import socket
import struct
import time
from collections import deque

import numpy as np

def send(stream, obj):
    stream.write(json.dumps(obj,separators=(',',':')).encode()+b'\n')
    stream.flush()

def receive(stream):
    return json.loads(stream.readline())

def measure(cfg):
    model=cfg['light']
    stamp=time.monotonic_ns
    boot=open('/proc/sys/kernel/random/boot_id').read().strip()
    sock=socket.create_connection((cfg['address'],cfg['port']),timeout=40,source_address=(cfg['source'],0))
    sock.setsockopt(socket.IPPROTO_TCP,socket.TCP_NODELAY,1)
    with sock, sock.makefile('rwb') as channel:
        send(channel,{'role':cfg['role'],'token':cfg['token'],'boot':boot})
        for arm in cfg['arms']:
            queue=deque()
            next_item=0
            while True:
                tick=receive(channel)
                if tick['op']=='finish':
                    assert not queue and next_item==len(arm['items'])
                    send(channel,{'finished':arm['id']});break
                assert tick['arm']==arm['id']
                created=None
                if tick['generate'] and next_item<len(arm['items']):
                    item=arm['items'][next_item];next_item+=1
                    origin=stamp()
                    features=np.asarray(item['x'],dtype=float)
                    raw=encode(features,arm['width'],model)
                    padded=raw+bytes(arm['size']-len(raw))
                    created={'id':item['id'],'created':origin,'encoded':stamp(),'hash':hashlib.sha256(raw).hexdigest(),'padded_hash':hashlib.sha256(padded).hexdigest()}
                    queue.append([item['id'],padded,0])
                send(channel,{'created':created,'demand':sum(len(b)-off for _,b,off in queue)})
                grant=receive(channel)['grant'];parts=[];segments=[]
                while grant:
                    identifier,payload,off=queue[0]
                    n=min(len(payload)-off,grant)
                    segments.append([identifier,off,n])
                    parts.append(payload[off:off+n]);grant-=n;queue[0][2]+=n
                    if queue[0][2]==len(payload):queue.popleft()
                send(channel,segments)
                channel.write(b''.join(parts));channel.flush()
                # Timestamp each result as its entire application frame arrives.
                receipts=[]
                while True:
                    frame=receive(channel)
                    instant=stamp()
                    if frame['op']=='end':break
                    assert frame['op']=='result'
                    receipts.append({'id':frame['id'],'score':frame['score'],'returned':instant})
                send(channel,{'receipts':receipts,'horizon':stamp()})
