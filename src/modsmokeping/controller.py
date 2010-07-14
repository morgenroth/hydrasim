import time
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="schildt"
__date__ ="$05.05.2010 14:12:21$"

from modbasic import controller
import subprocess
import os
import basics
import time

class SmokepingController(controller.BasicController):

    def __init__(self, setupdir, config):
        super(SmokepingController,self).__init__(setupdir, config)
        print("Smokeping controller")

        self.category = config.get('modsmokeping','smokepingcategory')
        self.runtime  = config.getint('modsmokeping','minutes')

        


    def run(self):
        if self.config.has_section('mobility'):
            mobility = MobilityModel(self.config, self.nodes)
            mobility.start()


        masters={}
        for node in self.nodes:
            if node.vhost.master.name not in masters:
                masters[node.vhost.master.name]=[]
            masters[node.vhost.master.name].append(node)

        print("Configuring smokeping")
        smokepingcfg=self.setupdir+"/smokepingtargets_"+self.category
        print(smokepingcfg)
        st = open(smokepingcfg,'w')


        st.write("*** Targets ***\n")
        st.write("probe = FPing\n")
        st.write("menu = Top\n")
        st.write("title = HYDRA smokeping configuration\n")
        st.write("remark = HYDRA: automatically generated smokeping configuration\n\n")

        #Add physical node
        st.write("+ Physical\n")
        st.write('menu = Physical\n')
        st.write('title = Physical\n')

        st.write('\n')


        st.write("++ RSPro\n")
        st.write("menu = RSPro\n")
        st.write("title = "+self.config.get('modsmokeping','physical')+'\n')
        st.write("host = "+self.config.get('modsmokeping','physical')+'\n')
        st.write('\n')


        for master,nodes in masters.iteritems():
            st.write("+ "+self.category+'_'+master+'\n')
            st.write('menu = '+self.category+": "+master+'\n')
            st.write('title = '+self.category+": "+master+'\n')

            st.write('\n')

            masteraddr=self.config.get(master,'host')

            st.write("++ Master_"+master+'\n')
            st.write("menu = Master_"+master+'\n')
            st.write("title = "+masteraddr+'\n')
            st.write("host = "+masteraddr+'\n')
            st.write('\n')


            for node in nodes:
                st.write("++ "+node.name+'\n')
                st.write("menu = "+node.name+'\n')
                st.write("title = "+node.address+'\n')
                st.write("host = "+node.address+'\n')
                st.write('\n')

            st.write('\n')

        st.close()

        #Smokeping off?
        self.stop=True
        p = subprocess.Popen("/etc/init.d/smokeping status", shell=True)
        status = os.waitpid(p.pid, 0)[1]
        if status == 0:
            print("Smokeping is running. I will not touch it.")
            self.stop=False
        else:
            print("Configuring smokeping")
            #basics.sudo("mv /etc/smokeping/config.d/Targets /etc/smokeping/config.d/Targets_old")
            #Todo: Replace in basics? os.system is deprecated
            #subprocess.call("sudo cp "+self.setupdir+"/smokepingtargets etc/smokeping/config.d/Probes")
            basics.sudo("cp "+smokepingcfg+" /etc/smokeping/config.d/Targets")

            print("Starting smokeping")
            ret = subprocess.call("sudo /etc/init.d/smokeping start", shell=True)
            if ret != 0:
                print("Problems starting smokeping")

        if self.runtime == 0 or self.runtime == -1:
            print("No timeout. Run until user aborts")
            print ("- run simulation -")
            raw_input(u'Press key to abort.')
        else:
            print("Running for "+str(self.runtime)+" minutes")
            time.sleep(self.runtime*60)

        if self.stop:
            print("Stopping smokeping")
            ret = subprocess.call("sudo /etc/init.d/smokeping stop", shell=True)
            if ret != 0:
                print("Problems stopping smokeping")
        #basics.sudo("rm /etc/smokeping/config.d/Targets")
        #basics.sudo("mv /etc/smokeping/config.d/Targets_old /etc/smokeping/config.d/Targets")


        print("Simulation finished. Taking down nodes")
