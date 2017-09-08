import json
import os
import subprocess
import configparser

import cherrypy

# Todo: too many config_parse blocks, create a function to easily call it

class SDCardDupe(object):
    @cherrypy.expose
    def index(self):

        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read('server.ini')

        # Get webpage, then replace needed parts here
        html_string = open('../www/index.html', 'r').read()
        html_string = html_string.replace("replacewithhostnamehere",config_parse['DuplicatorSettings']['Host'])

        css_string = '<style>' + open(config_parse['DuplicatorSettings']['SkeletonLocation'], 'r').read() + '</style>'
        html_string = html_string.replace("<style></style>",css_string)

        return html_string

    @cherrypy.expose
    def posted(self,img_file,devices):

        # get all mounted items on the rpi
        mounted_list = []
        mounted_volumes_output = subprocess.check_output("mount", shell=True)
        for mount_line in str(mounted_volumes_output.decode("utf-8")).split("\n"):
            device_name = mount_line.split(" on ",1)[0]
            if device_name not in mounted_list:
                mounted_list.append(device_name)

        # nested for loop, maybe we can optimize this later
        for dev_path in devices:

            reduced_list = []
            for mounted_item in mounted_list:
                # assumptions made, there will be no collisions, dont have to pop element
                # but to reduce the cost of loop, will pop element by creating new list
                if dev_path in mounted_item:
                    umount_disk_cmd = "sudo umount %s"%mounted_item
                    subprocess.call(umount_disk_cmd.split(" "))
                else:
                    reduced_list.append(mounted_item)

            mounted_list = []
            mounted_list.extend(reduced_list)


        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read('server.ini')

        dd_cmd = "sudo dcfldd bs=4M if=" + img_file + " of="
        dd_cmd += " of=".join(devices)
        dd_cmd += " sizeprobe=if statusinterval=1 2>&1 | tee "
        dd_cmd += config_parse['DuplicatorSettings']['Logs'] + "/progress.info"

        if not os.path.exists(config_parse['DuplicatorSettings']['Logs']):
            os.makedirs(config_parse['DuplicatorSettings']['Logs'])

        subprocess.call(dd_cmd.split(" "))

        html_string = "Javascript to redirect to monitor here"

        return html_string

    @cherrypy.expose
    def getStatus(self):
        # get host configs from server.ini
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read('server.ini')
        progress_file = config_parse['DuplicatorSettings']['Logs'] + "/progress.info"

        cat_cmd = "sudo cat "+ progress_file
        cat_output = str(subprocess.check_output(cat_cmd, shell=True).decode("utf-8"))
        if "%" in cat_output:
            percentage = cat_output.split(" of ")[-2].split("[")[-1]

        return percentage



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
        config_parse = configparser.ConfigParser()
        config_parse.sections()
        config_parse.read('server.ini')

        # get the list of images and check if valid img file
        for img_file in os.listdir(config_parse['DuplicatorSettings']['ImagePath']):
            img_fullpath = os.path.join(config_parse['DuplicatorSettings']['ImagePath'], img_file)
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

    # get host configs from server.ini
    config_parse = configparser.ConfigParser()
    config_parse.sections()
    config_parse.read('server.ini')

    conf = {
        'global':{
            # 'tools.json_in.on': True,
            # 'tools.json_in.force': False,
            'server.socket_host': config_parse['DuplicatorSettings']['Host'],
            'server.socket_port': int(config_parse['DuplicatorSettings']['SocketPort'])
        }
    }



    cherrypy.quickstart(SDCardDupe(), '/', conf)
