#   Programmer: limodou
#   E-mail:     limodou@gmail.com
#
#   Copyleft 2006 limodou
#
#   Distributed under the terms of the GPL (GNU Public License)
#
#   UliPad is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   $Id: mEditorCtrl.py 1624 2006-10-19 02:27:11Z limodou $

import wx
import os.path
from modules.wxctrl import FlatNotebook as FNB
from modules import common
from modules import Globals
from modules import Mixin

def add_mainframe_menu(menulist):
    menulist.extend([ ('IDM_FILE',
        [
            (100, 'IDM_FILE_NEW', tr('New') + '\tCtrl+N', wx.ITEM_NORMAL, 'OnFileNew', tr('Creates a new document')),
            (105, 'IDM_FILE_NEWMORE', tr('New') + '...', wx.ITEM_NORMAL, None, tr('Creates a new document')),
            (110, 'IDM_FILE_OPEN', tr('Open') + '\tCtrl+O', wx.ITEM_NORMAL, 'OnFileOpen', tr('Opens an existing document')),
            (120, 'IDM_FILE_REOPEN', tr('Reopen') + '\tE=Ctrl+Shift+O', wx.ITEM_NORMAL, 'OnFileReOpen', tr('Reopens an existing document')),
            (140, 'IDM_FILE_CLOSE', tr('Close') + '\tCtrl+F4', wx.ITEM_NORMAL, 'OnFileClose', tr('Closes an opened document')),
            (150, 'IDM_FILE_CLOSE_ALL', tr('Close All'), wx.ITEM_NORMAL, 'OnFileCloseAll', tr('Closes all document windows')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDM_FILE_SAVE', tr('Save') + '\tE=Ctrl+S', wx.ITEM_NORMAL, 'OnFileSave', tr('Saves an opened document using the same filename')),
            (180, 'IDM_FILE_SAVEAS', tr('Save As'), wx.ITEM_NORMAL, 'OnFileSaveAs', tr('Saves an opened document to a specified filename')),
            (190, 'IDM_FILE_SAVE_ALL', tr('Save All'), wx.ITEM_NORMAL, 'OnFileSaveAll', tr('Saves all documents')),
        ]),
    ])
Mixin.setPlugin('mainframe', 'add_menu', add_mainframe_menu)

def add_editctrl_menu(popmenulist):
    popmenulist.extend([ (None,
        [
            (100, 'IDPM_CLOSE', tr('Close') + '\tCtrl+F4', wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Closes an opened document')),
            (110, 'IDPM_CLOSE_ALL', tr('Close All'), wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Closes all document windows')),
            (120, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (130, 'IDPM_SAVE', tr('Save') + '\tCtrl+S', wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Saves an opened document using the same filename')),
            (140, 'IDPM_SAVEAS', tr('Save As'), wx.ITEM_NORMAL, 'OnPopUpMenu', 'tr(Saves an opened document to a specified filename)'),
            (150, 'IDPM_FILE_SAVE_ALL', tr('Save All'), wx.ITEM_NORMAL, 'OnPopUpMenu', tr('Saves all documents')),
            (160, '', '-', wx.ITEM_SEPARATOR, None, ''),
            (170, 'IDPM_OPEN_CMD_WINDOW', tr('Open Command Window Here'), wx.ITEM_NORMAL, 'OnOpenCmdWindow', ''),
        ]),
    ])
Mixin.setPlugin('editctrl', 'add_menu', add_editctrl_menu)

def add_mainframe_menu_image_list(imagelist):
    imagelist.update({
        'IDM_FILE_NEW':'images/new.gif',
        'IDM_FILE_OPEN':'images/open.gif',
        'IDM_FILE_CLOSE':'images/close.gif',
        'IDM_FILE_SAVE':'images/save.gif',
        'IDM_FILE_SAVEALL':'images/saveall.gif',
    })
Mixin.setPlugin('mainframe', 'add_menu_image_list', add_mainframe_menu_image_list)

def add_editctrl_menu_image_list(imagelist):
    imagelist = {
        'IDPM_CLOSE':'images/close.gif',
        'IDPM_SAVE':'images/save.gif',
        'IDPM_FILE_SAVEALL':'images/saveall.gif',
    }
Mixin.setPlugin('editctrl', 'add_menu_image_list', add_editctrl_menu_image_list)

def neweditctrl(win):
    from EditorFactory import EditorFactory

    win.notebook = EditorFactory(win.top, win.mainframe)
Mixin.setPlugin('mainsubframe', 'init', neweditctrl)

def on_close(win, event):
    if event.CanVeto():
        for document in win.editctrl.getDocuments():
            r = win.CloseFile(document, True)
            if r == wx.ID_CANCEL:
                return True
        if win.execplugin('closewindow', win) == wx.ID_CANCEL:
            return True
Mixin.setPlugin('mainframe', 'on_close', on_close)

def OnFileNew(win, event):
    win.editctrl.new()
Mixin.setMixin('mainframe', 'OnFileNew', OnFileNew)

def OnFileOpen(win, event):
    dlg = wx.FileDialog(win, tr("Open"), win.pref.last_dir, "", '|'.join(win.filewildchar), wx.OPEN|wx.HIDE_READONLY|wx.MULTIPLE)
    dlg.SetFilterIndex(getFilterIndex(win))
    if dlg.ShowModal() == wx.ID_OK:
        encoding = win.execplugin('getencoding', win, win)
        for filename in dlg.GetPaths():
            win.editctrl.new(filename, encoding)
        dlg.Destroy()
Mixin.setMixin('mainframe', 'OnFileOpen', OnFileOpen)

def getFilterIndex(win):
    if hasattr(win, 'document') and win.document:
        doc = win.document
        if doc.languagename:
            w = None
            for wildchar, lang in win.filenewtypes:
                if lang == doc.languagename:
                    w = wildchar
                    break
            if w:
                for i, v in enumerate(win.filewildchar):
                    s = v.split('|')[0]
                    if s.startswith(w):
                        return i
                
    if len(win.pref.recent_files) > 0:
        filename = win.pref.recent_files[0]
        ext = os.path.splitext(filename)[1]
        for i, v in enumerate(win.filewildchar):
            s = v.split('|')[1]
            for wildchar in s.split(';'):
                if wildchar.endswith(ext):
                    return i
            else:
                continue
    return 0
Mixin.setMixin('mainframe', 'getFilterIndex', getFilterIndex)

def OnFileReOpen(win, event):
    if win.document.isModified():
        document = findDocument(win.document)
        dlg = wx.MessageDialog(win, tr("This document has been modified,\ndo you really want to reload the file?"), tr("Reopen file..."), wx.YES_NO|wx.ICON_QUESTION)
        answer = dlg.ShowModal()
        dlg.Destroy()
        if answer != wx.ID_YES:
            return
        state = document.save_state()
        document.openfile(document.filename)
        document.editctrl.switch(document)
        document.restore_state(state)
Mixin.setMixin('mainframe', 'OnFileReOpen', OnFileReOpen)

def OnFileClose(win, event):
    document = findDocument(win.document)
    win.CloseFile(document)
    if len(win.editctrl.getDocuments()) == 0:
        win.editctrl.new()
Mixin.setMixin('mainframe', 'OnFileClose', OnFileClose)

def OnFileCloseAll(win, event):
    i = len(win.editctrl.getDocuments()) - 1
    while i > -1:
        document = win.editctrl.getDoc(i)
        if not document.opened:
            win.editctrl.skip_closing = True
            win.editctrl.skip_page_change = True
            win.editctrl.DeletePage(i)
        i -= 1

    k = len(win.editctrl.getDocuments())
    for i in range(k):
        document = win.editctrl.getDoc(0)
        r = win.CloseFile(document)
        if r == wx.ID_CANCEL:
            break
    if win.editctrl.GetPageCount() == 0:
        win.editctrl.new()
Mixin.setMixin('mainframe', 'OnFileCloseAll', OnFileCloseAll)

def CloseFile(win, document, checkonly = False):
    answer = wx.ID_YES
    if document.isModified():
        d = wx.MessageDialog(win, tr("Would you like to save %s ?") % document.getFilename(),
            tr("Close File"), wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
        answer = d.ShowModal()
        d.Destroy()
        if answer == wx.ID_YES:
            win.SaveFile(document)
        elif answer == wx.ID_CANCEL:
            return answer

    if checkonly == False:
        win.editctrl.lastdocument = None
        win.callplugin('closefile', win, document, document.filename)
        win.editctrl.closefile(document)
    return answer
Mixin.setMixin('mainframe', 'CloseFile', CloseFile)

def OnFileSave(win, event):
    document = findDocument(win.document)
    win.SaveFile(document)
    document.SetFocus()
Mixin.setMixin('mainframe', 'OnFileSave', OnFileSave)

def OnFileSaveAll(win, event):
    for ctrl in win.editctrl.getDocuments():
        if ctrl.opened:
            r = win.SaveFile(ctrl)
Mixin.setMixin('mainframe', 'OnFileSaveAll', OnFileSaveAll)

def OnFileSaveAs(win, event):
    win.SaveFile(win.document, True)
Mixin.setMixin('mainframe', 'OnFileSaveAs', OnFileSaveAs)

def SaveFile(win, ctrl, issaveas=False):
    encoding = None
    if not ctrl.cansavefile():
        return True

    if issaveas or len(ctrl.filename)<=0:
        encoding = win.execplugin('getencoding', win, win)
        dlg = wx.FileDialog(win, tr("Save File %s As") % ctrl.getFilename(), win.pref.last_dir, '', '|'.join(win.filewildchar), wx.SAVE|wx.OVERWRITE_PROMPT)
        dlg.SetFilterIndex(getFilterIndex(win))
        if (dlg.ShowModal() == wx.ID_OK):
            filename = dlg.GetPath()
            dlg.Destroy()

            #check if the filename has been openned, if openned then fail
            for document in win.editctrl.getDocuments():
                if (not ctrl is document ) and (filename == document.filename):
                    wx.MessageDialog(win, tr("Ths file %s has been openned!\nCann't save new file to it.") % document.getFilename(),
                        tr("Save As..."), wx.OK|wx.ICON_INFORMATION).ShowModal()
                    return False
        else:
            return False
    else:
        filename = ctrl.filename

    return win.editctrl.savefile(ctrl, filename, encoding)
Mixin.setMixin('mainframe', 'SaveFile', SaveFile)

def pref_init(pref):
    pref.last_dir = ''
    pref.notebook_direction = 0
Mixin.setPlugin('preference', 'init', pref_init)

def add_pref(preflist):
    preflist.extend([
        (tr('Document'), 290, 'choice', 'notebook_direction', tr('Document tabs direction'), [tr('Top'), tr('Bottom')])
    ])
Mixin.setPlugin('preference', 'add_pref', add_pref)

def savepreference(mainframe, pref):
    style = mainframe.editctrl.GetWindowStyleFlag()
    if pref.notebook_direction:
        style |= FNB.FNB_BOTTOM
    else:
        if style & FNB.FNB_BOTTOM:
            style ^= FNB.FNB_BOTTOM
    
    mainframe.editctrl.SetWindowStyleFlag(style)
    mainframe.editctrl.Refresh()
Mixin.setPlugin('prefdialog', 'savepreference', savepreference)

def findDocument(document):
    if hasattr(document, 'multiview') and document.multiview:
        return document.document
    else:
        return document
    
def OnOpenCmdWindow(win, event=None):
    filename = win.getCurDoc().getFilename()
    if not filename:
        filename = Globals.userpath
    else:
        filename = os.path.dirname(filename)
    if wx.Platform == '__WXMSW__':
        cmdline = os.environ['ComSpec']
        os.spawnl(os.P_NOWAIT, cmdline, r"cmd.exe /k cd %s" % filename)
    else:
        common.showerror(win, tr('This features is only implemented in Windows Platform.\nIf you know how to implement in Linux please tell me.'))
Mixin.setMixin('editctrl', 'OnOpenCmdWindow', OnOpenCmdWindow)