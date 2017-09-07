import json
import os
import subprocess
import configparser

import cherrypy

conf = {
    'global':{
        # 'tools.json_in.on': True,
        # 'tools.json_in.force': False,
        'server.socket_host': 'hostname.hello.com',
        'server.socket_port': 80
    }
}

class SDCardDupe(object):
    @cherrypy.expose
    def index(self):
        return open('../www/index.html', 'r').read()

    @cherrypy.expose
    def posted(self,img_file,devices):
        html_string = "<html><body>"
        html_string += "Image: %s"%img_file
        html_string += "</br>"
        html_string += "Device: %s"%devices
        html_string += "</br>"
        html_string += "</br>"
        html_string += "</body></html>"



        return html_string

    @cherrypy.expose
    def getStatus(self):
        status = "10%"

        return status


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getDevices(self):

        list_devices = []

        # command to get a list of devices on OS
        get_disk_cmd = "lsblk -d | awk -F: '{print $1}' | awk '{print $1}'"
        cmd_device_list_output = subprocess.check_output(get_disk_cmd, shell=True)

        # break down the list to only usb devices
        for device_name in str(cmd_device_list_output.decode("utf-8")).split("\n"):
            if len(device_name) > 0 and 'NAME' not in device_name and 'mmcblk0' not in device_name:

                # get the block size of the device and the gb size
                get_disksize_cmd = "cat /sys/block/" + device_name + "/size"
                cmd_blocksize_output = subprocess.check_output(get_disksize_cmd, shell=True).decode("utf-8").rstrip("\n")
                device_size_gb = str(round(((int(cmd_blocksize_output) / 2) / 1024) / 1024, 2)) + 'G';
                # list_devices[device_name] = str(device_size_gb) + 'G'
                list_devices.append({'name': "/dev/"+device_name, 'size': device_size_gb})

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        # return json.dumps(dict(Devices=list_devices))
        return json.dumps(list_devices)


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def getImages(self):

        list_images = []

        # get the path of images from the ini file
        config = configparser.ConfigParser()
        config.sections()
        config.read('dupe_ui_server.ini')

        # get the list of images and check if valid img file
        for img_file in os.listdir(config['DuplicatorSettings']['ImagePath']):
            img_fullpath = os.path.join(config['DuplicatorSettings']['ImagePath'], img_file)
            if os.path.isfile(img_fullpath) and  os.path.splitext(img_file)[1] == '.img':

                # get the size of the image
                img_filesize_cmd = "ls -sh " + img_fullpath
                img_size_cmd_output = subprocess.check_output(img_filesize_cmd, shell=True).decode("utf-8").rstrip("\n")

                # output is "Size Filename"
                # img_size_gb = round(((int(img_size_cmd_output.split(' ')[0]) / 2) / 1024) / 1024, 2);
                img_size_gb = img_size_cmd_output.split(' ')[0]

                # prep the data to send
                list_images.append({'filename': img_file, 'fullpath': img_fullpath, 'filesize': img_size_gb})

        # send the data as a json
        cherrypy.response.headers['Content-Type'] = 'application/json'
        return json.dumps(list_images)



if __name__ == '__main__':
    cherrypy.quickstart(SDCardDupe(), '/', conf)
