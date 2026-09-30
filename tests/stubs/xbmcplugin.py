ITEMS=[];ENDS=[];RESOLVED=[]
def addDirectoryItem(handle=None,url=None,listitem=None,isFolder=False,*a):
    if not isinstance(handle,int): handle,url,listitem,isFolder=(handle,url,listitem,isFolder)
    ITEMS.append((listitem.label,url,isFolder))
def endOfDirectory(h,*a,**k): ENDS.append(h)
def setResolvedUrl(h,ok,item): RESOLVED.append(item.path)
def setContent(*a,**k): pass
def addSortMethod(*a,**k): pass
def setPluginCategory(*a,**k): pass
def addDirectoryItems(h,items,*a):
    for u,li,f in items: ITEMS.append((li.label,u,f))
