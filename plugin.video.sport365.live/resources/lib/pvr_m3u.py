# -*- coding: utf-8 -*-

import sys,re,os,json,time
from copy import deepcopy

import xbmc,xbmcgui,xbmcaddon
import xbmcplugin


def cron_update(hour,activate):
    try:
        from cron import CronManager,CronJob
        manager = CronManager()
        #get jobs
        jobs = manager.getJobs()
        for job in jobs:
            print job.name
            if 'LivePolishTV' in job.name:  
                manager.deleteJob(job.id)
    except:
        xbmcgui.Dialog().ok('[COLOR red]Problem[/COLOR] ','Wtyczka [COLOR blue]service.cronxbmc[/COLOR] nie jest zainstalowana', 'Funkcja automatycznej aktualizacji nie będzie działać.')
        return False
    
    if activate=='true':
        job = CronJob()
        job.name = "LivePolishTV"
        job.command = 'RunPlugin(plugin://plugin.video.LivePolishTV?mode=AUTOm3u)'
        job.expression = "0 %s * * *"%(hour)
        job.show_notification = "true"
        manager.addJob(job)
        xbmcgui.Dialog().ok('cronxbmc','Automatyczna aktualizacji jest [COLOR blue]AKTYWNA[/COLOR]','Lista m3u będzie odświeżana codziennie o godzinie %s:00'%hour)   
    else:
        xbmcgui.Dialog().ok('cronxbmc','Automatyczna aktualizacji jest [COLOR red]WYŁĄCZONA[/COLOR]')
    return True

def addon_enable_and_set(addonid='pvr.iptvsimple',settings={'m3uPath': 'dupa'}):
    print '_addon_enable_and_set ID=%s' % addonid
    xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","id":1,"params":{"addonid":"%s", "enabled":true}}'%addonid )
    xbmc.sleep(500)
    msg=''
    try:
        pvr_addon = xbmcaddon.Addon(addonid)
        for k,v in settings.items():
            print 'k=%s v=%s' % (k,v)
            pvr_addon.setSetting(k,v)
        msg='PVR aktywny in uaktualniony'
    except:
        msg='[COLOR red]ERROR[/COLOR] PVR nie uaktualniony, zrób to ręcznie'
    return msg    
        
def update_iptv(fname,path,epgTimeShift,epgUrl):       

    m3uPath = os.path.join(path,fname) 
    if os.path.exists(m3uPath):
        xbmc.executebuiltin('StopPVRManager')
        xbmc.executebuiltin('PVR.StopManager')
        new_settings={'m3uPath': m3uPath,'m3uPathType':'0','epgUrl':epgUrl,'epgTimeShift':epgTimeShift,'epgPathType':'1','logoFromEpg':'2'}
        msg=addon_enable_and_set(addonid='pvr.iptvsimple',settings=new_settings)
        
        xbmcgui.Dialog().notification('', msg, xbmcgui.NOTIFICATION_INFO, 1000)
  
        version = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
        print 'Kodi version: %d, checking if PVR is active' % version
        try:
            json_response = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"pvrmanager.enabled"},"id":9}')
            decoded_data = json.loads(json_response)
            pvrmanager = decoded_data.get('result',{}).get('value','')
    
            if not pvrmanager:
                xbmcgui.Dialog().ok('[COLOR red]Telewizja nie jest aktywna![/COLOR] ','Telewizja PVR nie jest aktywaowana', 'Aktywuj i uruchom ponownie jak Telewizja się nie pojawi')
                # http://kodi.wiki/view/Window_IDs
                xbmc.executebuiltin('ActivateWindow(10021)')
        except:
            pass
        
        # json_response = xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Settings.GetSettingValue","params":{"setting":"pvrmanager.enabled"},"id":9}')
        # decoded_data = json.loads(json_response)
        # pvrmanager = decoded_data.get('result',{}).get('value','')
        # if pvrmanager:
        try:
            xbmc.executebuiltin('StartPVRManager')
            xbmc.executebuiltin('PVR.StartManager')
            xbmc.executebuiltin('PVR.SearchMissingChannelIcons')
            xbmc.executebuiltin('Notification(PVR Manager, PVR Manager (re)started, 5000)')
            xbmc.sleep(1000)
        except:
            pass
        xbmc.executebuiltin('Container.Refresh')

    else:
        xbmcgui.Dialog().notification('ERROR', '[COLOR red[Lista m3u jeszcze nie istnieje![/COLOR]', xbmcgui.NOTIFICATION_ERROR, 3000)    

def build_m3u(fname,path,service):
    outfilename = os.path.join(path,fname)     
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create('Tworzę listę programów TV [%s]'%(fname), 'Użuwaj z [COLOR blue]PVR IPTV Simple Client[/COLOR]')
    
    pDialog.update(0,message='Szukam: [%s]'%service)
    mod = __import__(service)
    out_all = mod.getChannels(addheader=True)

    N=len(out_all)
    out_sum=[]
    pDialog.update(0,message= 'Znalazlem %d' % N  )
    
    threadList = []
    threadData = [[] for x in range(N)]
    
    def ThreadFunction(one, threadData, index,N):
        streams = mod.getChannelVideo(one.get('url',''))
        threadData[index]=streams
        done = sum([1 for x in threadData if x ])
        message = '%d/%d %s'%(done,N-1,one.get('title','')) 
        progress = int(done*100.0/N)
        pDialog.update(progress, message=message)
        print "%d\t%s" % (progress,message)    
        
    try:
        from multiprocessing.pool import ThreadPool
        pool = ThreadPool(5)
        for i,one in enumerate(out_all):
            pool.apply_async(ThreadFunction, (one,threadData,i,N-1))
            time.sleep(0.1)
        pool.close()
        pool.join()
        for one,streams in zip(out_all,threadData):
            for stream in streams:
                link = stream.get('url','')
                if link:
                    one['url']=link
                    out_sum.append(deepcopy(one))
    except:
        for i,one in enumerate(out_all):
            progress = int((i)*100.0/N)
            message = '%d/%d %s'%(i,N-1,one.get('title','')) 
            pDialog.update(progress, message=message)
            #print "%d\t%s" % (progress,message)
            streams = mod.getChannelVideo(one.get('url',''))
            for stream in streams:
                print stream
                link = stream.get('url','')
                msg = stream.get('msg','')
                if link:
                    one['url']=link
                    out_sum.append(deepcopy(one))
                elif msg: pDialog.update(progress, message=stream.get('msg'))
    
    pDialog.close()
    if out_sum:
        out_sum.insert(0,out_all[0])
        if createM3Ufile(out_sum,outfilename):
            xbmcgui.Dialog().notification('Lista zapisana', outfilename, xbmcgui.NOTIFICATION_INFO, 10000)
    return out_sum

def createM3Ufile(out,fname='telewizjadatv.m3u'):    
    entry='#EXTINF:-1 tvg-id="{tvid}" group-title="Popularny" tvg-logo="{img}" url-epg="{urlepg}" group-title="{group}",{title}\n{url}\n\n'
    OUTxmu='#EXTM3U\n'
    for one in out:
        OUTxmu=OUTxmu+entry.format(**one)
    myfile = open(fname,'w')
    myfile.write(OUTxmu)
    myfile.close()
    return True