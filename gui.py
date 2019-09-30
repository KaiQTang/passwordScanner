from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from scanner import loadJson
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.scrollview import ScrollView
import traceback
import os
import subprocess
import json
from scanner import addFiles
from kivy.base import EventLoop
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView

class PasswordScannerApp(App):
    def build(self):
        root = Accordion(orientation='vertical')

        #Configs
        item = AccordionItem(title='Configs')

        self.configFilePathInput = TextInput(text="Type the path to config.json or drag and drop")
        Window.bind(on_dropfile=self._on_file_drop)
        item.add_widget(self.configFilePathInput)
        self.patterns = TextInput(text="Known Patterns")
        item.add_widget(self.patterns)
        self.types = TextInput(text="File types to scan")
        item.add_widget(self.types)
        self.keywords = TextInput(text="Keywords to search")
        item.add_widget(self.keywords)

        layoutConfig = GridLayout(cols=1)
        loadPatternsButton = Button(text='Load',font_size=20, halign="center")
        loadPatternsButton.bind(on_release=lambda x: self.loadConfigFile(self.configFilePathInput.text))
        layoutConfig.add_widget(loadPatternsButton)
        savePatternsButton = Button(text='Save',font_size=20, halign="center")
        savePatternsButton.bind(on_release=lambda x: self.saveToConfigs())
        layoutConfig.add_widget(savePatternsButton)
        item.add_widget(layoutConfig)
        root.add_widget(item)

        #Choose a folder
        item = AccordionItem(title='Choose a folder to scan')
        layoutFolder = GridLayout(cols=1)
        self.pathInput = TextInput(text="Type the path or drag and drop the folder here")
        Window.bind(on_dropfile=self._on_file_drop)
        layoutFolder.add_widget(self.pathInput)

        filesScroll = ScrollView()
        self.filesLabel = TextInput(text=str("List of files"))
        filesScroll.add_widget(self.filesLabel)
        layoutFolder.add_widget(filesScroll)

        savePathButton = Button(text='Confirm', size_hint=(0.1, 0.1), font_size=20, halign="center")
        savePathButton.bind(on_release=lambda x:self.savePath())
        layoutFolder.add_widget(savePathButton)
        item.add_widget(layoutFolder)
        root.add_widget(item)


        #output
        #todo add output path
        item = AccordionItem(title='Output')
        self.outputText = outputInput(text="Double click on this output text to start")
        item.add_widget(self.outputText)
        root.add_widget(item)
        return root

    def saveToConfigs(self):
        runFlag = True
        if (not os.path.exists(self.configFilePathInput.text) and not os.access(os.path.dirname(self.configFilePathInput.text), os.W_OK)):
            Alert(text="Failed to save to the path provided, update it in the Configs tab.")
            runFlag = False
        else:
            outputTypesList = self.types.text.split("\n")
            for outputType in outputTypesList:
                if (" " in outputType):
                    Alert(text="Cannot have space in file types")
                    runFlag = False

        if runFlag:
            raw = {}
            outputPatternsList = self.patterns.text.split("\n")
            outputTypesList = self.types.text.split("\n")
            outputkeywordsList = self.keywords.text.split("\n")
            try:
                with open(self.configFilePathInput.text, "w") as fp:
                    raw['patterns'] = outputPatternsList
                    raw['types'] = outputTypesList
                    raw['keywords'] = outputkeywordsList
                    json.dump(raw, fp)
                    print("file at " + str(self.configFilePathInput.text) + " created")
            except Exception as e:
                traceback.print_exc()
                print(e)


    def convertTextTo(self, text, flag):
        output = ""
        if (flag == 'text'):
            for item in text:
                output += item
                output += "\n"
        elif (flag == 'config'):
            for item in text:
                output += item
                output += ","
        return output[:-1]

    def _on_file_drop(self, window, file_path):
        ext = file_path[-11:]
        if (ext.decode("utf-8")  == 'config.json'):
            self.loadConfigFile(file_path)
            print("config file " + str(file_path) + " loaded...")
        else:
            self.folderPath = file_path
            self.pathInput.text = file_path
            print("set scan folder to " + str(file_path))

    def savePath(self):
        if os.path.isdir(self.pathInput.text):
            self.folderPath = self.pathInput.text
            if hasattr(self,"typesConfig"):
                curDir = os.getcwd()
                os.chdir(self.folderPath)
                files = addFiles(self.typesConfig)
                files = self.convertTextTo(files,'text')
                self.filesLabel.text = files
                os.chdir(curDir)
        else:
            Alert(text="Invalid folder path.")

    def loadConfigFile(self, file_path):
        if (os.path.exists(file_path)):
            self.configFilePath = file_path
            self.configFilePathInput.text = file_path
            try:
                (self.typesConfig, self.keywordsConfig, self.patternsConfig, self.raw) = loadJson(file_path)
                self.patterns.text = self.convertTextTo(self.patternsConfig, 'text')
                self.types.text = self.convertTextTo(self.typesConfig, 'text')
                self.keywords.text = self.convertTextTo(self.keywordsConfig, 'text')
            except Exception as e:
                Alert(text="Failed to load config file, not in json format.\n"
                           "Please update patterns,keywords,file types in Configs tab.")
        else:
            Alert(text="Failed to load config file, file does not exist.")


