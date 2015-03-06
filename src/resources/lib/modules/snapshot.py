################################################################################
#      This file is part of OpenELEC - http://www.openelec.tv
#      Copyright (C) 2009-2013 Stephan Raue (stephan@openelec.tv)
#      Copyright (C) 2013 Lutz Fiebach (lufie@openelec.tv)
#
#  This program is dual-licensed; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This Program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with OpenELEC; see the file COPYING.  If not, see
#  <http://www.gnu.org/licenses/>.
#
#  Alternatively, you can license this library under a commercial license,
#  please contact OpenELEC Licensing for more information.
#
#  For more information contact:
#  OpenELEC Licensing  <license@openelec.tv>  http://www.openelec.tv
################################################################################
# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals, division
import os
import xbmc
import xbmcgui
import re

class snapshot:

    menu = {'6': {
        'name': 32392,
        'menuLoader': 'menu_connections',
        'listTyp': 'snaplist',
        'InfoText': 32393,
        }}
    
    ENABLED = False

    def __init__(self, oeMain):
        try:
            oeMain.dbg_log('snapshot::__init__', 'enter_function', 0)
            self.oe = oeMain
            self.path = '/var/root/'
            self.part = self.get_block_device()
            self.listItems = {}
            self.update_menu = False
            self.do_fs_resize()
            self.oe.dbg_log('snapshot::__init__', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::__init__', 'ERROR: (' + repr(e) + ')', 4)

    def start_service(self):
        try:
            self.oe.dbg_log('snapshot::start_service', 'enter_function', 0)
            self.oe.dbg_log('snapshot::start_service', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::start_service', 'ERROR: (' + repr(e) + ')', 4)

    def stop_service(self):
        try:
            self.oe.dbg_log('snapshot::stop_service', 'enter_function', 0)
            self.oe.dbg_log('snapshot::stop_service', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::stop_service', 'ERROR: (' + repr(e) + ')', 4)
            
    def exit(self):
        try:
            self.oe.dbg_log('snapshot::exit', 'enter_function', 0)
            self.do_umount()
            self.visible = False
            self.clear_list()
            self.oe.dbg_log('snapshot::exit', 'exit_function', 0)
            pass
        except Exception, e:
            self.oe.dbg_log('snapshot::exit', 'ERROR: (' + repr(e) + ')', 4)

    def do_init(self):
        try:
            self.oe.dbg_log('snapshot::do_init', 'exit_function', 0)
            self.visible = True
            self.menu_connections(None)
            self.oe.dbg_log('snapshot::do_init', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::do_init', 'ERROR: (%s)' % repr(e))

    # ###################################################################
    # # Snapshot GUI
    # ###################################################################

    def clear_list(self):
        try:
            self.oe.dbg_log('snapshot::clear_list', 'enter_function', 0)
            remove = [entry for entry in self.listItems]
            for entry in remove:
                del self.listItems[entry]
            self.oe.dbg_log('snapshot::clear_list', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::clear_list', 'ERROR: (' + repr(e) + ')', 4)

    def menu_connections(self, focusItem=None):
        try:
            if not hasattr(self.oe, 'winOeMain'):
                return 0
            if not self.oe.winOeMain.visible:
                return 0
            self.oe.dbg_log('snapshot::menu_connections', 'enter_function', 0)
            if not self.part:
                self.oe.winOeMain.getControl(1601).setLabel(self.oe._(32394))
                self.clear_list()
                self.oe.winOeMain.getControl(int(self.oe.listObject['snaplist'])).reset()
                self.oe.dbg_log('snapshot::menu_connections', 'exit_function (not on btrfs root)', 0)
                return
            dictProperties = {}
            
            # type 1=int, 2=string, 3=array, 4=bool
            
            properties = {
                0: {
                    'type': 2,
                    'value': 'ID',
                    },
                1: {
                    'type': 2,
                    'value': 'gen',
                    },
                2: {
                    'type': 2,
                    'value': 'cgen',
                    },
                3: {
                    'type': 2,
                    'value': 'top level',
                    },
                5: {
                    'type': 2,
                    'value': 'otime',
                    },
                6: {
                    'type': 2,
                    'value': 'path',
                    },
                }
            
            rebuildList = 0
            self.listSnaps = self.list_snapshots()
            activeSub = self.get_active()['ID']
            if len(self.listSnaps) != len(self.listItems):
                rebuildList = 1
                self.oe.winOeMain.getControl(int(self.oe.listObject['snaplist'])).reset()
                self.clear_list()
            else:
                for snap in self.listSnaps:
                    if snap not in self.listItems:
                        rebuildList = 1
                        self.oe.winOeMain.getControl(int(self.oe.listObject['snaplist'])).reset()
                        self.clear_list()
                        break
            for snap in self.listSnaps:
                dictProperties = {}
                snapName = ''
                dictProperties['entry'] = snap
                dictProperties['modul'] = self.__class__.__name__
                dictProperties['action'] = 'open_context_menu'
                dictProperties['custom'] = ''
                if 'path' in self.listSnaps[snap]:
                    snapName = self.listSnaps[snap]['path']
                for prop in properties:
                    name = properties[prop]['value']
                    if name in self.listSnaps[snap]:
                        value = self.listSnaps[snap][name]
                        if name == 'ID':
                            if value == activeSub:
                                dictProperties['active'] = 1
                            else:
                                dictProperties['active'] = 0
                        if properties[prop]['type'] == 1:
                            value = unicode(int(value))
                        if properties[prop]['type'] == 2:
                            value = unicode(value)
                        if properties[prop]['type'] == 3:
                            value = unicode(len(value))
                        if properties[prop]['type'] == 4:
                            value = unicode(int(value))
                        dictProperties[name] = value
                        
                if rebuildList == 1:
                    self.listItems[snap] = self.oe.winOeMain.addConfigItem(snapName, dictProperties, self.oe.listObject['snaplist'])
                else:
                    if self.listItems[snap] != None: 
                        self.listItems[snap].setLabel(snapName)
                        for dictProperty in dictProperties:
                            self.listItems[snap].setProperty(dictProperty, unicode(dictProperties[dictProperty]))
            self.update_menu = False
            self.oe.dbg_log('snapshot::menu_connections', 'exit_function', 0)
        except Exception, e:
            self.update_menu = False
            self.oe.dbg_log('snapshot::menu_connections', 'ERROR: (' + repr(e) + ')', 4)

    def open_context_menu(self, listItem):
        try:
            self.oe.dbg_log('snapshot::show_options', 'enter_function', 0)
            values = {}
            if listItem is None:
                listItem = self.oe.winOeMain.getControl(self.oe.listObject['snaplist']).getSelectedItem()
            if listItem.getProperty('active') == '1':
                values[1] = {
                    'text': self.oe._(32397),
                    'action': 'create_snapshot',
                    }
            elif listItem.getProperty('active') == '0':
                values[1] = {
                    'text': self.oe._(32398),
                    'action': 'delete_snapshot',
                    }
                values[2] = {
                    'text': self.oe._(32399),
                    'action': 'activate_snapshot',
                    }
                values[3] = {
                    'text': self.oe._(32400),
                    'action': 'custom_snap_name',
                    }
            items = []
            actions = []
            for key in values.keys():
                items.append(values[key]['text'])
                actions.append(values[key]['action'])
            select_window = xbmcgui.Dialog()
            title = self.oe._(32012).encode('utf-8')
            result = select_window.select(title, items)
            if result == 2:
                listItem.setProperty('custom', unicode(select_window.input('Enter Custom Name', type=xbmcgui.INPUT_ALPHANUM)))
            if result >= 0:
                getattr(self, actions[result])(listItem)
            self.oe.dbg_log('snapshot::show_options', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::show_options', 'ERROR: (' + repr(e) + ')', 4)

    # ###################################################################
    # # btrfs Main
    # ###################################################################
  
    def do_mount(self):
        try:
            self.oe.dbg_log('snapshot::do_mount', 'enter_function', 0)
            if not os.path.exists(self.path):
                os.mkdir(self.path)
            if not os.path.ismount(self.path):
                self.oe.execute(' '.join(['mount -o subvolid=0', self.part, self.path]), get_result=0)
            self.oe.dbg_log('snapshot::do_mount', 'exit_function', 0)
            return True
        except Exception, e:
            self.oe.dbg_log('snapshot::do_mount', 'ERROR: (' + repr(e) + ')', 4)
            return False

    def do_umount(self):
        try:
            self.oe.dbg_log('snapshot::do_umount', 'enter_function', 0)
            if os.path.ismount(self.path):
                self.oe.execute('umount ' + self.path, get_result=0)
            if os.path.exists(self.path):
                os.rmdir(self.path)
            self.oe.dbg_log('snapshot::do_umount', 'exit_function', 0)
            return True
        except Exception, e:
            self.oe.dbg_log('snapshot::do_umount', 'ERROR: (' + repr(e) + ')', 4)
            return False
    
    def do_fs_resize(self):
        try: 
            self.oe.dbg_log('snapshot::do_fs_resize', 'enter_function', 0)
            if os.path.exists('/storage/.please_resize_me'):
                if self.do_mount():
                    self.oe.execute(' '.join(['btrfs filesystem resize max', self.path]), get_result=0)
                    os.remove('/storage/.please_resize_me')
            self.oe.dbg_log('snapshot::do_fs_resize', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::do_fs_resize', 'ERROR: (' + repr(e) + ')', 4)

    def get_block_device(self):
        try:
            self.oe.dbg_log('snapshot::get_block_device', 'enter_function', 0)
            with open('/proc/mounts') as f:
                for line in f:
                    if '/flash' in line:
                        mount = line.strip().split()
                        break
            self.oe.dbg_log('snapshot::get_block_device', 'exit_function', 0)
            if mount[2] == 'btrfs':
                return mount[0]
        except Exception, e:
            self.oe.dbg_log('snapshot::get_block_device', 'ERROR: (' + repr(e) + ')', 4)
                        
    def list_snapshots(self):
        try:
            self.oe.dbg_log('snapshot::list_snapshots', 'enter_function', 0)
            if self.do_mount():
                subvolumes = self.oe.execute(' '.join(['btrfs subvolume list -c', self.path]), get_result=1)
                #           ID 257 gen 2548 cgen 6 top level 5 path boot_old
                
                snapshots = self.oe.execute(' '.join(['btrfs subvolume list -s', self.path]), get_result=1) 
                #           ID 261 gen 286 cgen 217 top level 5 otime 2015-03-03 21:43:57 path boot

            properties = ['ID','gen','cgen','top level','otime','path']

            subs = {}
            listsubs = {}
            for i, line in enumerate(subvolumes.split('\n')):
                if len(line) != 0:
                    subs[i] = line.strip().split()
                    for j in 9, 7, 6, 4, 2, 0:
                        subs[i].remove(subs[i][j])
                    subs[i].insert(4,'')
                    listsubs[i] = dict(zip(properties, subs[i]))
                                            
            snaps = {}
            listsnaps = {}
            for i, line in enumerate(snapshots.split('\n')):
                if len(line) != 0:
                    snaps[i] = line.strip().split()
                    for j in 12, 9, 7, 6, 4, 2, 0:
                        snaps[i].remove(snaps[i][j])
                    snaps[i][4] = snaps[i][4] + ' ' + snaps[i][5]
                    snaps[i].remove(snaps[i][5])    
                    listsnaps[i] = dict(zip(properties, snaps[i]))

            listdiff = {}
            for i in listsubs:
                if listsubs[i]['path'] != 'storage':
                    same = False
                    for j in listsnaps:
                        if listsubs[i]['ID'] == listsnaps[j]['ID']:
                            same = True
                        else:
                            pass
                    if not same:
                        listdiff[i] = listsubs[i]
            
            for i in listdiff:
                listsnaps[len(listsnaps) + 1] = listdiff[i]
            
            self.oe.dbg_log('snapshot::list_snapshots', 'exit_function', 0)
            return listsnaps
        except Exception, e:
            self.oe.dbg_log('snapshot::list_snapshots', 'ERROR: (' + repr(e) + ')', 4)
            
    def create_snapshot(self, listItem):
        try:
            self.oe.dbg_log('snapshot::create_snapshot', 'enter_function', 0)
            if listItem is None:
                listItem = self.oe.winOeMain.getControl(self.oe.listObject['snaplist']).getSelectedItem()
            if listItem is None:
                return
            snapname = self.path + listItem.getProperty('path')
            #                          btrfs subvolume snapshot /var/root/'name' /var/root/'name'-'timestamp'
            self.oe.execute(' '.join(['btrfs subvolume snapshot', snapname, snapname + '-' + self.oe.timestamp()]), get_result=0)
            self.oe.dbg_log('snapshot::create_snapshot', 'exit_function', 0)
            self.oe.set_busy(0)
        except Exception, e:
            self.oe.set_busy(0)
            self.oe.dbg_log('snapshot::create_snapshot', 'ERROR: (' + repr(e) + ')', 4)
            
    def delete_snapshot(self, listItem):
        try:
            self.oe.dbg_log('snapshot::delete_snapshot', 'enter_function', 0)
            if listItem is None:
                listItem = self.oe.winOeMain.getControl(self.oe.listObject['snaplist']).getSelectedItem()
            if listItem is None:
                return
            #                          btrfs subvoume delete --commit-after /var/root/'name'
            self.oe.execute(' '.join(['btrfs subvolume delete --commit-after', self.path + listItem.getProperty('path')]), get_result=0)
            self.oe.dbg_log('snapshot::delete_snapshot', 'exit_function', 0)
            self.oe.set_busy(0)
        except Exception, e:
            self.oe.set_busy(0)
            self.oe.dbg_log('snapshot::delete_snapshot', 'ERROR: (' + repr(e) + ')', 4)
            
    def get_active(self):
        try:
            self.oe.dbg_log('snapshot::get_active', 'enter_function', 0)
            active = self.oe.execute(' '.join(['btrfs subvolume get-default', self.path]), get_result=1)
#           ID 256 gen 13 top level 5 path system
            properties = ['ID', 'gen', 'top level', 'path']
            active = active.strip('\n').strip().split()
            for i in 7, 5, 4, 2, 0:
                active.remove(active[i])
            activeDict = dict(zip(properties, active))
            self.oe.dbg_log('snapshot::get_active', 'exit_function', 0)
            return activeDict
        except Exception, e:
            self.oe.dbg_log('snapshot::get_active', 'ERROR: (' + repr(e) + ')', 4)

    def activate_snapshot(self, listItem):
        try:
            self.oe.dbg_log('snapshot::activate_snapshot', 'enter_function', 0)
            if listItem is None:
                listItem = self.oe.winOeMain.getControl(self.oe.listObject['snaplist']).getSelectedItem()
            if listItem is None:
                return
            self.oe.execute(' '.join(['btrfs subvolume set-default', listItem.getProperty('ID'), self.path]) , get_result=0)
            self.oe.execute(' '.join(['extlinux -i', self.path]) , get_result=0)
                
            f = open(self.path + listItem.getProperty('path') + '/extlinux.conf','r')
            filedata = f.read()
            f.close()
            
            prog = re.compile('(.*)(subvol=.*?),(.*)(subvol=\w+)(.*)', re.S)
            old = prog.match(filedata)
            
            newdata = filedata.replace(old.group(2), 'subvol=' + listItem.getProperty('path'))
            
            if old.group(2) == 'subvol=' + listItem.getProperty('path'):
                f.close()
                return
            
            f = open(self.path + listItem.getProperty('path') + '/extlinux.conf','w')
            f.write(newdata)
            f.close()

            self.oe.dbg_log('snapshot::activate_snapshot', 'exit_function', 0)
            self.oe.set_busy(0)
        except Exception, e:
            self.oe.set_busy(0)
            self.oe.dbg_log('snapshot::activate_snapshot', 'ERROR: (' + repr(e) + ')', 4)
            
    def custom_snap_name(self, listItem):
        try:
            self.oe.dbg_log('snapshot::custom_snap_name', 'enter_function', 0)
            if listItem is None:
                listItem = self.oe.winOeMain.getControl(self.oe.listObject['snaplist']).getSelectedItem()
            if listItem is None:
                return
            for snap in self.listSnaps:
                if self.listSnaps[snap]['path'] == listItem.getProperty('custom'):
                    duplicateName = xbmcgui.Dialog()
                    duplicateName.ok('Duplicate Name', 'Please choose a different name')
                    return
            #                          mv /var/root/'name' /var/root/'newname'
            self.oe.execute(' '.join(['mv', self.path + listItem.getProperty('path'), self.path + listItem.getProperty('custom')]), get_result=0)
            self.oe.dbg_log('snapshot::custom_snap_name', 'exit_function', 0)
        except Exception, e:
            self.oe.dbg_log('snapshot::custom_snap_name', 'ERROR: (' + repr(e) + ')', 4)
