class EchoConsumer(object):
    def __init__(self, channel, format):
        self.channel = channel
        self.format = format
    
    def __call__(self, msg):
        print self.format % {'body': msg.body}
        self.channel.basic_ack(msg.delivery_tag)