class Alert(Popup):
    def __init__(self, text):
        super(Alert, self).__init__()
        content = AnchorLayout(anchor_x='center', anchor_y='bottom')
        content.add_widget(
            Label(text=text, halign='left', valign='top')
        )
        ok_button = Button(text='Close', size_hint=(None, None), size=(Window.width / 5, Window.height / 10))
        content.add_widget(ok_button)
        popup = Popup(
            title="Error",
            content=content,
            size_hint=(None, None),
            size=(Window.width/2, Window.height/2),
            auto_dismiss=True,
        )
        ok_button.bind(on_press=popup.dismiss)
        popup.open()


class outputInput(TextInput):
    def on_touch_down(self, touch):
        super(outputInput, self).on_touch_down(touch)
        if touch.button == 'right':
            #self.popup = PopMenu(touch)
            #self.popup.open()
            print("right mouse clicked")
            t= self.selection_text
            print(t)
            begin = self._selection_from
            end = self._selection_to
            print(begin,end)
            #self._show_cut_copy_paste(pos, EventLoop.window, mode='paste')

    def on_double_tap(self):
        super(outputInput, self).on_double_tap()
        try:
            if hasattr(App.get_running_app(), 'folderPath') and hasattr(App.get_running_app(), 'configFilePath'):
                App.get_running_app().outputText.text = "Starting the scan, please do not close this window."
                folderPath = (App.get_running_app().folderPath)
                if(type(folderPath) != type("string")):
                    folderPath = folderPath.decode("utf-8")
                configFile = (App.get_running_app().configFilePath)
                if (type(configFile) != type("string")):
                    configFile = configFile.decode("utf-8")
                scan = 'python scanner.py -c '+configFile + " -p " +folderPath + " -o output.json"
                #todo workon here
                print(scan)
                result = subprocess.check_output(scan)
                if (type(result) != type("string")):
                    result = result.decode("utf-8")
                print(result)
                App.get_running_app().outputText.text = str(result)
            else:
                Alert(text="Scan cannot be started!\nMake sure you have chosen a config file and folder to scan in other tabs.")
        except Exception as e:
            traceback.print_exc()
            Alert(text=str(e))

class PopMenu(object):
    def __init__(self, touch):
        myContent = BoxLayout(orientation='vertical')
        button = Button(text='copy')
        myContent.add_widget(button)
        button = Button(text='send to known patterns')
        myContent.add_widget(button)

        self.popup = ModalView(size_hint=(None, None), height=myContent.height, pos_hint={'x' : touch.spos[0], 'top' : touch.spos[1]},auto_dismiss=True)
        self.popup.add_widget(myContent)
    def open(self, *args):
        self.popup.open()


if __name__ == '__main__':
    PasswordScannerApp().run()
