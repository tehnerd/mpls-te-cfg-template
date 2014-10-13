import jinja2
import sys
from string import join
import socket
import sqlite3




class CfgContext(object):
    def __init__(self):
        self.cfg_dict = dict()
        #need to check jinja2 docs about something more usefull
        self.TEMPLATE_DIR = './'
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.TEMPLATE_DIR))

    
    def cfg_from_cli(self,cfg_line):
        if len(cfg_line) < 4:
            print("arguments must be: <vendor> <descr/lsp name> <tunnel_num> <hosts>...")
            sys.exit(-1)
        if len(cfg_line[0].split(':')) > 1:
            vendor = cfg_line[0].split(':')[0]
            dbname = cfg_line[0].split(':')[1]
        else:
            vendor = cfg_line[0]
            dbname = None
        self.cfg_dict['vendor'] = vendor
        self.cfg_dict['lsp_name'] = cfg_line[1]
        self.cfg_dict['tunnel_num'] = cfg_line[2]
        self.cfg_dict['nodes'] = list()
        node_id = 3
        node_name_dict = dict()
        if dbname != None:
            '''
            dbname must be rlist and it must be in format <hostname>:<ip_address>
            '''
            db = sqlite3.connect(dbname)
            cur = db.cursor()
            cur.execute("select * from rlist")
            data = cur.fetchall()
            db.close()
            for line in data:
                node_name_dict[line[0]] = line[1]
        while node_id < len(cfg_line):
            if dbname != None:
                node_ip = node_name_dict[cfg_line[node_id]]
            else:
                node_ip = socket.gethostbyname(cfg_line[node_id])
            self.cfg_dict['nodes'].extend((node_ip,))
            node_id += 1

    def render_template(self):
        template_name = join((self.TEMPLATE_DIR,
                              "mpls-te-cfg.jinja"),'')
        template = self.env.get_template(template_name)
        print template.render(cfg_dict = self.cfg_dict)

def main():
    cfg_context = CfgContext()
    cfg_context.cfg_from_cli(sys.argv[1:])
    print(cfg_context.cfg_dict)
    cfg_context.render_template()




if __name__ == '__main__':
    main()
