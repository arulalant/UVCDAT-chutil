import vcs

x = None

def genTemplate(xscale=0, yscale=1.25, xmove=0, ymove=-0.1):
    """
    This default argument made it for India Map to looks pretty.
    """
    
    global x
    if not (x and isinstance(x, vcs.Canvas.Canvas)):
        # initializing vcs
        x = vcs.init()
        # set portrait not only here.. v.portrait() should call while calling
        # this function or should pass x=v in this function.
        x.portrait()        
        # auto update vcs
        x.mode = 1
        print "one time initializing of vcs obj x"

    if 'genTemplate' in x.listelements('template'):
        # get the 'genTemplate' template object from temporary memory of vcs
        # template
        gentemp = x.gettemplate('genTemplate')
    else:
        # creating 'genTemplate' object
        tt = x.createtexttable('new', 'std')
        tt.font = 1
        tt.priority = 1
        
        tit = x.createtexttable('title', 'std')
        tit.font = 2
        tit.priority = 1

        tio = x.createtextorientation('title', 'centerup')
        tio.height = 15
        tio.angle = 0
        
        tco = x.createtextorientation('comment1', 'centerup')
        tco.height = 10
        tco.angle = 0
        
        to = x.createtextorientation('new', 'centerup')
        to.height = 10
        to.angle = 0
        
        tol = x.createtextorientation('newleft', '7right')
        tol.height = 10
        tol.angle = 0        
        
        # create copy of ASD template
        gentemp = x.createtemplate()#'genTemplate', 'ASD')

        gentemp.title.priority = 1
        gentemp.title.x = 0.50
        gentemp.title.y = 0.9
        gentemp.title.texttable = tit
        gentemp.title.textorientation = tio
        
        gentemp.comment1.priority = 1
        gentemp.comment1.x = 0.50
        gentemp.comment1.y = 0.88
        gentemp.comment1.texttable = tit
        gentemp.comment1.textorientation = tco
        
        gentemp.min.priority = 0    # off min value
        gentemp.mean.priority = 0   # off mean value
        gentemp.max.priority = 0    # off max value
        gentemp.dataname.priority = 0  # off the variable id

#        gentemp.legend_type = 'VCS'
        gentemp.legend.priority = 1
        
        gentemp.legend.x1 = 0.1
        gentemp.legend.y1 = 0.18
        gentemp.legend.x2 = 0.9
        gentemp.legend.y2 = 0.195
        
        gentemp.legend.texttable = tt
        gentemp.legend.textorientation = to

        gentemp.xtic2.priority = 0 
        gentemp.ytic2.priority = 0
        gentemp.xlabel2.priority = 0 
        gentemp.ylabel2.priority = 0
        
        gentemp.xlabel1.texttable = tt
        gentemp.xlabel1.textorientation = to
        gentemp.ylabel1.texttable = tt
        gentemp.ylabel1.textorientation = tol        

        gentemp.xname.priority = 0  # off the longitude string in x axis
        gentemp.yname.priority = 0  # off the latitude string in y axis
        gentemp.units.priority = 0  # off the units value

        if xscale:
            gentemp.scale(xscale, axis = 'x')
        if yscale:
            gentemp.scale(yscale, axis = 'y')
        if xmove:
            gentemp.move(xmove, 'x')
        if ymove:
            gentemp.move(ymove, 'y')
#        gentemp.scalefont(2.4)
#        gentemp.moveto(.1,.25)

        # saving the 'genTemplate' into temporary python memory
#        x.set('template', 'genTemplate')

    # return the genTemplate object
    return gentemp
# end of def genTemplate():
