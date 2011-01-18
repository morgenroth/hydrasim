# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="sebastianschildt"
__date__ ="$14.09.2009 16:27:27$"


class LogLine:
    time=-1.0
    node="ANONYMOUS"
    position=(-1.0,-1.0)

    #TODO: Add formatter
    def get_line(self):
        return str(self.time)+"\t"+str(self.node)+"\t"+str(self.position[0])+"\t"+str(self.position[1])

    def print_line(self):
        print(self.get_line())

    def write_line(self,f):
        """Save logline to stream"""
        f.write(self.get_line()+"\n")
